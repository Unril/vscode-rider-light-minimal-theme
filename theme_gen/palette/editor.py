"""EditorPalette -- editor chrome colors derived from palette base colors.

All values are derived from Palette seed colors using TCol lightness/chroma/alpha
steps. No hardcoded hex values.

Sub-palettes group related fields:
  SymbolColors   -- symbol icon colors mapped from syntax roles
  OutputColors   -- terminal/output panel log-level tokens
  EditorChrome   -- caret, line numbers, brackets, guides, inlay hints
  SelectionColors -- selection, word highlights, find matches (transparent)
  WidgetColors   -- status bar, peek view, settings, chat, notebook
  AnsiColors     -- terminal ANSI colors (palette/ansi.py)
"""

from dataclasses import dataclass
from typing import Self

from theme_gen.core.tcol import TCol
from theme_gen.palette.ansi import AnsiColors
from theme_gen.palette.palette import Palette
from theme_gen.palette.syntax import SyntaxPalette

# Dark themes need higher alpha for overlays to be visible on dark backgrounds.
# Light alpha -> dark alpha mapping (roughly 1.5x).
_ALPHA_LIGHT = (0.05, 0.15, 0.25)
_ALPHA_DARK = (0.10, 0.22, 0.35)


def _tint(color: TCol, *, is_dark: bool) -> TCol:
    """Shift a color toward the background: darker on dark, lighter on light."""
    return color.much_darker if is_dark else color.much_lighter


def _overlay(color: TCol, level: int, *, is_dark: bool) -> TCol:
    """Apply alpha overlay at level 0/1/2, scaled for dark backgrounds."""
    alphas = _ALPHA_DARK if is_dark else _ALPHA_LIGHT
    return color.with_alpha(alphas[level])


@dataclass(frozen=True)
class SymbolColors:
    """Symbol icon colors mapped from syntax roles."""

    cls: TCol  # class/struct
    function: TCol
    interface: TCol
    variable: TCol
    constant: TCol
    enum: TCol
    enum_member: TCol
    property: TCol
    keyword: TCol
    namespace: TCol
    string: TCol
    number: TCol


@dataclass(frozen=True)
class OutputColors:
    """Terminal and output panel log-level token colors."""

    info: TCol
    warn: TCol
    error: TCol
    debug: TCol


@dataclass(frozen=True)
class EditorChrome:
    """Editor surface colors: caret, guides, brackets, inlay hints."""

    caret: TCol
    caret_row: TCol
    line_num: TCol
    indent_guide: TCol
    indent_guide_active: TCol
    bracket_match: TCol
    bracket_match_border: TCol
    whitespace: TCol
    ruler: TCol
    inlay_bg: TCol
    inlay_fg: TCol
    codelens: TCol
    info_fg: TCol
    stack_frame: TCol
    stack_focused: TCol
    debug_bg: TCol


@dataclass(frozen=True)
class SelectionColors:
    """Selection and highlight colors (transparent -- must not hide decorations)."""

    primary: TCol  # editor selection
    inactive: TCol  # inactive editor selection
    highlight: TCol  # other occurrences of selected text
    word_read: TCol  # symbol read-access highlight
    word_write: TCol  # symbol write-access highlight
    word_text: TCol  # textual occurrence highlight (secondary accent)
    # hover_bg is a faint accent wash used for three editor decorations that
    # can light up many rows at once: range highlight (find/goto), hover
    # highlight (word under mouse), and fold background. Sharing one value
    # keeps the "faint wash" signal uniform; splitting later is an easy edit.
    hover_bg: TCol
    find_match: TCol  # current find match
    find_hl: TCol  # other find matches
    find_ruler: TCol  # find match in overview ruler


@dataclass(frozen=True)
class WidgetColors:
    """UI chrome: status bar, peek view, settings, chat, notebook."""

    status_error_bg: TCol
    peek_match_hl: TCol
    settings_modified: TCol
    chat_edited_fg: TCol
    notebook_cell_bg: TCol
    slash_cmd_fg: TCol
    chat_lines_add: TCol
    chat_lines_remove: TCol


