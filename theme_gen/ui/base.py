"""BaseSection -- root colors, text, button, input, dropdown, scrollbar, badge, progress."""

from typing import override

from core.tcol import TCol
from palette.theme import Theme
from ui.protocol import UISection


class BaseSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        fg = p.foreground

        return {
            "foreground": fg,
            "focusBorder": p.accent,
            "sash.hoverBorder": p.accent,
            "widget.shadow": p.shadow,
            "widget.border": p.border,
            "selection.background": p.selection_bg,
            "icon.foreground": p.fg_icon,
            "descriptionForeground": p.fg_muted,
            "errorForeground": p.error,
            "disabledForeground": p.fg_disabled,
            # Text -- active uses accent_hover (darker shade) for click/press
            # feedback, matching the button hover and editorLink.activeForeground
            # treatment. Without this, links give no visual confirmation when pressed.
            "textLink.foreground": p.accent,
            "textLink.activeForeground": p.accent_hover,
            "textBlockQuote.background": p.panel_bg,
            "textBlockQuote.border": p.border,
            "textCodeBlock.background": p.panel_bg,
            # Markdown preview alerts
            "markdownAlert.note.foreground": p.accent,
            "markdownAlert.tip.foreground": p.success,
            "markdownAlert.important.foreground": p.secondary,
            "markdownAlert.warning.foreground": p.warning,
            "markdownAlert.caution.foreground": p.error,
            "textPreformat.foreground": fg,
            "textPreformat.background": p.panel_bg,
            "textSeparator.foreground": p.text_separator,
            # Button
            "button.background": p.accent,
            "button.foreground": p.fg_on_accent,
            "button.border": p.shadow,
            "button.hoverBackground": p.accent_hover,
            "button.secondaryBackground": p.btn_secondary_bg,
            "button.secondaryForeground": fg,
            # Secondary hover stays in the neutral family -- using accent blue
            # would create false primary-action affordance on Cancel/Dismiss buttons.
            "button.secondaryHoverBackground": p.border_subtle,
            # Input
            "input.background": p.background,
            # Input/dropdown/search borders use `border` (not `border_subtle`) so
            # the field edge is a meaningful affordance. Still below the strict
            # 3:1 non-text threshold at ~1.42:1, but a meaningful improvement
            # over 1.21:1 subtle. Stronger focus state (p.accent) remains the
            # keyboard navigation cue.
            "input.border": p.border,
            "input.foreground": fg,
            "input.placeholderForeground": p.fg_muted,
            "inputOption.activeBorder": p.accent,
            "inputOption.activeBackground": p.hover_bg_neutral,
            "inputOption.activeForeground": fg,
            "inputValidation.errorBackground": p.error_bg,
            "inputValidation.errorForeground": p.error,
            "inputValidation.errorBorder": p.error_border,
            "inputValidation.warningBackground": p.warn_bg,
            "inputValidation.warningForeground": p.warning,
            "inputValidation.warningBorder": p.warn_border,
            "inputValidation.infoBackground": p.info_bg,
            "inputValidation.infoForeground": p.accent,
            "inputValidation.infoBorder": p.info_border,
            # Dropdown (menu inherits from these)
            "dropdown.background": p.surface_elevated,
            "dropdown.border": p.border,
            "dropdown.foreground": fg,
            # Scrollbar
            "scrollbar.shadow": p.shadow,
            "scrollbarSlider.background": p.scrollbar_thumb,
            "scrollbarSlider.hoverBackground": p.scrollbar_hover,
            "scrollbarSlider.activeBackground": p.scrollbar_active,
            # Badge / Progress
            "badge.background": p.accent,
            "badge.foreground": p.fg_on_accent,
            "progressBar.background": p.accent,
            # Keybinding labels -- "keycap" appearance in command palette.
            # panel_bg background + border_subtle top/side + border bottom gives
            # a subtle 3D physical-key effect consistent with the surface system.
            "keybindingLabel.foreground": fg,
            "keybindingLabel.background": p.panel_bg,
            "keybindingLabel.border": p.border_subtle,
            "keybindingLabel.bottomBorder": p.border,
        }
