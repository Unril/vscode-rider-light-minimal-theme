"""WidgetSection -- editor widgets, suggest, peek, quick picker, notifications, settings.

Border philosophy: widgets use shadow for separation, not borders.
Only peek view uses accent border as a design element.
"""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class WidgetSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        e = theme.editor
        fg = p.foreground

        return {
            "editorWidget.background": p.surface_elevated,
            "editorWidget.border": p.border,
            "editorSuggestWidget.background": p.surface_elevated,
            "editorSuggestWidget.border": p.border,
            "editorSuggestWidget.foreground": fg,
            "editorSuggestWidget.selectedBackground": p.selection_bg,
            "editorSuggestWidget.selectedForeground": fg,
            "editorSuggestWidget.highlightForeground": p.accent,
            "editorSuggestWidget.focusHighlightForeground": p.accent,
            # Hover widget — slightly elevated surface
            "editorHoverWidget.background": p.surface_elevated,
            "editorHoverWidget.border": p.border,
            "editorHoverWidget.foreground": fg,
            "editorHoverWidget.highlightForeground": p.accent,
            # Hover widget status bar -- the "⌘ click to go to definition" hint
            # at the bottom. Grounded on panel_bg so it reads as a footer strip
            # rather than floating text at the popup's edge.
            "editorHoverWidget.statusBarBackground": p.panel_bg,
            # Quick input / command palette
            "quickInput.background": p.surface_elevated,
            "quickInput.foreground": fg,
            # Peek view — accent border is intentional design element
            "peekView.border": p.accent,
            "peekViewEditor.background": p.panel_bg,
            "peekViewResult.background": p.panel_bg,
            "peekViewTitle.background": p.panel_bg,
            "peekViewResult.selectionBackground": p.selection_bg,
            "peekViewResult.selectionForeground": fg,
            "peekViewTitleLabel.foreground": fg,
            "peekViewTitleDescription.foreground": p.fg_muted,
            "peekViewResult.fileForeground": fg,
            "peekViewResult.lineForeground": p.fg_muted,
            "peekViewEditor.matchHighlightBackground": e.widgets.peek_match_hl,
            "peekViewResult.matchHighlightBackground": e.widgets.peek_match_hl,
            # Notifications -- elevated (float on top of the UI)
            "notifications.background": p.surface_elevated,
            "notifications.foreground": fg,
            "notificationCenterHeader.background": p.surface_elevated,
            "notificationCenterHeader.foreground": fg,
            "notificationsErrorIcon.foreground": p.error,
            "notificationsWarningIcon.foreground": p.warning,
            "notificationsInfoIcon.foreground": p.accent,
            "notificationLink.foreground": p.accent,
            "notificationCenter.border": p.border,
            "notificationToast.border": p.border,
            # Quick picker
            "quickInputList.focusBackground": p.selection_bg,
            "pickerGroup.border": p.border_subtle,
            "pickerGroup.foreground": p.fg_muted,
            # Toolbar
            "toolbar.hoverBackground": p.hover_bg_neutral,
            "toolbar.activeBackground": p.selection_bg,
            # Search editor -- input edge uses `border` (not `border_subtle`)
            # so the field reads as interactive.
            "searchEditor.textInputBorder": p.border,
            # Input option hover
            "inputOption.hoverBackground": p.hover_bg_neutral,
            # Settings
            "settings.dropdownBackground": p.surface_elevated,
            "settings.dropdownBorder": p.border,
            "settings.headerForeground": fg,
            # Settings inputs -- input edge uses `border` (not `border_subtle`)
            # so the field reads as interactive.
            "settings.numberInputBorder": p.border,
            "settings.textInputBorder": p.border,
            "settings.modifiedItemIndicator": e.widgets.settings_modified,
            "settings.rowHoverBackground": p.hover_bg_neutral,
            # Welcome page
            "welcomePage.tileBackground": p.panel_bg,
            "welcomePage.tileHoverBackground": p.welcome_tile_hover,
            # Action bar
            "actionBar.toggledBackground": p.border_subtle,
        }
