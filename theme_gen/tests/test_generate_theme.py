"""Structural validation test -- verifies the full generation pipeline produces valid output."""

# pylint: disable=redefined-outer-name

import json
import re
from typing import cast

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")


_COLOR_COUNT_MIN = 200
_COLOR_COUNT_MAX = 600
_TOKEN_COLOR_COUNT_MIN = 70
_SEMANTIC_TOKEN_COUNT_MIN = 55


class TestThemeStructure:
    def test_has_required_top_level_keys(self, theme_output: dict[str, object]) -> None:
        for key in [
            "$schema",
            "name",
            "type",
            "semanticHighlighting",
            "colors",
            "tokenColors",
            "semanticTokenColors",
        ]:
            assert key in theme_output, f"Missing top-level key: {key}"

    def test_schema_value(self, theme_output: dict[str, object]) -> None:
        assert theme_output["$schema"] == "vscode://schemas/color-theme"

    def test_type_is_light(self, theme_output: dict[str, object]) -> None:
        assert theme_output["type"] == "light"

    def test_semantic_highlighting_enabled(self, theme_output: dict[str, object]) -> None:
        assert theme_output["semanticHighlighting"] is True

    def test_colors_are_hex_strings(self, theme_output: dict[str, object]) -> None:
        colors = cast("dict[str, str]", theme_output["colors"])
        for key, val in colors.items():
            assert HEX_RE.match(val), f"colors[{key}]: invalid hex '{val}'"

    def test_token_colors_structure(self, theme_output: dict[str, object]) -> None:
        token_colors = cast("list[dict[str, object]]", theme_output["tokenColors"])
        for entry in token_colors:
            assert "name" in entry
            assert "scope" in entry or "settings" in entry
            if "settings" in entry:
                settings = cast("dict[str, str]", entry["settings"])
                for k in settings:
                    assert k in ("foreground", "fontStyle")

    def test_semantic_token_values(self, theme_output: dict[str, object]) -> None:
        sem = cast("dict[str, str | dict[str, str]]", theme_output["semanticTokenColors"])
        for key, val in sem.items():
            if isinstance(val, str):
                assert HEX_RE.match(val), f"semantic[{key}]: invalid hex"
            else:
                assert "foreground" in val
                assert HEX_RE.match(val["foreground"])

    def test_json_serializable(self, theme_output: dict[str, object]) -> None:
        text = json.dumps(theme_output, indent=2)
        parsed = cast("dict[str, object]", json.loads(text))
        assert parsed["name"] == "Rider Light Minimal"

    def test_color_count_in_range(self, theme_output: dict[str, object]) -> None:
        colors = cast("dict[str, str]", theme_output["colors"])
        count = len(colors)
        assert _COLOR_COUNT_MIN <= count <= _COLOR_COUNT_MAX, f"Color count {count} outside expected range"

    def test_token_color_count(self, theme_output: dict[str, object]) -> None:
        token_colors = cast("list[dict[str, object]]", theme_output["tokenColors"])
        count = len(token_colors)
        assert count >= _TOKEN_COLOR_COUNT_MIN, f"Only {count} tokenColors"

    def test_semantic_token_count(self, theme_output: dict[str, object]) -> None:
        sem = cast("dict[str, object]", theme_output["semanticTokenColors"])
        count = len(sem)
        assert count >= _SEMANTIC_TOKEN_COUNT_MIN, f"Only {count} semanticTokenColors"

    class TestDarkThemeStructure:
        """Structural validation for the dark theme variant."""

        def test_has_required_top_level_keys(self, dark_theme_output: dict[str, object]) -> None:
            for key in [
                "$schema",
                "name",
                "type",
                "semanticHighlighting",
                "colors",
                "tokenColors",
                "semanticTokenColors",
            ]:
                assert key in dark_theme_output, f"Missing top-level key: {key}"

        def test_type_is_dark(self, dark_theme_output: dict[str, object]) -> None:
            assert dark_theme_output["type"] == "dark"

        def test_name_is_dark(self, dark_theme_output: dict[str, object]) -> None:
            assert dark_theme_output["name"] == "Rider Light Minimal Dark"

        def test_colors_are_hex_strings(self, dark_theme_output: dict[str, object]) -> None:
            colors = cast("dict[str, str]", dark_theme_output["colors"])
            for key, val in colors.items():
                assert HEX_RE.match(val), f"colors[{key}]: invalid hex '{val}'"

        def test_color_count_in_range(self, dark_theme_output: dict[str, object]) -> None:
            colors = cast("dict[str, str]", dark_theme_output["colors"])
            count = len(colors)
            assert _COLOR_COUNT_MIN <= count <= _COLOR_COUNT_MAX, f"Color count {count} outside expected range"

        def test_token_color_count(self, dark_theme_output: dict[str, object]) -> None:
            token_colors = cast("list[dict[str, object]]", dark_theme_output["tokenColors"])
            assert len(token_colors) >= _TOKEN_COLOR_COUNT_MIN

        def test_semantic_token_count(self, dark_theme_output: dict[str, object]) -> None:
            sem = cast("dict[str, object]", dark_theme_output["semanticTokenColors"])
            assert len(sem) >= _SEMANTIC_TOKEN_COUNT_MIN

        def test_json_serializable(self, dark_theme_output: dict[str, object]) -> None:
            text = json.dumps(dark_theme_output, indent=2)
            parsed = cast("dict[str, object]", json.loads(text))
            assert parsed["name"] == "Rider Light Minimal Dark"
