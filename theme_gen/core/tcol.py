"""TCol -- immutable OKLCH color wrapper for theme generation.

Wraps coloraide.Color in OKLCH space. All operations return new TCol
instances. Hex output uses perceptual gamut mapping to sRGB.
"""

import functools
import math
from dataclasses import dataclass
from typing import Self, override

from coloraide import Color
from scipy.optimize import brentq

_OKLCH = "oklch"
_SRGB = "srgb"
_CH_L = "lightness"
_CH_C = "chroma"
_CH_H = "hue"
_CH_R = "red"
_CH_G = "green"
_CH_B = "blue"
_HEX_ALPHA_LEN = 8
_LAB_D65 = "lab-d65"
MIDPOINT_LIGHTNESS = 0.5


def _to_oklch(c: Color) -> Color:
    return c.convert(_OKLCH) if c.space() != _OKLCH else c.clone()


def _build_hex(srgb: Color) -> str:
    """Uppercase hex from a gamut-fitted sRGB Color."""
    r = round(srgb.get(_CH_R) * 255)
    g = round(srgb.get(_CH_G) * 255)
    b = round(srgb.get(_CH_B) * 255)
    a = srgb.alpha()
    if a < 1.0:
        return f"#{r:02X}{g:02X}{b:02X}{round(a * 255):02X}"
    return f"#{r:02X}{g:02X}{b:02X}"


