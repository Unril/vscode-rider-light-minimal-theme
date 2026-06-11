"""Palette -- central seed values derived from accent_hue + variant parameters."""

from dataclasses import dataclass
from typing import Self

from core.tcol import TCol

# Status color hues (OKLCH, fixed by convention)
_HUE_ERROR = 20.0
_HUE_WARNING = 55.0
_HUE_SUCCESS = 150.0

# Chroma levels (base chroma is at s500 peak; steps scale from this)
_CHROMA_VIVID = 0.163

# Secondary accent offset (complementary hue)
_SECONDARY_HUE_OFFSET = 180.0

# Foreground lightness per variant (OKLCH L)
_FG_LIGHTNESS_LIGHT = 0.20
_FG_LIGHTNESS_DARK = 0.83

# Dark variant background tint
_DARK_BG_CHROMA = 0.018

# Light variant surface hierarchy -- warm off-white base
# Hue 85 is pale yellow; 0.002 chroma is imperceptibly warm at screen scale
# but hides the "blue-screen glow" of pure #FFFFFF on calibrated monitors.
# (Was 0.004 -- dropped in half after full-IDE testing showed a faint cream cast
# when large contiguous surface areas filled the viewport.)
_LIGHT_SURFACE_HUE = 85.0
_LIGHT_SURFACE_CHROMA = 0.002


