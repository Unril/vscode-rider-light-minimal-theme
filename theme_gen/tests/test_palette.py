"""Tests for TCol ramp steps and Palette."""

from core.tcol import TCol
from palette.palette import Palette

_RAMP_STEP_COUNT = 9
_ACHROMATIC_CHROMA_MAX = 0.01


_CHROMA_TOLERANCE = 0.02
_HUE_TOLERANCE = 2.0


_BG_MIN_LIGHTNESS = 0.99  # light variant bg should be near-white
_BG_MAX_CHROMA = 0.01  # light variant bg is imperceptibly tinted

_FG_MAX_LIGHTNESS = 0.36
_WCAG_AA_FLOOR = 4.5
_DARK_BG_MAX_LIGHTNESS = 0.3
_FG_DARK_MIN_LIGHTNESS = 0.7


class TestTColRampSteps:
    def test_produces_9_steps(self) -> None:
        c = TCol.from_oklch(0.50, 0.14, 262.0)
        steps = [c.s100, c.s200, c.s300, c.s400, c.s500, c.s600, c.s700, c.s800, c.s900]
        assert len(steps) == _RAMP_STEP_COUNT

    def test_lightness_decreases(self) -> None:
        c = TCol.from_oklch(0.50, 0.14, 262.0)
        steps = [c.s100, c.s200, c.s300, c.s400, c.s500, c.s600, c.s700, c.s800, c.s900]
        for i in range(len(steps) - 1):
            assert steps[i].lightness > steps[i + 1].lightness

    def test_all_steps_are_tcol(self) -> None:
        c = TCol.from_oklch(0.50, 0.10, 120.0)
        for attr in [
            "s100",
            "s200",
            "s300",
            "s400",
            "s500",
            "s600",
            "s700",
            "s800",
            "s900",
        ]:
            assert isinstance(getattr(c, attr), TCol)

    def test_achromatic_ramp(self) -> None:
        c = TCol.from_oklch(0.50, 0.0, 0.0)
        assert c.s500.c < _ACHROMATIC_CHROMA_MAX

    def test_preserves_hue_and_scales_chroma(self) -> None:
        c = TCol.from_oklch(0.50, 0.14, 262.0)
        step = c.s300
        # Hue preserved
        assert abs(step.h - 262.0) < _HUE_TOLERANCE
        # Chroma scaled down (s300 scale = 0.48)
        assert step.c < c.c
        assert step.c > 0.0


class TestPalette:
    def test_for_light_produces_valid_fields(self) -> None:
        p = Palette.for_light()
        assert isinstance(p.accent, TCol)
        assert isinstance(p.error, TCol)
        assert isinstance(p.warning, TCol)
        assert isinstance(p.success, TCol)
        assert isinstance(p.foreground, TCol)
        assert isinstance(p.background, TCol)
        assert isinstance(p.panel_bg, TCol)
        assert isinstance(p.border, TCol)
        assert isinstance(p.fg_muted, TCol)
        assert isinstance(p.fg_disabled, TCol)
        assert isinstance(p.fg_icon, TCol)
        assert isinstance(p.fg_on_accent, TCol)
        assert isinstance(p.shadow, TCol)
        assert isinstance(p.hover_bg, TCol)
        assert isinstance(p.selection_bg, TCol)

    def test_for_light_background_is_warm_off_white(self) -> None:
        p = Palette.for_light()
        # Not pure white -- a small warm yellow tint at hue 85.
        # Imperceptible as "colored" but avoids the blue-screen glow of #FFFFFF.
        assert p.background.lightness > _BG_MIN_LIGHTNESS
        assert p.background.c < _BG_MAX_CHROMA
        # Near-white: first two hex channels reach 0xFE or 0xFF. Specific values
        # depend on sRGB gamut projection at whatever chroma we settle on.
        assert p.background.hex.startswith(("#FF", "#FE"))

    def test_surface_hierarchy(self) -> None:
        p = Palette.for_light()
        # elevated > default > subtle > sunken
        assert p.surface_elevated.lightness >= p.background.lightness
        assert p.background.lightness > p.panel_bg.lightness > p.surface_sunken.lightness

    def test_for_light_foreground_is_dark_grey(self) -> None:
        p = Palette.for_light()
        assert p.foreground.lightness < _FG_MAX_LIGHTNESS

    def test_hover_bg_is_distinct_from_panel(self) -> None:
        p = Palette.for_light()
        assert p.hover_bg.lightness < p.panel_bg.lightness

    def test_selection_bg_is_darker_than_panel(self) -> None:
        p = Palette.for_light()
        assert p.selection_bg.lightness < p.panel_bg.lightness

    def test_for_dark_produces_valid_fields(self) -> None:
        p = Palette.for_dark()
        assert isinstance(p.accent, TCol)
        assert isinstance(p.error, TCol)
        assert isinstance(p.foreground, TCol)
        assert isinstance(p.background, TCol)
        assert isinstance(p.panel_bg, TCol)
        assert isinstance(p.shadow, TCol)

    def test_for_dark_background_is_dark(self) -> None:
        p = Palette.for_dark()
        assert p.background.lightness < _DARK_BG_MAX_LIGHTNESS

    def test_for_dark_foreground_is_light(self) -> None:
        p = Palette.for_dark()
        assert p.foreground.lightness > _FG_DARK_MIN_LIGHTNESS

    def test_for_dark_accent_contrast(self) -> None:
        p = Palette.for_dark()
        assert p.accent.contrast(p.background) >= _WCAG_AA_FLOOR

    def test_for_dark_panel_darker_than_editor(self) -> None:
        p = Palette.for_dark()
        assert p.panel_bg.lightness < p.background.lightness

    def test_for_dark_derived_alpha_fields(self) -> None:
        p = Palette.for_dark()
        assert p.gutter_add.a < 1.0
        assert p.diff_insert.a < 1.0
        assert p.error_bg.a < 1.0
        assert p.scrollbar_thumb.a < 1.0

    def test_neutral_derived_fields(self) -> None:
        p = Palette.for_light()
        assert isinstance(p.btn_secondary_bg, TCol)
        assert isinstance(p.scrollbar_thumb, TCol)

    def test_derived_alpha_fields(self) -> None:
        p = Palette.for_light()
        assert p.gutter_add.a < 1.0
        assert p.diff_insert.a < 1.0
        assert p.error_bg.a < 1.0
        assert p.scrollbar_thumb.a < 1.0
