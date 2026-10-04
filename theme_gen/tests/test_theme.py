"""Tests for SyntaxPalette, EditorPalette, and Theme."""

from dataclasses import fields as dc_fields
from typing import cast

import pytest
from coloraide import Color

from theme_gen.core.tcol import TCol
from theme_gen.palette.editor import (
    EditorChrome,
    EditorPalette,
    OutputColors,
    SelectionColors,
    SymbolColors,
    WidgetColors,
)
from theme_gen.palette.palette import Palette
from theme_gen.palette.syntax import SyntaxPalette
from theme_gen.palette.theme import Theme

_WCAG_AA = 4.5
_WCAG_AA_TOLERANCE = 4.4
_SEMANTIC_MIN = 4.5
_LAB_L_TOLERANCE = 0.5  # Lab L* precision after sRGB gamut mapping and hex rounding
_FG_LIGHT_MIN = 0.7  # dark-variant foreground must be lighter than this
_HUE_WRAP = 180  # half-circle for shortest-arc hue comparison
_HUE_DRIFT_MAX = 5.0  # max acceptable hue drift between light and dark variants
_ALPHA_OPAQUE_MIN = 0.5  # colors with alpha below this are transparent overlays
_LIGHTNESS_RANGE_MIN = 0.10  # dark editor palette: minimum acceptable lightness
_LIGHTNESS_RANGE_MAX = 0.95  # dark editor palette: maximum acceptable lightness
_DARK_BG_MAX_LIGHTNESS = 0.3  # dark palette background must be darker than this
_CONTRAST_TOLERANCE = 1e-4  # brentq precision for contrast floor
_CHROMA_TOLERANCE = 0.01  # acceptable chroma drift after darkening


class TestTColFromLabL:
    """TCol.from_lab_l: create a TCol at the OkLCh L that achieves a target CIELab L*."""

    def _actual_lab_l(self, col: TCol) -> float:
        return Color(col.hex).convert("lab-d65").get("lightness")

    def test_achieves_target_lab_l_for_blue_hue(self) -> None:
        col = TCol.from_lab_l(44.0, 0.25, 265.0)
        assert abs(self._actual_lab_l(col) - 44.0) < _LAB_L_TOLERANCE

    def test_achieves_target_lab_l_for_purple_hue(self) -> None:
        col = TCol.from_lab_l(34.0, 0.25, 310.0)
        assert abs(self._actual_lab_l(col) - 34.0) < _LAB_L_TOLERANCE

    def test_achieves_target_lab_l_for_brown_hue(self) -> None:
        col = TCol.from_lab_l(54.0, 0.08, 40.0)
        assert abs(self._actual_lab_l(col) - 54.0) < _LAB_L_TOLERANCE

    def test_returns_tcol_instance(self) -> None:
        col = TCol.from_lab_l(44.0, 0.12, 175.0)
        assert isinstance(col, TCol)

    def test_oklch_l_is_in_valid_range(self) -> None:
        col = TCol.from_lab_l(44.0, 0.12, 175.0)
        assert 0.0 <= col.lightness <= 1.0

    @pytest.mark.parametrize("hue", [40.0, 85.0, 130.0, 175.0, 220.0, 265.0, 310.0, 355.0])
    def test_all_cluster_hues_achieve_mid_tier_target(self, hue: float) -> None:
        col = TCol.from_lab_l(44.0, 0.12, hue)
        assert abs(self._actual_lab_l(col) - 44.0) < _LAB_L_TOLERANCE

    def test_higher_target_produces_higher_oklch_l(self) -> None:
        bright = TCol.from_lab_l(54.0, 0.12, 265.0)
        dark = TCol.from_lab_l(34.0, 0.12, 265.0)
        assert bright.lightness > dark.lightness

    def test_achromatic_color_achieves_target(self) -> None:
        col = TCol.from_lab_l(44.0, 0.0, 0.0)
        assert abs(self._actual_lab_l(col) - 44.0) < _LAB_L_TOLERANCE