@dataclass(frozen=True)
class Palette:
    """Seed values + derived chromatic alpha variants for a theme variant."""

    # 5 chromatic anchors (opaque)
    accent: TCol
    secondary: TCol
    error: TCol
    warning: TCol
    success: TCol

    # Surface hierarchy (achromatic, 4 levels + borders)
    # elevated > default > subtle > sunken; readers parse depth by contrast.
    surface_elevated: TCol  # hover cards, command palette, notifications
    foreground: TCol
    background: TCol  # "surface_default" -- editor, active tab, tab row, inputs
    panel_bg: TCol  # "surface_subtle" -- sidebar, title bar, inactive tab, section headers, peek view, minimap
    surface_sunken: TCol  # activity bar, status bar -- deepest container chrome
    border: TCol  # loud: widget edges, panel outlines, focused inputs
    border_subtle: TCol  # quiet: tab separators, section dividers, input borders

    # Foreground variants
    fg_muted: TCol
    fg_disabled: TCol
    fg_icon: TCol
    # fg_on_accent: text color to use against an accent-colored surface
    # (badges, buttons, status-bar error/warning). On light this is elevated
    # (near-white) for max contrast; on dark this is editor_bg (near-black)
    # since the dark accent is light enough to put dark text on.
    fg_on_accent: TCol

    # Interactive surfaces (list/tree hover, selection)
    hover_bg: TCol  # accent-tinted -- focus, drop targets, primary actions
    hover_bg_neutral: TCol  # neutral -- everyday list/tree row hover
    selection_bg: TCol

    # Derived: accent
    link: TCol
    accent_hover: TCol

    # Validation backgrounds and borders
    error_bg: TCol
    error_border: TCol
    warn_bg: TCol
    warn_border: TCol
    info_bg: TCol
    info_border: TCol

    # Gutter / diff markers
    gutter_add: TCol
    gutter_mod: TCol
    gutter_del: TCol
    # Diff line vs text -- VS Code stacks line background and text background
    # additively, so a modified line with word-level changes uses BOTH. Keeping
    # them at the same alpha produced a dark blob (~28% effective) right where
    # readability matters most. Line is now a faint wash; text stays prominent
    # so word-level diffs pop against the row.
    diff_insert_line: TCol
    diff_remove_line: TCol
    diff_insert: TCol
    diff_remove: TCol

    # Minimap highlights
    minimap_error: TCol
    minimap_warning: TCol
    minimap_slider: TCol

    # Scrollbar
    scrollbar_thumb: TCol
    scrollbar_hover: TCol
    scrollbar_active: TCol

    # UI chrome (neutral derived)
    btn_secondary_bg: TCol
    text_separator: TCol
    status_prominent_bg: TCol

    # Reusable overlays and tints
    shadow: TCol  # fg @ 15% -- widget shadow, button border, preformat bg
    drop_bg: TCol  # accent @ 15% -- drop targets, focus backgrounds, slash cmd bg
    accent_wash: TCol  # accent @ 5% -- very faint accent tint (chat request bg)
    hover_bg_opaque: TCol  # accent s100 -- opaque accent tint for terminal/sticky hover

    # Variant flag
    is_dark: bool

    @classmethod
    def for_light(cls, accent_hue: float = 262.0) -> Self:
        """Light variant: derive all fields from accent_hue.

        Surface hierarchy (4 levels, warm off-white base):
          L=1.000  elevated -- hover cards, command palette, notifications
          L=0.995  default  -- editor, active tab, inputs (warm off-white)
          L=0.955  subtle   -- sidebar, title bar, inactive tabs, section headers, peek view
          L=0.920  sunken   -- activity bar, status bar
          L=0.910  border_subtle -- tab separators, input borders, section dividers
          L=0.850  border        -- widget edges, panel outlines, focused inputs

        Chrome contrast inspired by VS Code Light+ (5% editor/sidebar delta)
        tempered with this theme's warmer, softer aesthetic.

        Foreground hierarchy:
          L=0.20  foreground, icons (near-black)
          L=0.56  muted text (descriptions, inactive tabs, line numbers)
          L=0.72  disabled text (placeholders, ghost text)

        The off-white at L=0.995 with a 0.002 chroma at hue 85 is a barely-perceptible
        warm tint. It hides the "blue-screen glow" of pure white #FFFFFF without
        reading as colored at any reasonable viewing distance.
        """
        accent_base = TCol.from_oklch(0.50, _CHROMA_VIVID, accent_hue)
        secondary_base = TCol.from_oklch(0.50, _CHROMA_VIVID, accent_hue + _SECONDARY_HUE_OFFSET)
        neutral = TCol.from_oklch(0.50, 0.0, 0.0)

        # 4-level surface hierarchy, all warm-tinted with a hint of yellow at hue 85.
        # 3% editor/sidebar delta -- visible without looking heavy.
        elevated = TCol.from_oklch(1.000, 0.0, 0.0)  # pure white for maximum lift
        default_bg = TCol.from_oklch(0.995, _LIGHT_SURFACE_CHROMA, _LIGHT_SURFACE_HUE)  # warm off-white
        panel = TCol.from_oklch(0.965, _LIGHT_SURFACE_CHROMA, _LIGHT_SURFACE_HUE)  # sidebar, tab row, title bar
        sunken = TCol.from_oklch(0.935, _LIGHT_SURFACE_CHROMA, _LIGHT_SURFACE_HUE)  # activity bar, status bar
        border_val = TCol.from_oklch(0.870, 0.0, 0.0)  # loud border
        border_sub = TCol.from_oklch(0.920, 0.0, 0.0)  # subtle inner divider

        # Foregrounds -- darker than before for better contrast (Rider uses #000000)
        fg = TCol.from_oklch(_FG_LIGHTNESS_LIGHT, 0.0, 0.0)

        accent = accent_base.s600.with_min_contrast(panel, 4.6)
        secondary = secondary_base.s600.with_min_contrast(panel, 4.6)
        error_base = TCol.from_oklch(0.50, _CHROMA_VIVID, _HUE_ERROR)
        warning_base = TCol.from_oklch(0.50, _CHROMA_VIVID, _HUE_WARNING)
        success_base = TCol.from_oklch(0.50, _CHROMA_VIVID, _HUE_SUCCESS)
        error = error_base.s600.with_min_contrast(panel, 4.6)
        warning = warning_base.s400.with_min_contrast(panel, 4.6)
        success = success_base.s600.with_min_contrast(panel, 4.6)

        return cls(
            accent=accent,
            secondary=secondary,
            error=error,
            warning=warning,
            success=success,
            surface_elevated=elevated,
            foreground=fg,
            background=default_bg,
            panel_bg=panel,
            surface_sunken=sunken,
            border=border_val,
            border_subtle=border_sub,
            # fg_muted targets sunken (deepest chrome) for WCAG AA. Floor of 4.6
            # (not 4.5) absorbs quantization loss when Brent's OKLCH solution is
            # rounded to 8-bit sRGB -- without the buffer the output misses 4.5:1
            # by ~0.02 on sunken (found by quality review).
            fg_muted=neutral.s600.with_min_contrast(sunken, 4.6),
            fg_disabled=neutral.s400,
            fg_icon=fg,
            fg_on_accent=elevated,
            hover_bg=accent.with_alpha(0.08),
            hover_bg_neutral=neutral.with_alpha(0.05),
            selection_bg=accent.with_alpha(0.15),
            link=accent_base.s800,
            # accent_hover darker than default s500 so fg_on_accent (white) meets
            # WCAG AA when layered on the hover color (button, editorLink:active).
            accent_hover=accent_base.s700,
            error_bg=error.a05,
            error_border=error.a50,
            warn_bg=warning.a05,
            warn_border=warning.a50,
            # Info border at a50 for semantic consistency with error/warn borders.
            # (An earlier revision used a25 to avoid collision with gutter_mod, but
            # the two almost never co-occur in the same UI region, and a25 is too
            # faint for an actual validation border.)
            info_bg=accent.a05,
            info_border=accent.a50,
            gutter_add=success.a50,
            gutter_mod=accent.a50,
            gutter_del=error.a50,
            diff_insert_line=success.a05,
            diff_remove_line=error.a05,
            diff_insert=success.a15,
            diff_remove=error.a15,
            minimap_error=error.a80,
            minimap_warning=warning.a80,
            minimap_slider=fg.with_alpha(0.08),
            scrollbar_thumb=fg.with_alpha(0.12),  # light scrollbar is gentle; thumb visible, not heavy
            scrollbar_hover=fg.a25,
            scrollbar_active=fg.a50,
            btn_secondary_bg=neutral.s100,
            # textSeparator paints <hr> lines in hover tooltips and markdown
            # preview dividers. Must match the theme's soft border system
            # (border_subtle) -- pure foreground reads as harsh on off-white.
            text_separator=border_sub,
            status_prominent_bg=accent.muted.s600.a50,
            shadow=fg.a05,  # soft drop shadow -- widgets float rather than bordered
            drop_bg=accent.a15,
            accent_wash=accent.a05,
            hover_bg_opaque=accent.s100,
            is_dark=False,
        )

    @classmethod
    def for_dark(cls, accent_hue: float = 262.0) -> Self:
        """Dark variant: derive all fields from accent_hue.

        Surface hierarchy (4 levels, blue-tinted H=262+180=82, C=0.015):
          L=0.300  elevated -- hover cards, command palette, notifications
                              (sits above the line-highlight overlay = editor + fg.a10 ~= L=0.28,
                              rendered via EditorChrome.caret_row -- NOT a palette field)
          L=0.220  default  -- editor, active tab, tab row, inputs
          L=0.180  subtle   -- sidebar, title bar, inactive tabs, section headers, peek view
          L=0.150  sunken   -- activity bar, status bar
          L=0.280  border_subtle -- tab separators, inner dividers
          L=0.350  border        -- widget edges, panel outlines

        Foreground hierarchy:
          L=0.83  foreground, icons (near-white)
          L=0.56  muted text (descriptions, inactive tabs, line numbers)
          L=0.40  disabled text (placeholders, ghost text)
        """
        _bg_hue = accent_hue + _SECONDARY_HUE_OFFSET  # warm tint from secondary hue

        accent_base = TCol.from_oklch(0.50, _CHROMA_VIVID, accent_hue)
        secondary_base = TCol.from_oklch(0.50, _CHROMA_VIVID, accent_hue + _SECONDARY_HUE_OFFSET)
        neutral = TCol.from_oklch(0.50, 0.0, 0.0)

        # 4-level surface hierarchy, all warm-tinted.
        # Elevated must be clearly above the line-highlight overlay (editor L=0.22 + fg.a10 ~= L=0.29)
        # so popovers don't appear darker than the line they cover.
        elevated = TCol.from_oklch(0.30, _DARK_BG_CHROMA, _bg_hue)  # hover cards, command palette
        editor_bg = TCol.from_oklch(0.22, _DARK_BG_CHROMA, _bg_hue)  # editor, inputs
        panel = TCol.from_oklch(0.18, _DARK_BG_CHROMA, _bg_hue)  # sidebar, tab row
        sunken = TCol.from_oklch(0.15, _DARK_BG_CHROMA, _bg_hue)  # activity bar, status bar
        border_val = TCol.from_oklch(0.35, _DARK_BG_CHROMA, _bg_hue)  # loud border
        border_sub = TCol.from_oklch(0.28, _DARK_BG_CHROMA, _bg_hue)  # subtle inner divider

        # Foregrounds -- light for dark bg
        fg = TCol.from_oklch(_FG_LIGHTNESS_DARK, 0.0, 0.0)

        accent = accent_base.s400
        secondary = secondary_base.s400
        error_base = TCol.from_oklch(0.50, _CHROMA_VIVID, _HUE_ERROR)
        warning_base = TCol.from_oklch(0.50, _CHROMA_VIVID, _HUE_WARNING)
        success_base = TCol.from_oklch(0.50, _CHROMA_VIVID, _HUE_SUCCESS)
        error = error_base.s400.with_min_contrast(panel, 4.6)
        warning = warning_base.s400.with_min_contrast(panel, 4.6)
        success = success_base.s400.with_min_contrast(panel, 4.6)

        return cls(
            accent=accent,
            secondary=secondary,
            error=error,
            warning=warning,
            success=success,
            surface_elevated=elevated,
            foreground=fg,
            background=editor_bg,
            panel_bg=panel,
            surface_sunken=sunken,
            border=border_val,
            border_subtle=border_sub,
            # fg_muted targets sunken (deepest chrome) for WCAG AA. Floor 4.6
            # absorbs sRGB quantization loss; see light variant.
            fg_muted=neutral.s400.with_min_contrast(sunken, 4.6),
            fg_disabled=neutral.s600,
            fg_icon=fg,
            fg_on_accent=editor_bg,
            hover_bg=accent.with_alpha(0.12),
            hover_bg_neutral=fg.with_alpha(0.06),
            selection_bg=accent.with_alpha(0.22),
            link=accent_base.s500,
            accent_hover=accent_base.s300,
            error_bg=error.a15,
            error_border=error.a50,
            warn_bg=warning.a15,
            warn_border=warning.a50,
            info_bg=accent.a15,
            info_border=accent.a50,
            gutter_add=success.a50,
            gutter_mod=accent.a50,
            gutter_del=error.a50,
            # Dark variant: line wash needs slightly more alpha to be visible
            # than on light, but still well below the text-level (a25) so word
            # diffs pop above the row.
            diff_insert_line=success.with_alpha(0.10),
            diff_remove_line=error.with_alpha(0.10),
            diff_insert=success.a25,
            diff_remove=error.a25,
            minimap_error=error.a80,
            minimap_warning=warning.a80,
            minimap_slider=fg.with_alpha(0.12),
            scrollbar_thumb=fg.a15,
            scrollbar_hover=fg.a25,
            scrollbar_active=fg.a50,
            btn_secondary_bg=neutral.s800,
            # textSeparator -- matches border_subtle for consistency with the
            # theme's divider system (see light variant rationale).
            text_separator=border_sub,
            status_prominent_bg=accent.muted.s400.a50,
            shadow=TCol.from_oklch(0.0, 0.0, 0.0).with_alpha(0.18),  # softer than before (was 0.35)
            drop_bg=accent.a25,
            accent_wash=accent.a15,
            hover_bg_opaque=accent.s800,
            is_dark=True,
        )
