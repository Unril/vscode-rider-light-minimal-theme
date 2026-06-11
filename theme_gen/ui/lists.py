"""ListSection -- list/tree, activity bar, sidebar.

Surface routing:
  activity bar            ->  surface_sunken  (deepest chrome, anchors window edge)
  sidebar / tree body     ->  panel_bg        (subtle, distinct from editor)
  list hover              ->  hover_bg_neutral (quiet gray -- routine hover)
  list active selection   ->  selection_bg    (accent-tinted -- focused state)
  list inactive selection ->  hover_bg_neutral (distinct from active so focus-loss is visible)
  list focus (keyboard)   ->  drop_bg         (accent-tinted at higher alpha than hover)
"""

from typing import override

from core.tcol import TCol
from palette.theme import Theme
from ui.protocol import UISection


class ListSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        fg = p.foreground

        return {
            # Lists — hover is neutral, selection is accent-tinted for clear distinction
            "list.activeSelectionBackground": p.selection_bg,
            "list.activeSelectionForeground": fg,
            "list.focusBackground": p.drop_bg,
            "list.focusForeground": fg,
            "list.hoverBackground": p.hover_bg_neutral,
            "list.hoverForeground": fg,
            # Inactive selection (tree unfocused) -- 8% accent. Quality review
            # flagged that 12% vs 15% active blended to a 1.04:1 contrast ratio
            # -- visually identical. Widening to 8%-vs-15% gives a perceivable
            # lightness gap while keeping the "your file is open" signal visible.
            "list.inactiveSelectionBackground": p.accent.with_alpha(0.08),
            "list.inactiveSelectionForeground": fg,
            "list.inactiveSelectionIconForeground": fg,
            "list.highlightForeground": p.accent,
            "list.activeSelectionIconForeground": fg,
            "list.errorForeground": p.error,
            "list.warningForeground": p.warning,
            "list.focusOutline": p.accent,
            "list.focusAndSelectionOutline": p.accent,
            "list.focusHighlightForeground": p.accent,
            "list.filterMatchBackground": p.secondary.a15,
            "list.dropBackground": p.hover_bg,
            # Inactive focus -- dimmer than active focus so the user sees that
            # keyboard focus has moved to the editor. Active uses drop_bg (accent
            # at 15%); inactive drops to 8% so the "your file is still highlighted"
            # signal persists without competing with the editor's focus.
            "list.inactiveFocusBackground": p.accent.with_alpha(0.08),
            # Tree indent guides -- a12 gives ~10% perceived darkness on panel_bg.
            # Stronger than editor-indent-guide scale because sidebar text is smaller
            # and navigation benefits from clear hierarchy, but not so strong that
            # the guides dominate the content.
            "tree.indentGuidesStroke": p.foreground.with_alpha(0.12),
            # Inactive branch guides (folders not containing the currently-focused item)
            # -- half the strength so the active branch path visually leads the eye.
            "tree.inactiveIndentGuidesStroke": p.foreground.with_alpha(0.06),
            # Activity Bar -- SUNKEN (deepest chrome, anchors the window)
            "activityBar.background": p.surface_sunken,
            "activityBar.foreground": fg,
            "activityBar.inactiveForeground": p.fg_muted,
            "activityBar.border": p.border_subtle,  # surface contrast does the separation; line stays quiet
            "activityBar.activeBorder": p.accent,
            "activityBar.activeFocusBorder": p.accent,
            "activityBar.activeBackground": p.selection_bg,
            "activityBarBadge.background": p.accent,
            "activityBarBadge.foreground": p.fg_on_accent,
            # Activity Bar Top (when positioned at top) -- same sunken treatment
            "activityBarTop.foreground": fg,
            "activityBarTop.inactiveForeground": p.fg_muted,
            "activityBarTop.activeBorder": p.accent,
            "activityBarTop.background": p.surface_sunken,
            "activityBarTop.activeBackground": p.selection_bg,
            # Side Bar -- SUBTLE panel (one level above sunken, below editor)
            # Outer edge uses `border` (not border_subtle) because the adjacent surface
            # (editor at L=0.995) is only 2% lighter than panel_bg (L=0.975). That's enough
            # for surface-depth perception but too subtle for pane boundaries -- a stronger
            # line divides "sidebar region" from "editor region" clearly.
            # This routing also governs the auxiliary bar (secondary sidebar) since VS Code
            # reuses sideBar.background/border for it -- no dedicated auxiliaryBar.* keys exist.
            "sideBar.background": p.panel_bg,
            "sideBar.foreground": fg,
            "sideBar.border": p.border,
            "sideBarTitle.foreground": fg,
            "sideBarTitle.background": p.surface_sunken,
            "sideBarSectionHeader.foreground": fg,
            "sideBarSectionHeader.background": p.panel_bg,
            # Header-to-body divider is intentionally invisible: header and body
            # share the same surface (panel_bg), so the only cue between them
            # should be typography, not a line. A visible divider fragmented what
            # is semantically one region (the sidebar panel).
            "sideBarSectionHeader.border": p.panel_bg,
            "sideBar.dropBackground": p.hover_bg,
            # Sticky scroll in sidebar
            "sideBarStickyScroll.background": p.panel_bg,
            "sideBarStickyScroll.border": p.border_subtle,
        }