class TestTColWithMinContrast:
    """TCol.with_min_contrast: darken a color until it meets a contrast floor."""

    _BG: TCol = TCol.from_hex("#FFFFFF")

    def test_returns_self_when_already_passes(self) -> None:
        dark = TCol.from_oklch(0.40, 0.25, 265.0)
        assert dark.contrast(self._BG) > _WCAG_AA
        result = dark.with_min_contrast(self._BG, _WCAG_AA)
        assert result == dark

    def test_darkens_to_meet_wcag_aa_floor(self) -> None:
        light = TCol.from_oklch(0.70, 0.12, 175.0)
        assert light.contrast(self._BG) < _WCAG_AA
        result = light.with_min_contrast(self._BG, _WCAG_AA)
        assert result.contrast(self._BG) >= _WCAG_AA - _CONTRAST_TOLERANCE

    def test_darkens_to_meet_semantic_floor(self) -> None:
        light = TCol.from_oklch(0.70, 0.12, 175.0)
        result = light.with_min_contrast(self._BG, _SEMANTIC_MIN)
        assert result.contrast(self._BG) >= _SEMANTIC_MIN - _CONTRAST_TOLERANCE

    def test_contrast_is_exact_not_over_darkened(self) -> None:
        light = TCol.from_oklch(0.70, 0.12, 175.0)
        result = light.with_min_contrast(self._BG, _WCAG_AA)
        assert result.contrast(self._BG) < _WCAG_AA + 0.05

    def test_preserves_hue(self) -> None:
        light = TCol.from_oklch(0.70, 0.12, 175.0)
        result = light.with_min_contrast(self._BG, _WCAG_AA)
        assert abs(result.h - 175.0) < 1.0

    def test_preserves_chroma(self) -> None:
        light = TCol.from_oklch(0.70, 0.12, 175.0)
        result = light.with_min_contrast(self._BG, _WCAG_AA)
        assert abs(result.c - 0.12) < _CHROMA_TOLERANCE

    def test_zero_floor_returns_self_unchanged(self) -> None:
        col = TCol.from_oklch(0.80, 0.12, 175.0)
        result = col.with_min_contrast(self._BG, 0.0)
        assert result == col

    def test_result_is_darker_than_input(self) -> None:
        light = TCol.from_oklch(0.70, 0.12, 175.0)
        result = light.with_min_contrast(self._BG, _WCAG_AA)
        assert result.lightness < light.lightness

    class TestTColWithMinContrastDark:
        """TCol.with_min_contrast on a dark background: lightens to meet contrast floor."""

        _BG: TCol = TCol.from_oklch(0.20, 0.015, 260.0)

        def test_returns_self_when_already_passes(self) -> None:
            light = TCol.from_oklch(0.80, 0.12, 175.0)
            assert light.contrast(self._BG) > _WCAG_AA
            result = light.with_min_contrast(self._BG, _WCAG_AA)
            assert result == light

        def test_lightens_to_meet_wcag_aa_floor(self) -> None:
            dark = TCol.from_oklch(0.30, 0.12, 175.0)
            assert dark.contrast(self._BG) < _WCAG_AA
            result = dark.with_min_contrast(self._BG, _WCAG_AA)
            assert result.contrast(self._BG) >= _WCAG_AA - _CONTRAST_TOLERANCE

        def test_contrast_is_exact_not_over_lightened(self) -> None:
            dark = TCol.from_oklch(0.30, 0.12, 175.0)
            result = dark.with_min_contrast(self._BG, _WCAG_AA)
            assert result.contrast(self._BG) < _WCAG_AA + 0.05

        def test_preserves_hue(self) -> None:
            dark = TCol.from_oklch(0.30, 0.12, 175.0)
            result = dark.with_min_contrast(self._BG, _WCAG_AA)
            assert abs(result.h - 175.0) < 1.0

        def test_preserves_chroma(self) -> None:
            dark = TCol.from_oklch(0.30, 0.12, 175.0)
            result = dark.with_min_contrast(self._BG, _WCAG_AA)
            assert abs(result.c - 0.12) < _CHROMA_TOLERANCE

        def test_result_is_lighter_than_input(self) -> None:
            dark = TCol.from_oklch(0.30, 0.12, 175.0)
            result = dark.with_min_contrast(self._BG, _WCAG_AA)
            assert result.lightness > dark.lightness

        def test_zero_floor_returns_self_unchanged(self) -> None:
            col = TCol.from_oklch(0.30, 0.12, 175.0)
            result = col.with_min_contrast(self._BG, 0.0)
            assert result == col