@dataclass(frozen=True)
class EditorPalette:
    """Editor chrome colors bridging syntax and UI.

    Composed of six sub-palettes for logical grouping.
    Consumers access fields via sub-palette: ``e.chrome.caret``, ``e.selection.primary``, etc.
    """

    symbols: SymbolColors
    output: OutputColors
    chrome: EditorChrome
    selection: SelectionColors
    widgets: WidgetColors
    ansi: AnsiColors

    @classmethod
    def create(cls, syntax: SyntaxPalette, palette: Palette) -> Self:
        """Derive all editor chrome from palette base colors."""
        accent = palette.accent
        secondary = palette.secondary
        warning = palette.warning
        success = palette.success
        error = palette.error

        is_dark = palette.is_dark

        # Subtle tinted backgrounds: shift toward bg, then apply modifier.
        bracket_base = _tint(secondary, is_dark=is_dark)
        stack_frame_base = _tint(warning, is_dark=is_dark).muted
        stack_focused_base = _tint(success, is_dark=is_dark).muted
        find_match_base = _tint(accent, is_dark=is_dark).soft
        notebook_base = _tint(accent, is_dark=is_dark).muted.a80

        # Symbol icons appear in sidebar (outline, breadcrumbs, symbol picker)
        # which sits on panel_bg. Ensure each symbol color meets 4.6:1 there.
        panel_bg = palette.panel_bg

        def _sym(c: TCol) -> TCol:
            return c.with_min_contrast(panel_bg, 4.6)

        return cls(
            symbols=SymbolColors(
                cls=_sym(syntax.type),
                function=_sym(syntax.function),
                interface=_sym(syntax.type),
                variable=_sym(syntax.field),
                constant=_sym(syntax.field),
                enum=_sym(syntax.type),
                enum_member=_sym(syntax.enum_member),
                property=_sym(syntax.field),
                keyword=_sym(syntax.keyword),
                namespace=_sym(syntax.namespace),
                string=_sym(syntax.string),
                number=_sym(syntax.number),
            ),
            output=OutputColors(
                info=accent,
                warn=warning,
                error=error,
                debug=palette.fg_muted,
            ),
            chrome=EditorChrome(
                caret=accent,
                caret_row=_overlay(palette.foreground, 0, is_dark=is_dark),
                # Line numbers are structural navigation, not "disabled" chrome -- use
                # fg_muted (WCAG-AA-passing) so they stay legible at small sizes.
                line_num=palette.fg_muted,
                # Indent guides -- inactive at 5% so deeply-nested code (Python
                # especially) doesn't develop a zebra-stripe pattern. Active stays
                # at 25% so the current scope is clearly highlighted -- 5x the
                # inactive alpha gives unambiguous focus without visual noise from
                # uninvolved branches. Bumped from a15 inactive (review found 15%
                # produced visible vertical stripes in long indented blocks).
                indent_guide=palette.foreground.a05,
                indent_guide_active=palette.foreground.a25,
                whitespace=palette.fg_disabled,
                ruler=palette.foreground.a25,  # stronger than indent_guide so ruler is distinguishable
                # Inlay hints: alpha background so hints composite over
                # selection/find-match highlights instead of punching opaque
                # holes through them. Light uses 8% fg (visible pill on white);
                # dark uses 10% fg (slightly stronger to register on dark bg).
                inlay_bg=palette.foreground.with_alpha(0.08) if not is_dark else palette.foreground.with_alpha(0.10),
                inlay_fg=palette.fg_muted,
                codelens=palette.fg_muted,
                info_fg=palette.fg_muted,
                bracket_match=bracket_base.muted,
                bracket_match_border=secondary.soft,  # crisper than tinted form -- bracket-match is a key reading cue
                stack_frame=stack_frame_base,
                stack_focused=stack_focused_base,
                debug_bg=success.muted,
            ),
            selection=SelectionColors(
                primary=_overlay(accent, 1, is_dark=is_dark),
                # Inactive selection -- dropped to 8% alpha so it reads clearly
                # lighter than primary (15%). Quality review found the previous
                # 12% inactive vs 15% primary blended to contrast 1.04:1 --
                # visually identical. 8% gives a clearer lightness gap while
                # keeping the "your selection survives focus loss" signal.
                inactive=accent.with_alpha(0.14 if is_dark else 0.08),
                # highlight is "other occurrences of the current selection" -- must read
                # between hover_bg (level 0 -- can cover many rows) and primary (level 1 --
                # the focused selection). Uses a dedicated mid-alpha so it sits visibly
                # between the two without colliding with either.
                highlight=accent.with_alpha(0.16 if is_dark else 0.10),
                # Read vs write occurrences: VS Code exposes these as two distinct
                # decorations (editor.wordHighlightBackground for reads,
                # editor.wordHighlightStrongBackground for writes). Setting them
                # to the same value erases a refactoring-relevant signal -- you
                # want the write sites of a symbol to stand out from reads since
                # mutations are more consequential. Both stay in the accent family
                # for now; moving reads to neutral gray to solve blue-family
                # stacking with selection is tracked as an open refactor.
                word_read=accent.with_alpha(0.25 if is_dark else 0.18),
                word_write=accent.with_alpha(0.38 if is_dark else 0.28),
                word_text=_overlay(secondary, 1, is_dark=is_dark),
                hover_bg=_overlay(accent, 0, is_dark=is_dark),
                find_match=find_match_base,
                find_hl=_overlay(warning, 2, is_dark=is_dark),
                find_ruler=warning.a50,
            ),
            widgets=WidgetColors(
                status_error_bg=error.vivid,
                peek_match_hl=warning.a25,
                settings_modified=secondary.vivid,
                chat_edited_fg=secondary.s700 if not is_dark else secondary.s300,
                notebook_cell_bg=notebook_base,
                slash_cmd_fg=accent.darker.vivid if not is_dark else palette.accent_hover,
                chat_lines_add=success.a80,
                chat_lines_remove=error.a80,
            ),
            ansi=AnsiColors.for_dark(palette.background) if is_dark else AnsiColors.for_light(palette.background),
        )
