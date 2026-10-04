"""Tests for TCol and FontStyle."""

import pytest
from coloraide import Color

from theme_gen.core.font_style import FontStyle
from theme_gen.core.tcol import TCol


class TestTColHexRoundTrip:
    def test_opaque_hex_round_trip(self) -> None:
        t = TCol.from_hex("#FF0000")
        assert t.hex == "#FF0000"

    def test_alpha_hex_round_trip(self) -> None:
        t = TCol.from_hex("#FF000080")
        assert t.hex == "#FF000080"

    def test_white(self) -> None:
        assert TCol.from_hex("#FFFFFF").hex == "#FFFFFF"

    def test_black(self) -> None:
        assert TCol.from_hex("#000000").hex == "#000000"

    def test_lowercase_input(self) -> None:
        t = TCol.from_hex("#aabbcc")
        assert t.hex == "#AABBCC"


_HEX_8_LEN = 9
_HEX_6_LEN = 7
_ALPHA_TOLERANCE = 0.01
_BLACK_WHITE_CONTRAST_MIN = 15.0
_WCAG_AA = 4.5


class TestTColAlpha:
    def test_with_alpha_produces_8_digit_hex(self) -> None:
        t = TCol.from_hex("#FF0000").with_alpha(0.5)
        assert len(t.hex) == _HEX_8_LEN
        assert t.hex.endswith("80")

    def test_with_alpha_1_produces_6_digit_hex(self) -> None:
        t = TCol.from_hex("#FF000080").with_alpha(1.0)
        assert len(t.hex) == _HEX_6_LEN

    def test_alpha_property(self) -> None:
        t = TCol.from_hex("#FF000080")
        assert abs(t.a - 0.502) < _ALPHA_TOLERANCE

    def test_invalid_alpha_raises(self) -> None:
        t = TCol.from_hex("#FF0000")
        with pytest.raises(ValueError, match="alpha must be"):
            _ = t.with_alpha(1.5)


class TestTColContrast:
    def test_black_white_contrast(self) -> None:
        black = TCol.from_hex("#000000")
        white = TCol.from_hex("#FFFFFF")
        ratio = black.contrast(white)
        assert ratio > _BLACK_WHITE_CONTRAST_MIN

    def test_same_color_contrast(self) -> None:
        c = TCol.from_hex("#808080")
        assert c.contrast(c) == pytest.approx(1.0, abs=0.1)


class TestTColLightenDarken:
    def test_lighten_increases_lightness(self) -> None:
        t = TCol.from_hex("#808080")
        lighter = t.lighten(0.1)
        assert lighter.lightness > t.lightness

    def test_darken_decreases_lightness(self) -> None:
        t = TCol.from_hex("#808080")
        darker = t.darken(0.1)
        assert darker.lightness < t.lightness

    def test_lighten_clamps_at_1(self) -> None:
        t = TCol.from_hex("#FFFFFF")
        lighter = t.lighten(0.5)
        assert lighter.lightness <= 1.0

    def test_darken_clamps_at_0(self) -> None:
        t = TCol.from_hex("#000000")
        darker = t.darken(0.5)
        assert darker.lightness >= 0.0


class TestTColShiftHue:
    def test_shift_hue_changes_hue(self) -> None:
        t = TCol.from_hex("#FF0000")
        shifted = t.shift_hue(120)
        assert abs(shifted.h - ((t.h + 120) % 360)) < 1.0

    def test_shift_hue_wraps(self) -> None:
        t = TCol.from_oklch(0.5, 0.1, 350.0)
        shifted = t.shift_hue(30)
        assert abs(shifted.h - 20.0) < 1.0


class TestTColSetChroma:
    def test_set_chroma(self) -> None:
        t = TCol.from_hex("#FF0000")
        muted = t.set_chroma(0.05)
        assert abs(muted.c - 0.05) < _ALPHA_TOLERANCE

    def test_set_chroma_zero_is_achromatic(self) -> None:
        t = TCol.from_hex("#FF0000")
        gray = t.set_chroma(0.0)
        assert gray.c == pytest.approx(0.0, abs=0.001)

    def test_negative_chroma_raises(self) -> None:
        t = TCol.from_hex("#FF0000")
        with pytest.raises(ValueError, match="chroma must be"):
            _ = t.set_chroma(-0.1)


class TestTColDefensiveCopy:
    def test_external_color_mutation_does_not_affect_tcol(self) -> None:
        c = Color("oklch", [0.5, 0.1, 262])
        t = TCol(c)
        original_hex = t.hex
        # Mutate the external Color
        _ = c.set("lightness", 0.9)
        assert t.hex == original_hex

    def test_from_oklch_is_independent(self) -> None:
        t1 = TCol.from_oklch(0.5, 0.1, 262)
        t2 = t1.lighten(0.2)
        assert t1.hex != t2.hex
        assert t1.lightness < t2.lightness


class TestTColEquality:
    def test_same_hex_equal(self) -> None:
        assert TCol.from_hex("#FF0000") == TCol.from_hex("#FF0000")

    def test_different_hex_not_equal(self) -> None:
        assert TCol.from_hex("#FF0000") != TCol.from_hex("#00FF00")

    def test_hashable(self) -> None:
        s = {TCol.from_hex("#FF0000"), TCol.from_hex("#FF0000")}
        assert len(s) == 1


class TestFontStyle:
    def test_values(self) -> None:
        assert FontStyle.ITALIC.value == "italic"
        assert FontStyle.BOLD.value == "bold"
        assert FontStyle.NONE.value == ""

    def test_is_str(self) -> None:
        assert isinstance(FontStyle.ITALIC, str)