class TestSyntaxPalette:
    def test_create_produces_all_roles(self) -> None:
        bg = TCol.from_hex("#FFFFFF")
        sp = SyntaxPalette.create(background=bg)
        roles = [
            "keyword",
            "control",
            "type",
            "function",
            "string",
            "number",
            "comment",
            "function_decl",
            "namespace",
            "field",
            "field_const",
            "escape",
            "metadata",
            "enum_member",
            "param",
            "punct",
            "deprecated",
        ]
        for role in roles:
            assert isinstance(getattr(sp, role), TCol)

    def test_wcag_aa_contrast(self) -> None:
        """Structural roles must meet WCAG AA (4.5:1); semantic roles meet 3.0:1."""
        bg = TCol.from_hex("#FFFFFF")
        sp = SyntaxPalette.create(background=bg)

        def _check(color: TCol, role: str, floor: float) -> None:
            ratio = color.contrast(bg)
            assert ratio >= floor, f"{role} contrast {ratio:.2f} < {floor}"

        # Structural roles: WCAG AA required
        _check(sp.keyword, "keyword", _WCAG_AA_TOLERANCE)
        _check(sp.control, "control", _WCAG_AA_TOLERANCE)
        _check(sp.type, "type", _WCAG_AA_TOLERANCE)
        _check(sp.namespace, "namespace", _WCAG_AA_TOLERANCE)
        _check(sp.escape, "escape", _WCAG_AA_TOLERANCE)
        _check(sp.param, "param", _WCAG_AA_TOLERANCE)
        _check(sp.punct, "punct", _WCAG_AA_TOLERANCE)
        # Semantic color roles: 3.0:1 minimum
        _check(sp.function, "function", _SEMANTIC_MIN)
        _check(sp.field, "field", _SEMANTIC_MIN)
        _check(sp.comment, "comment", _SEMANTIC_MIN)
        _check(sp.string, "string", _SEMANTIC_MIN)
        _check(sp.metadata, "metadata", _SEMANTIC_MIN)
        _check(sp.number, "number", _SEMANTIC_MIN)
        _check(sp.enum_member, "enum_member", _SEMANTIC_MIN)
        _check(sp.deprecated, "deprecated", _SEMANTIC_MIN)

    def test_foreground_and_background(self) -> None:
        bg = TCol.from_hex("#FFFFFF")
        sp = SyntaxPalette.create(background=bg)
        assert sp.background.hex == "#FFFFFF"
        assert sp.foreground.hex == "#000000"


class TestSyntaxPaletteDark:
    _DARK_BG: TCol = TCol.from_oklch(0.25, 0.018, 82.0)

    def test_create_produces_all_roles(self) -> None:
        sp = SyntaxPalette.create(background=self._DARK_BG, is_dark=True)
        roles = [
            "keyword",
            "control",
            "type",
            "function",
            "string",
            "number",
            "comment",
            "function_decl",
            "namespace",
            "field",
            "field_const",
            "escape",
            "metadata",
            "enum_member",
            "param",
            "punct",
            "deprecated",
        ]
        for role in roles:
            assert isinstance(getattr(sp, role), TCol)

    def test_wcag_aa_contrast_on_dark_bg(self) -> None:
        sp = SyntaxPalette.create(background=self._DARK_BG, is_dark=True)
        for role in [
            "keyword",
            "control",
            "type",
            "namespace",
            "escape",
            "param",
            "punct",
            "function",
            "field",
            "comment",
            "string",
            "metadata",
            "number",
            "enum_member",
            "deprecated",
        ]:
            color = cast("TCol", getattr(sp, role))
            ratio: float = color.contrast(self._DARK_BG)
            assert ratio >= _WCAG_AA_TOLERANCE, f"{role} contrast {ratio:.2f} < {_WCAG_AA_TOLERANCE}"

    def test_foreground_is_light(self) -> None:
        sp = SyntaxPalette.create(background=self._DARK_BG, is_dark=True)
        assert sp.foreground.lightness > _FG_LIGHT_MIN

    def test_same_hues_as_light(self) -> None:
        light_sp = SyntaxPalette.create(background=TCol.from_hex("#FFFFFF"))
        dark_sp = SyntaxPalette.create(background=self._DARK_BG, is_dark=True)
        for role in ["keyword", "type", "function", "string", "number", "comment", "field", "metadata"]:
            light_col = cast("TCol", getattr(light_sp, role))
            dark_col = cast("TCol", getattr(dark_sp, role))
            diff = abs(light_col.h - dark_col.h) % 360
            if diff > _HUE_WRAP:
                diff = 360 - diff
            assert diff < _HUE_DRIFT_MAX, f"{role} hue drift: light={light_col.h:.1f} dark={dark_col.h:.1f}"


class TestEditorPalette:
    def test_create_produces_all_fields(self) -> None:
        bg = TCol.from_hex("#FFFFFF")
        sp = SyntaxPalette.create(background=bg)
        p = Palette.for_light()
        ep = EditorPalette.create(sp, p)
        assert isinstance(ep.chrome.caret, TCol)
        assert isinstance(ep.selection.primary, TCol)
        assert isinstance(ep.symbols.cls, TCol)
        assert isinstance(ep.output.error, TCol)

    def test_symbol_colors_from_syntax(self) -> None:
        bg = TCol.from_hex("#FFFFFF")
        sp = SyntaxPalette.create(background=bg)
        p = Palette.for_light()
        ep = EditorPalette.create(sp, p)
        assert ep.symbols.cls == sp.type
        assert ep.symbols.function == sp.function


