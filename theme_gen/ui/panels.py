"""PanelSection -- panel body, status bar, title bar, menu, command center.

Surface routing (single-surface panel, floating content):
  panel body + header + output + stickyScroll -> p.panel_bg  (one tier; no
    inversion where header looks "sunken" relative to body)
  commandCenter                               -> p.background  (editor surface;
    this widget sits in the title bar above the editor)
  panel section headers                       -> p.panel_bg    (matches tab row)
  title bar                                   -> p.panel_bg    (groups with tabs)
  status bar                                  -> p.surface_sunken  (deepest chrome)
  menu body                                   -> p.background  (popup elevation)

The "panel" here is the bottom-dock panel (Terminal / Problems / Output / Debug
Console). Putting all its surfaces on panel_bg makes it read as one slab with
floating tabs, matching how the auxiliary (chat) panel is also routed.

Inner dividers (section headers, input borders, picker/command center edges) use
border_subtle so the panel's own outer edge stays loud via p.border.
"""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class PanelSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        e = theme.editor
        fg = p.foreground

        return {
            # Panel -- body + header on one surface. Avoids the "header looks
            # sunken" inversion seen when activeBackground was p.background.
            "panel.background": p.panel_bg,
            "panel.border": p.border,
            "panelTitle.activeBorder": p.accent,
            "panelTitle.activeForeground": fg,
            "panelTitle.activeBackground": p.panel_bg,
            "panelTitle.inactiveForeground": p.fg_muted,
            # panelTitle.border: transparent for the same reason as
            # editorGroupHeader.tabsBorder -- the border between panel tab strip
            # and panel body bleeds through on hover state changes.
            "panelTitle.border": p.foreground.with_alpha(0.0),
            "panelInput.border": p.border_subtle,
            "panelSectionHeader.background": p.panel_bg,
            "panelSectionHeader.foreground": fg,
            "panelSectionHeader.border": p.border_subtle,
            "panelSection.border": p.border_subtle,
            # Panel content areas -- same surface as panel body
            "outputView.background": p.panel_bg,
            # Sticky scroll in panel -- inherits panel surface
            "panelStickyScroll.background": p.panel_bg,
            "panelStickyScroll.border": p.border_subtle,
            # Status Bar -- SUNKEN (matches activity bar; anchors window bottom)
            "statusBar.background": p.surface_sunken,
            "statusBar.foreground": fg,
            # statusBar.border: transparent -- the surface depth change from
            # panel/editor to surface_sunken already separates the regions.
            # A visible border bleeds through when status bar items are hovered.
            "statusBar.border": p.foreground.with_alpha(0.0),
            "statusBar.debuggingBackground": e.chrome.debug_bg,
            "statusBar.debuggingForeground": p.fg_on_accent,
            "statusBar.noFolderBackground": p.surface_sunken,
            "statusBar.focusBorder": p.accent,
            "statusBarItem.hoverBackground": p.hover_bg,
            "statusBarItem.hoverForeground": fg,
            "statusBarItem.activeBackground": p.selection_bg,
            "statusBarItem.compactHoverBackground": p.border_subtle,
            "statusBarItem.focusBorder": p.accent,
            "statusBarItem.errorBackground": e.widgets.status_error_bg,
            "statusBarItem.errorForeground": p.fg_on_accent,
            "statusBarItem.warningBackground": p.warning,
            "statusBarItem.warningForeground": p.fg_on_accent,
            # Prominent items -- stand out from regular status bar entries
            # (used for things like "update available"). drop_bg (accent @ 15%)
            # is visible on sunken L=0.945; the old hover_bg (8%) was too faint.
            "statusBarItem.prominentBackground": p.drop_bg,
            "statusBarItem.prominentForeground": fg,
            # Hover must be STRONGER than base to provide feedback. Use a50
            # so hover is always a visible step above drop_bg (a15 light / a25 dark).
            "statusBarItem.prominentHoverBackground": p.accent.a50,
            "statusBarItem.prominentHoverForeground": fg,
            "statusBarItem.remoteBackground": p.hover_bg,
            "statusBarItem.remoteForeground": fg,
            # Offline state -- agent editors show this frequently; use the muted
            # disabled foreground so it reads as "not quite available" without alarm.
            "statusBarItem.offlineBackground": p.panel_bg,
            "statusBarItem.offlineForeground": p.fg_muted,
            # Title Bar -- SUBTLE panel (matches tab row / sidebar header)
            "titleBar.activeBackground": p.panel_bg,
            "titleBar.activeForeground": fg,
            "titleBar.inactiveBackground": p.panel_bg,
            "titleBar.inactiveForeground": p.fg_muted,
            # titleBar.border: transparent -- title bar and tab strip are both
            # on panel_bg, so no border is needed between them. A visible line
            # would bleed through when menubar items are hovered.
            "titleBar.border": p.foreground.with_alpha(0.0),
            # Menu -- explicitly anchored to prevent OS-native dark-mode
            # fallback on Windows/Linux (Electron native menus can inherit
            # system colors when these are undefined).
            "menu.background": p.surface_elevated,
            "menu.foreground": fg,
            "menu.selectionBackground": p.selection_bg,
            "menu.selectionForeground": fg,
            "menu.separatorBackground": p.border_subtle,
            "menu.border": p.border,
            "menubar.selectionBackground": p.selection_bg,
            "menubar.selectionForeground": fg,
            # Command Center
            "commandCenter.foreground": fg,
            "commandCenter.activeForeground": fg,
            "commandCenter.background": p.background,
            "commandCenter.activeBackground": p.background,
            "commandCenter.border": p.border_subtle,
            "commandCenter.activeBorder": p.accent,
            "commandCenter.inactiveForeground": p.fg_muted,
            "commandCenter.inactiveBorder": p.border_subtle,
            # Banner -- horizontal strip below title bar for workspace warnings,
            # update prompts, restricted-mode notices. Use panel_bg so it reads as
            # chrome (not an editor surface) with accent icon for the severity cue.
            "banner.background": p.panel_bg,
            "banner.foreground": fg,
            "banner.iconForeground": p.accent,
        }
