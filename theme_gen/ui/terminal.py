"""TerminalSection -- ANSI colors, cursor, selection, find, sticky scroll, command decorations.

ANSI color generation strategy for a light theme:
  6 chromatic hues at standard ANSI positions in OKLCH space.
  Normal: CIELab L*=45, chroma=0.15, WCAG AA floor (4.5:1 on white).
  Bright: CIELab L*=55, chroma=0.18, 3.0:1 floor (lighter for bold text).
  Black/white: achromatic at fixed OKLCH lightness levels.
"""

from dataclasses import dataclass
from typing import override

from core.tcol import TCol
from palette.theme import Theme
from ui.protocol import UISection

# Standard ANSI hue angles (OKLCH)
_HUE_RED = 25.0
_HUE_GREEN = 145.0
_HUE_YELLOW = 85.0
_HUE_BLUE = 260.0
_HUE_MAGENTA = 320.0
_HUE_CYAN = 195.0

# Normal: dark enough for white bg, WCAG AA
_NORMAL_LAB_L = 45.0
_NORMAL_CHROMA = 0.15
_NORMAL_FLOOR = 4.5

# Bright: lighter and more saturated than normal for bold/bright text.
# Contrast floor kept at AA (4.5:1) so bright variants remain readable for
# everyday terminal output; the higher chroma (0.18 vs 0.15) + higher Lab L
# (55 vs 45) preserve the "brighter" feel even when the floor forces the
# final output slightly darker than the raw OkLCh target.
_BRIGHT_LAB_L = 55.0
_BRIGHT_CHROMA = 0.18
_BRIGHT_FLOOR = 4.6


@dataclass(frozen=True)
class AnsiColors:
    """16 ANSI terminal colors generated from standard hues."""

    black: TCol
    red: TCol
    green: TCol
    yellow: TCol
    blue: TCol
    magenta: TCol
    cyan: TCol
    white: TCol
    bright_black: TCol
    bright_red: TCol
    bright_green: TCol
    bright_yellow: TCol
    bright_blue: TCol
    bright_magenta: TCol
    bright_cyan: TCol
    bright_white: TCol

    @classmethod
    def for_light(cls, background: TCol) -> "AnsiColors":
        """Generate 16 ANSI colors for a light terminal background."""

        def _normal(hue: float) -> TCol:
            return TCol.from_lab_l(_NORMAL_LAB_L, _NORMAL_CHROMA, hue).with_min_contrast(background, _NORMAL_FLOOR)

        def _bright(hue: float) -> TCol:
            return TCol.from_lab_l(_BRIGHT_LAB_L, _BRIGHT_CHROMA, hue).with_min_contrast(background, _BRIGHT_FLOOR)

        return cls(
            black=TCol.from_oklch(0.25, 0.0, 0.0),
            red=_normal(_HUE_RED),
            green=_normal(_HUE_GREEN),
            yellow=_normal(_HUE_YELLOW),
            blue=_normal(_HUE_BLUE),
            magenta=_normal(_HUE_MAGENTA),
            cyan=_normal(_HUE_CYAN),
            # ANSI white/brightWhite: intentionally low contrast on light bg.
            # Known tradeoff: ~1.83:1 (white) and ~1.14:1 (brightWhite) fail
            # text contrast, but ANSI slot 7/15 is NOT a body-text role. CLI
            # tools use it for borders, separators, dim table elements, and
            # low-emphasis decorations. Inverting to dark gray (as some reviews
            # suggest) breaks tools that rely on ANSI white being "the lighter
            # neutral." Revisit only if real terminal workloads show unreadable
            # output -- not from static contrast audits.
            white=TCol.from_oklch(0.80, 0.0, 0.0),
            bright_black=TCol.from_oklch(0.45, 0.0, 0.0),
            bright_red=_bright(_HUE_RED),
            bright_green=_bright(_HUE_GREEN),
            bright_yellow=_bright(_HUE_YELLOW),
            bright_blue=_bright(_HUE_BLUE),
            bright_magenta=_bright(_HUE_MAGENTA),
            bright_cyan=_bright(_HUE_CYAN),
            bright_white=TCol.from_oklch(0.95, 0.0, 0.0),
        )

    @classmethod
    def for_dark(cls, background: TCol) -> "AnsiColors":
        """Generate 16 ANSI colors for a dark terminal background."""
        dark_normal_lab_l = 60.0
        dark_normal_chroma = 0.13
        dark_bright_lab_l = 68.0
        dark_bright_chroma = 0.15

        def _normal(hue: float) -> TCol:
            return TCol.from_lab_l(dark_normal_lab_l, dark_normal_chroma, hue).with_min_contrast(
                background, _NORMAL_FLOOR
            )

        def _bright(hue: float) -> TCol:
            return TCol.from_lab_l(dark_bright_lab_l, dark_bright_chroma, hue).with_min_contrast(
                background, _BRIGHT_FLOOR
            )

        return cls(
            # ANSI black on dark: must sit ABOVE the terminal background in
            # lightness so CLI tools using it for dim/muted content (git log
            # graphs, tree connectors, separators) remain visible. L=0.30 gives
            # ~1.5:1 against the L=0.22 terminal bg -- subtle but perceptible,
            # matching the "dim structural element" semantic of ANSI slot 0.
            black=TCol.from_oklch(0.30, 0.0, 0.0),
            red=_normal(_HUE_RED),
            green=_normal(_HUE_GREEN),
            yellow=_normal(_HUE_YELLOW),
            blue=_normal(_HUE_BLUE),
            magenta=_normal(_HUE_MAGENTA),
            cyan=_normal(_HUE_CYAN),
            white=TCol.from_oklch(0.75, 0.0, 0.0),
            bright_black=TCol.from_oklch(0.45, 0.0, 0.0),
            bright_red=_bright(_HUE_RED),
            bright_green=_bright(_HUE_GREEN),
            bright_yellow=_bright(_HUE_YELLOW),
            bright_blue=_bright(_HUE_BLUE),
            bright_magenta=_bright(_HUE_MAGENTA),
            bright_cyan=_bright(_HUE_CYAN),
            bright_white=TCol.from_oklch(0.90, 0.0, 0.0),
        )


class TerminalSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        sel = theme.editor.selection
        ansi = AnsiColors.for_dark(p.background) if theme.is_dark else AnsiColors.for_light(p.background)

        return {
            # Terminal foreground
            "terminal.foreground": p.foreground,
            # ANSI normal
            "terminal.ansiBlack": ansi.black,
            "terminal.ansiRed": ansi.red,
            "terminal.ansiGreen": ansi.green,
            "terminal.ansiYellow": ansi.yellow,
            "terminal.ansiBlue": ansi.blue,
            "terminal.ansiMagenta": ansi.magenta,
            "terminal.ansiCyan": ansi.cyan,
            "terminal.ansiWhite": ansi.white,
            # ANSI bright
            "terminal.ansiBrightBlack": ansi.bright_black,
            "terminal.ansiBrightRed": ansi.bright_red,
            "terminal.ansiBrightGreen": ansi.bright_green,
            "terminal.ansiBrightYellow": ansi.bright_yellow,
            "terminal.ansiBrightBlue": ansi.bright_blue,
            "terminal.ansiBrightMagenta": ansi.bright_magenta,
            "terminal.ansiBrightCyan": ansi.bright_cyan,
            "terminal.ansiBrightWhite": ansi.bright_white,
            # Cursor
            "terminalCursor.foreground": p.accent,
            "terminalCursor.background": p.background,
            # Selection -- match editor selection. selectionForeground MUST be set
            # explicitly: when null, VS Code applies its "minimum contrast ratio"
            # feature which overrides our carefully tuned ANSI palette with
            # auto-adjusted colors. Pinning to p.foreground keeps the palette stable.
            "terminal.selectionBackground": sel.primary,
            "terminal.selectionForeground": p.foreground,
            "terminal.inactiveSelectionBackground": sel.inactive,
            # Find -- must be transparent (VS Code spec). findMatchBorder outlines
            # the current match so it stands out from other find hits.
            "terminal.findMatchBackground": sel.find_hl,
            "terminal.findMatchBorder": p.accent,
            "terminal.findMatchHighlightBackground": sel.find_hl,
            # Hover and sticky scroll
            # Terminal hover uses alpha so it composites over CLI tools that set
            # their own background colors (htop, lazygit, test runners). Solid
            # colors would obliterate the underlying content. Sticky scroll stays
            # opaque because it's a chrome surface, not content.
            "terminal.hoverHighlightBackground": p.accent.with_alpha(0.12),
            "terminalStickyScroll.background": p.background,
            "terminalStickyScroll.border": p.border,
            "terminalStickyScrollHover.background": p.hover_bg_opaque,
            # Command decorations
            "terminalCommandDecoration.defaultBackground": p.fg_muted,
            "terminalCommandDecoration.successBackground": p.success,
            "terminalCommandDecoration.errorBackground": p.error,
            # Terminal background (panel content area)
            "terminal.background": p.background,
        }
