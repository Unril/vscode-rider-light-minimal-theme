"""TerminalSection -- ANSI colors, cursor, selection, find, sticky scroll, command decorations."""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class TerminalSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        sel = theme.editor.selection
        ansi = theme.editor.ansi

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