class TestEditorPaletteDark:
    def test_create_produces_all_fields(self) -> None:
        t = Theme.create(is_dark=True)
        ep = t.editor
        assert isinstance(ep.chrome.caret, TCol)
        assert isinstance(ep.selection.primary, TCol)
        assert isinstance(ep.symbols.cls, TCol)
        assert isinstance(ep.output.error, TCol)

    def test_all_opaque_colors_in_lightness_range(self) -> None:
        t = Theme.create(is_dark=True)
        ep = t.editor
        sub_palettes: list[tuple[str, SymbolColors | OutputColors | EditorChrome | SelectionColors | WidgetColors]] = [
            ("symbols", ep.symbols),
            ("output", ep.output),
            ("chrome", ep.chrome),
            ("selection", ep.selection),
            ("widgets", ep.widgets),
        ]
        for sub_name, sub in sub_palettes:
            for f in dc_fields(sub):
                col = cast("TCol", getattr(sub, f.name))
                if col.a < _ALPHA_OPAQUE_MIN:
                    continue
                assert _LIGHTNESS_RANGE_MIN <= col.lightness <= _LIGHTNESS_RANGE_MAX, (
                    f"{sub_name}.{f.name}: L={col.lightness:.3f} out of range"
                )


class TestAnsiColors:
    def test_neutral_ramp_is_ordered_in_both_variants(self) -> None:
        for is_dark in (False, True):
            ansi = Theme.create(is_dark=is_dark).editor.ansi
            assert ansi.bright_white.lightness > ansi.white.lightness > ansi.bright_black.lightness

    def test_black_sits_on_the_variant_side_of_the_terminal_background(self) -> None:
        light, dark = Theme.create(is_dark=False), Theme.create(is_dark=True)
        assert light.editor.ansi.black.lightness < light.palette.background.lightness
        # Dark: ANSI black must sit ABOVE the terminal background or dim CLI output vanishes.
        assert dark.editor.ansi.black.lightness > dark.palette.background.lightness


class TestTheme:
    def test_create_produces_valid_theme(self) -> None:
        t = Theme.create()
        assert isinstance(t.palette, Palette)
        assert isinstance(t.syntax, SyntaxPalette)
        assert isinstance(t.editor, EditorPalette)
        assert t.is_dark is False

    def test_create_dark_produces_valid_theme(self) -> None:
        t = Theme.create(is_dark=True)
        assert isinstance(t.palette, Palette)
        assert isinstance(t.syntax, SyntaxPalette)
        assert isinstance(t.editor, EditorPalette)
        assert t.is_dark is True

    def test_dark_palette_background_is_dark(self) -> None:
        t = Theme.create(is_dark=True)
        assert t.palette.background.lightness < _DARK_BG_MAX_LIGHTNESS

    def test_dark_syntax_roles_pass_wcag_aa(self) -> None:
        t = Theme.create(is_dark=True)
        bg = t.syntax.background

        def _check(color: TCol, role: str, floor: float) -> None:
            assert color.contrast(bg) >= floor, f"{role} contrast below {floor}:1"

        _check(t.syntax.keyword, "keyword", _WCAG_AA)
        _check(t.syntax.type, "type", _WCAG_AA)
        _check(t.syntax.param, "param", _WCAG_AA)
        _check(t.syntax.punct, "punct", _WCAG_AA)
        _check(t.syntax.function, "function", _SEMANTIC_MIN)
        _check(t.syntax.field, "field", _SEMANTIC_MIN)
        _check(t.syntax.string, "string", _SEMANTIC_MIN)
        _check(t.syntax.comment, "comment", _SEMANTIC_MIN)
        _check(t.syntax.number, "number", _SEMANTIC_MIN)

    def test_syntax_roles_pass_wcag_aa(self) -> None:
        t = Theme.create()
        bg = t.syntax.background

        def _check(color: TCol, role: str, floor: float) -> None:
            assert color.contrast(bg) >= floor, f"{role} contrast below {floor}:1"

        _check(t.syntax.keyword, "keyword", _WCAG_AA)
        _check(t.syntax.type, "type", _WCAG_AA)
        _check(t.syntax.param, "param", _WCAG_AA)
        _check(t.syntax.punct, "punct", _WCAG_AA)
        _check(t.syntax.function, "function", _SEMANTIC_MIN)
        _check(t.syntax.field, "field", _SEMANTIC_MIN)
        _check(t.syntax.string, "string", _SEMANTIC_MIN)
        _check(t.syntax.comment, "comment", _SEMANTIC_MIN)
        _check(t.syntax.number, "number", _SEMANTIC_MIN)