@functools.total_ordering
@dataclass(frozen=True, init=False, eq=False, repr=False)
class TCol:
    """Immutable theme color stored in OKLCH, converted to sRGB on output.

    Eagerly caches hex string and OKLCH components so repeated access is free. Defensively copies the underlying coloraide.Color on construction.
    """

    _color: Color
    _srgb: Color
    _hex: str
    _l: float
    _c: float
    _h: float
    _a: float

    def __init__(self, value: Color | str) -> None:
        if isinstance(value, str):
            s = value.strip().lstrip("#")
            if len(s) == _HEX_ALPHA_LEN:
                rgb_part, alpha_hex = s[:6], s[6:8]
                c = Color(f"#{rgb_part}")
                c[-1] = int(alpha_hex, 16) / 255
            else:
                c = Color(f"#{s}")
            oklch = _to_oklch(c)
        else:
            oklch = _to_oklch(value)

        srgb = oklch.convert(_SRGB).fit(_SRGB)
        hue = oklch.get(_CH_H)

        object.__setattr__(self, "_color", oklch)
        object.__setattr__(self, "_srgb", srgb)
        object.__setattr__(self, "_hex", _build_hex(srgb))
        object.__setattr__(self, "_l", oklch.get(_CH_L))
        object.__setattr__(self, "_c", oklch.get(_CH_C))
        object.__setattr__(self, "_h", 0.0 if math.isnan(hue) else hue)
        object.__setattr__(self, "_a", oklch.alpha())

    @classmethod
    def from_hex(cls, hex_str: str) -> Self:
        """Create from #RGB, #RRGGBB, or #RRGGBBAA."""
        return cls(hex_str)

    @classmethod
    def from_oklch(cls, lightness: float, chroma: float, hue: float) -> Self:
        """Create from OKLCH components.

        Hue normalized to 0-360.
        """
        return cls(Color(_OKLCH, [lightness, chroma, hue % 360]))

    @property
    def hex(self) -> str:
        """#RRGGBB or #RRGGBBAA via perceptual gamut mapping."""
        return self._hex

    @property
    def lightness(self) -> float:
        """OKLCH lightness (0.0-1.0)."""
        return self._l

    @property
    def c(self) -> float:
        """OKLCH chroma (0.0+)."""
        return self._c

    @property
    def h(self) -> float:
        """OKLCH hue (0-360).

        0.0 for achromatic colors.
        """
        return self._h

    @property
    def a(self) -> float:
        """Alpha (0.0-1.0)."""
        return self._a

    @property
    def color(self) -> Color:
        """Underlying OKLCH coloraide.Color (read-only clone)."""
        return self._color.clone()

    def with_alpha(self, alpha: float) -> Self:
        """New TCol with given alpha (0.0-1.0)."""
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be 0.0-1.0, got {alpha}")
        c = self.color
        c[-1] = alpha
        return type(self)(c)

    @property
    def a05(self) -> Self:
        """This color at 5% opacity."""
        return self.with_alpha(0.05)

    @property
    def a15(self) -> Self:
        """This color at 15% opacity."""
        return self.with_alpha(0.15)

    @property
    def a25(self) -> Self:
        """This color at 25% opacity."""
        return self.with_alpha(0.25)

    @property
    def a50(self) -> Self:
        """This color at 50% opacity."""
        return self.with_alpha(0.50)

    @property
    def a80(self) -> Self:
        """This color at 80% opacity."""
        return self.with_alpha(0.80)

    # ── Lightness steps ──

    @property
    def lighter(self) -> Self:
        """Lightness +0.15 (one step lighter)."""
        return self.lighten(0.15)

    @property
    def darker(self) -> Self:
        """Lightness -0.15 (one step darker)."""
        return self.darken(0.15)

    @property
    def much_lighter(self) -> Self:
        """Lightness +0.35 (two steps lighter)."""
        return self.lighten(0.35)

    @property
    def much_darker(self) -> Self:
        """Lightness -0.35 (two steps darker)."""
        return self.darken(0.35)

    # ── Chroma steps ──

    @property
    def muted(self) -> Self:
        """Chroma set to 0.04 (barely tinted)."""
        return self.set_chroma(0.04)

    @property
    def soft(self) -> Self:
        """Chroma set to 0.07 (gentle color)."""
        return self.set_chroma(0.07)

    @property
    def vivid(self) -> Self:
        """Chroma set to 0.15 (full saturation)."""
        return self.set_chroma(0.15)

    # ── Lightness ramp (perceptually even chroma) ──
    #
    # Chroma is scaled per step to match perceptual evenness.
    # Values from APCA-based color generator with "Even chroma" mode.
    # The curve peaks at s500 and tapers at both light and dark ends.
    # Each entry is (lightness, chroma_scale) where chroma_scale is
    # relative to the base color's chroma.

    def _at_step(self, target_l: float, chroma_scale: float) -> Self:
        """New TCol at target lightness with scaled chroma, preserving hue and alpha."""
        c = self.color
        _ = c.set(_CH_L, target_l)
        _ = c.set(_CH_C, self._c * chroma_scale)
        return type(self)(c)

    @property
    def s100(self) -> Self:
        """L=0.95, chroma x0.10 (barely tinted)."""
        return self._at_step(0.95, 0.10)

    @property
    def s200(self) -> Self:
        """L=0.88, chroma x0.27."""
        return self._at_step(0.88, 0.27)

    @property
    def s300(self) -> Self:
        """L=0.80, chroma x0.48."""
        return self._at_step(0.80, 0.48)

    @property
    def s400(self) -> Self:
        """L=0.72, chroma x0.71."""
        return self._at_step(0.72, 0.71)

    @property
    def s500(self) -> Self:
        """L=0.64, chroma x1.00 (peak)."""
        return self._at_step(0.64, 1.00)

    @property
    def s600(self) -> Self:
        """L=0.56, chroma x0.89."""
        return self._at_step(0.56, 0.89)

    @property
    def s700(self) -> Self:
        """L=0.48, chroma x0.75."""
        return self._at_step(0.48, 0.75)

    @property
    def s800(self) -> Self:
        """L=0.38, chroma x0.60."""
        return self._at_step(0.38, 0.60)

    @property
    def s900(self) -> Self:
        """L=0.28, chroma x0.43 (darkest)."""
        return self._at_step(0.28, 0.43)

    def lighten(self, amount: float) -> Self:
        """Increase OKLCH lightness by amount.

        Clamped to 0.0-1.0.
        """
        c = self.color
        _ = c.set(_CH_L, min(1.0, c.get(_CH_L) + abs(amount)))
        return type(self)(c)

    def darken(self, amount: float) -> Self:
        """Decrease OKLCH lightness by amount.

        Clamped to 0.0-1.0.
        """
        c = self.color
        _ = c.set(_CH_L, max(0.0, c.get(_CH_L) - abs(amount)))
        return type(self)(c)

    def shift_hue(self, degrees: float) -> Self:
        """Rotate hue by degrees.

        Returns self unchanged when shift is a full rotation.
        """
        if math.isclose(degrees % 360, 0.0):
            return self
        c = self.color
        _ = c.set(_CH_H, (self._h + degrees) % 360)
        return type(self)(c)

    def set_chroma(self, chroma: float) -> Self:
        """New TCol with absolute chroma value."""
        if chroma < 0.0:
            raise ValueError(f"chroma must be >= 0.0, got {chroma}")
        c = self.color
        _ = c.set(_CH_C, chroma)
        return type(self)(c)

    def contrast(self, other: TCol) -> float:
        """WCAG 2.1 contrast ratio (1.0 to 21.0)."""
        return self._color.contrast(other.color)

    def mix(self, other: TCol, amount: float = 0.5) -> Self:
        """Blend self with other in sRGB space.

        amount=0 returns self, amount=1 returns other.
        """
        mixed = self._color.mix(other.color, amount, space=_SRGB)
        return type(self)(mixed)

    @classmethod
    def from_lab_l(cls, target_lab_l: float, chroma: float, hue: float) -> Self:
        """Create a TCol at the OkLCh L that achieves target CIELab L*.

        Uses scipy.optimize.brentq (Brent's method) to find the OkLCh L that maps to the given CIELab L* at the specified hue and chroma.

        This compensates for the hue-dependent mapping between OkLCh L and Lab L*: purple (310°) has a lower Lab L* than blue (265°) at the same OkLCh L, making it appear darker. Targeting Lab L* directly ensures colors at the same tier have the same
        perceptual weight regardless of hue.
        """

        def residual(ok_l: float) -> float:
            return Color(_OKLCH, [ok_l, chroma, hue]).convert(_LAB_D65).get(_CH_L) - target_lab_l

        ok_l = brentq(residual, 0.0, 1.0)
        return cls.from_oklch(ok_l, chroma, hue)

    def with_min_contrast(self, bg: TCol, min_ratio: float) -> Self:
        """Return self adjusted until contrast against bg meets min_ratio.

        On a light background (L >= 0.5), darkens the color (searches L downward). On a dark background (L < 0.5), lightens the color (searches L upward). Uses scipy.optimize.brentq to find the exact OkLCh L where contrast equals min_ratio, preserving hue
        and chroma precisely. Returns self unchanged if it already passes or min_ratio <= 0.
        """
        if min_ratio <= 0.0 or self.contrast(bg) >= min_ratio:
            return self

        h, c = self._h, self._c

        def residual(ok_l: float) -> float:
            return type(self).from_oklch(ok_l, c, h).contrast(bg) - min_ratio

        if bg.lightness >= MIDPOINT_LIGHTNESS:
            # Light bg: darken text (search downward from current L to 0)
            return type(self).from_oklch(brentq(residual, 0.0, self._l), c, h)
        # Dark bg: lighten text (search upward from current L to 1)
        return type(self).from_oklch(brentq(residual, self._l, 1.0), c, h)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TCol):
            return NotImplemented
        return self._hex == other._hex

    @override
    def __hash__(self) -> int:
        return hash(self._hex)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, TCol):
            return NotImplemented
        return (self._l, self._c, self._h, self._a) < (
            other._l,
            other._c,
            other._h,
            other._a,
        )

    @override
    def __repr__(self) -> str:
        return f"TCol({self._hex!r})"

    @override
    def __str__(self) -> str:
        return self._hex
