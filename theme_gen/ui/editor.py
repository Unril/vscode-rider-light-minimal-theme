"""EditorSection -- editor core, line numbers, brackets, gutter, inlay hints, overview ruler."""

from typing import override

from core.tcol import TCol
from palette.theme import Theme
from ui.protocol import UISection


class EditorSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        e = theme.editor
        c = e.chrome
        sel = e.selection
        fg = p.foreground

        return {
            "editor.background": p.background,
            "editor.foreground": fg,
            "editorCursor.foreground": c.caret,
            "editor.lineHighlightBackground": c.caret_row,
            "editor.selectionBackground": sel.primary,
            "editor.inactiveSelectionBackground": sel.inactive,
            "editor.selectionHighlightBackground": sel.highlight,
            "editor.wordHighlightBackground": sel.word_read,
            "editor.wordHighlightTextBackground": sel.word_text,
            "editor.wordHighlightStrongBackground": sel.word_write,
            "editor.findMatchBackground": sel.find_match,
            "editor.findMatchHighlightBackground": sel.find_hl,
            "editor.rangeHighlightBackground": sel.hover_bg,
            "editor.hoverHighlightBackground": sel.hover_bg,
            "editorLineNumber.foreground": c.line_num,
            "editorLineNumber.activeForeground": p.accent,
            "editorIndentGuide.background1": c.indent_guide,
            "editorIndentGuide.activeBackground1": c.indent_guide_active,
            "editorBracketMatch.background": c.bracket_match,
            "editorBracketMatch.border": c.bracket_match_border,
            "editorWhitespace.foreground": c.whitespace,
            "editorRuler.foreground": c.ruler,
            "editorCodeLens.foreground": c.codelens,
            "editorInlayHint.background": c.inlay_bg,
            "editorInlayHint.foreground": c.inlay_fg,
            "editorGutter.background": p.background,
            "editorGutter.addedBackground": p.gutter_add,
            "editorGutter.modifiedBackground": p.gutter_mod,
            "editorGutter.deletedBackground": p.gutter_del,
            "editorError.foreground": p.error,
            "editorWarning.foreground": p.warning,
            "editorInfo.foreground": p.accent,
            # Marker navigation (go-to-error widget)
            "editorMarkerNavigation.background": p.background,
            "editorMarkerNavigationError.background": p.error.a15,
            "editorMarkerNavigationWarning.background": p.warning.a15,
            "editorMarkerNavigationInfo.background": p.accent.a15,
            "editorUnnecessaryCode.opacity": fg.a50,
            # Overview ruler -- density-map treatment (markers at 80% so stacked hits
            # read as intensity instead of an oversaturated clown stripe).
            # The left border separates the minimap slab from the scrollbar track.
            "editorOverviewRuler.background": p.background,
            "editorOverviewRuler.border": p.border_subtle,
            "editorOverviewRuler.errorForeground": p.error.a80,
            "editorOverviewRuler.warningForeground": p.warning.a80,
            "editorOverviewRuler.infoForeground": p.accent.a80,
            "editorOverviewRuler.modifiedForeground": p.gutter_mod,
            "editorOverviewRuler.addedForeground": p.gutter_add,
            "editorOverviewRuler.deletedForeground": p.gutter_del,
            "editorOverviewRuler.findMatchForeground": sel.find_ruler,
            "editorOverviewRuler.bracketMatchForeground": c.bracket_match_border,
            # Ruler markers for editor highlights (word occurrences, selections,
            # range highlights from Quick Open / goto-symbol). Reference requires
            # non-opaque values so underlying ruler content isn't hidden.
            "editorOverviewRuler.wordHighlightForeground": sel.word_read,
            "editorOverviewRuler.wordHighlightStrongForeground": sel.word_write,
            "editorOverviewRuler.wordHighlightTextForeground": sel.word_text,
            "editorOverviewRuler.selectionHighlightForeground": sel.highlight,
            "editorOverviewRuler.rangeHighlightForeground": sel.hover_bg,
            # Sticky scroll (shadow inherits from scrollbar.shadow)
            "editorStickyScroll.background": p.background,
            "editorStickyScrollHover.background": p.hover_bg_opaque,
            "editorLink.activeForeground": p.accent_hover,
            "editor.foldBackground": sel.hover_bg,
            "editorGutter.foldingControlForeground": p.fg_muted,
            "editorGhostText.foreground": p.fg_disabled,
            "editorHint.foreground": p.fg_muted,
            # Bracket pair colorization — hue-shifted series matching heading colors
            **{
                f"editorBracketHighlight.foreground{i}": color
                for i, color in enumerate(theme.syntax.hue_shifted, start=1)
            },
            "editorBracketHighlight.unexpectedBracket.foreground": p.error,
            # Stack frames
            "editor.stackFrameHighlightBackground": c.stack_frame,
            "editor.focusedStackFrameHighlightBackground": c.stack_focused,
            # Editor lightbulb -- warm gold for code action attention
            "editorLightBulb.foreground": p.secondary,
            "editorLightBulbAutoFix.foreground": p.secondary,
            # Gutter comment markers -- warm attention for annotations/reviews
            "editorGutter.commentGlyphForeground": p.secondary,
            "editorGutter.commentUnresolvedGlyphForeground": p.secondary,
            "editorGutter.commentDraftGlyphForeground": p.secondary.a50,
        }
