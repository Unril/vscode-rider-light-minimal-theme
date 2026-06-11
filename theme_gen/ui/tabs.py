"""TabSection -- editor groups, tabs, breadcrumbs.

Active tab is VISUALLY DISTINCT from inactive tabs. The chrome strip (tab
container, inactive tabs) uses panel_bg; the active tab uses editor_bg. This
is the primary cue users rely on to identify the active file.

  Title bar + sidebar header + tab strip + inactive tabs -> panel_bg (chrome)
  Active tab + editor body + breadcrumbs                 -> editor_bg

Active/inactive distinction carried by THREE stacked cues:
  1. Surface: editor_bg vs panel_bg (the dominant cue, visible at a glance)
  2. Accent top border (2px blue line on active only)
  3. Full-strength fg on active vs fg_muted on inactive

Modified (dirty) indicators replace the accent top with secondary (warm gold)
on active dirty tabs. Inactive dirty tabs get a half-alpha secondary line.
"""

from typing import override

from core.tcol import TCol
from palette.theme import Theme
from ui.protocol import UISection


class TabSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        fg = p.foreground
        editor_bg = p.background

        return {
            # Editor groups -- subtle divider between splits (the surface stays the same)
            "editorGroup.border": p.border_subtle,
            "editorGroup.dropBackground": p.drop_bg,
            "editorGroup.focusedEmptyBorder": p.accent,
            # Tab container -- panel_bg. Matches sidebar header + title bar so
            # the entire chrome band above the editor is one surface. This avoids
            # the visible rectangular boundary between sidebar chrome and the tab
            # region that appears when tabs are on editor_bg.
            "editorGroupHeader.tabsBackground": p.panel_bg,
            # tabsBorder is the 1px line below the entire tab strip. Setting it
            # to transparent eliminates the bottom-line artefacts on hover --
            # the surface hierarchy (panel_bg strip vs editor_bg editor) already
            # separates the two regions without needing an explicit divider.
            "editorGroupHeader.tabsBorder": p.foreground.with_alpha(0.0),
            # Active tab -- editor_bg. CLEARLY distinct from inactive (panel_bg,
            # L=0.975). The active tab sits on the editor surface, visually extruding
            # from the chrome strip into the editor region below. This is the
            # primary way users identify which file is active -- the 2% surface
            # delta is the dominant cue, reinforced by accent top border and
            # full-strength foreground text.
            "tab.activeBackground": editor_bg,
            "tab.activeForeground": fg,
            "tab.activeBorderTop": p.accent,
            # Bottom border on active tab -- match editor_bg so the active tab
            # visually extrudes seamlessly into the editor surface below
            # (JetBrains/Rider extrusion pattern). The editorGroupHeader.tabsBorder
            # is hidden under the active tab by this 1px overlay.
            "tab.activeBorder": editor_bg,
            "tab.unfocusedActiveBorder": editor_bg,
            "tab.unfocusedActiveBorderTop": p.border_subtle,
            # Inactive tabs -- surface_sunken (L=0.935). The 6% delta from active
            # (editor_bg L=0.995) makes the active tab unambiguously brighter.
            # This matches the Light+/GitHub convention where inactive tabs are
            # clearly grayed out, not "almost the same as active."
            "tab.inactiveBackground": p.surface_sunken,
            # Unfocused-group backgrounds -- active stays editor_bg regardless of
            # focus; inactive stays sunken.
            "tab.unfocusedActiveBackground": editor_bg,
            "tab.unfocusedInactiveBackground": p.surface_sunken,
            # Inactive foreground uses fg_muted -- readable (passes WCAG AA on
            # panel_bg) while still visibly dimmer than active tab's fg. Review
            # noted fg_disabled at ~2.45:1 failed accessibility for tab labels,
            # which are actual text not non-text UI indicators.
            "tab.inactiveForeground": p.fg_muted,
            # Tab separators -- panel_bg (same as strip and inactive tabs). Active
            # tab stands out via its editor_bg background, not via separator lines.
            "tab.border": p.panel_bg,
            # Hover -- opaque light blue for clear interactive feedback.
            "tab.hoverBackground": p.hover_bg_opaque,
            "tab.hoverForeground": fg,
            "tab.unfocusedHoverBackground": p.hover_bg_opaque,
            # Unfocused -- active at full fg, inactive at fg_muted (same as focused
            # inactive) so unfocused-inactive tabs stay legible.
            "tab.unfocusedActiveForeground": fg,
            "tab.unfocusedInactiveForeground": p.fg_muted,
            # Modified (dirty) indicators. Active uses secondary (warm gold) for
            # a distinct "this tab has unsaved changes" cue; inactive variant keeps
            # the signal visible on tabs the user isn't currently focused on.
            "tab.activeModifiedBorder": p.secondary,
            "tab.inactiveModifiedBorder": p.secondary.a50,
            "tab.unfocusedActiveModifiedBorder": p.secondary.a50,
            # Hover border -- fully transparent. VS Code uses one token for both
            # active and inactive tab hover borders; any visible color shows as
            # a line against one surface or the other (active=editor_bg vs
            # inactive=sunken). Transparent eliminates the line entirely.
            "tab.hoverBorder": p.foreground.with_alpha(0.0),
            "tab.unfocusedHoverBorder": p.foreground.with_alpha(0.0),
            # Drag-drop indicator -- accent line shown when a tab is being dragged.
            "tab.dragAndDropBorder": p.accent,
            # Pinned-tab boundary -- separator between pinned and unpinned tabs.
            # Uses the loud border so the pinned group is visibly distinct.
            "tab.lastPinnedBorder": p.border,
            # Breadcrumbs -- secondary "you are here" (the primary cue is the active
            # tab). Use fg_muted so the breadcrumb is legible while reading quieter
            # than the tab row; hovered/focused path elements get full fg.
            "breadcrumb.foreground": p.fg_muted,
            "breadcrumb.focusForeground": fg,
            "breadcrumb.activeSelectionForeground": fg,
            "breadcrumb.background": editor_bg,
        }
