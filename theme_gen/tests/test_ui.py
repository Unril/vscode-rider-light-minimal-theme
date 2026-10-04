"""Tests for UI sections and ColorMapComposition."""

import re
from collections.abc import Callable

import pytest

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.base import BaseSection
from theme_gen.ui.chat import ChatSection
from theme_gen.ui.composer import ColorMapComposition
from theme_gen.ui.debug import DebugSection
from theme_gen.ui.editor import EditorSection
from theme_gen.ui.lists import ListSection
from theme_gen.ui.panels import PanelSection
from theme_gen.ui.protocol import UISection
from theme_gen.ui.symbols import SymbolSection
from theme_gen.ui.tabs import TabSection
from theme_gen.ui.terminal import TerminalSection
from theme_gen.ui.testing import TestingSection
from theme_gen.ui.vcs import VcsSection
from theme_gen.ui.widgets import WidgetSection

ALL_SECTIONS: list[Callable[[], UISection]] = [
    BaseSection,
    ListSection,
    EditorSection,
    TabSection,
    WidgetSection,
    PanelSection,
    VcsSection,
    ChatSection,
    SymbolSection,
    TerminalSection,
    DebugSection,
    TestingSection,
]

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")

_SYMBOL_ICON_COUNT = 33
_MIN_TOTAL_COLORS = 200


@pytest.fixture
def theme() -> Theme:
    return Theme.create()


@pytest.fixture
def all_sections() -> list[UISection]:
    return [cls() for cls in ALL_SECTIONS]


@pytest.fixture
def composition(all_sections: list[UISection]) -> ColorMapComposition:
    return ColorMapComposition(all_sections)


class TestUISections:
    @pytest.mark.parametrize("section_cls", ALL_SECTIONS)
    def test_returns_dict(self, section_cls: Callable[[], UISection], theme: Theme) -> None:
        colors = section_cls().build(theme)
        assert isinstance(colors, dict)
        assert len(colors) > 0

    @pytest.mark.parametrize("section_cls", ALL_SECTIONS)
    def test_values_are_tcol(self, section_cls: Callable[[], UISection], theme: Theme) -> None:
        colors = section_cls().build(theme)
        for key, val in colors.items():
            assert isinstance(val, TCol), f"{key}: expected TCol, got {type(val)}"

    @pytest.mark.parametrize("section_cls", ALL_SECTIONS)
    def test_tcol_hex_is_valid(self, section_cls: Callable[[], UISection], theme: Theme) -> None:
        colors = section_cls().build(theme)
        for key, val in colors.items():
            assert HEX_RE.match(val.hex), f"{key}: invalid hex '{val.hex}'"

    @pytest.mark.parametrize("section_cls", ALL_SECTIONS)
    def test_keys_are_dotted_strings(self, section_cls: Callable[[], UISection], theme: Theme) -> None:
        colors = section_cls().build(theme)
        for key in colors:
            assert isinstance(key, str)
            assert len(key) > 0

    def test_symbol_section_has_13_icons(self, theme: Theme) -> None:
        colors = SymbolSection().build(theme)
        assert len(colors) == _SYMBOL_ICON_COUNT


class TestColorMapComposition:
    def test_build_returns_dict(self, composition: ColorMapComposition, theme: Theme) -> None:
        colors = composition.build(theme)
        assert isinstance(colors, dict)

    def test_total_key_count_reasonable(self, composition: ColorMapComposition, theme: Theme) -> None:
        colors = composition.build(theme)
        assert len(colors) >= _MIN_TOTAL_COLORS

    def test_all_values_are_tcol(self, composition: ColorMapComposition, theme: Theme) -> None:
        colors = composition.build(theme)
        for key, val in colors.items():
            assert isinstance(val, TCol), f"{key}: expected TCol"

    def test_all_hex_values_valid(self, composition: ColorMapComposition, theme: Theme) -> None:
        colors = composition.build(theme)
        for key, val in colors.items():
            assert HEX_RE.match(val.hex), f"{key}: invalid hex '{val.hex}'"

    def test_build_returns_non_empty(self, composition: ColorMapComposition, theme: Theme) -> None:
        colors = composition.build(theme)
        assert len(colors) > 0

    def test_detects_duplicate_keys(self, theme: Theme) -> None:
        class DuplicateSection:
            def build(
                self,
                theme: Theme,  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
            ) -> dict[str, TCol]:
                return {"foreground": TCol("#000000")}

        comp = ColorMapComposition([BaseSection(), DuplicateSection()])
        with pytest.raises(ValueError, match="Duplicate color key"):
            _ = comp.build(theme)

    def test_required_root_keys_present(self, composition: ColorMapComposition, theme: Theme) -> None:
        colors = composition.build(theme)
        for key in [
            "foreground",
            "editor.background",
            "editor.foreground",
            "statusBar.background",
            "titleBar.activeBackground",
        ]:
            assert key in colors, f"Missing required key: {key}"


class TestTerminalDark:
    def test_terminal_section_builds_with_dark_theme(self) -> None:
        dark_theme = Theme.create(is_dark=True)
        colors = TerminalSection().build(dark_theme)
        assert isinstance(colors, dict)
        assert len(colors) > 0

    def test_all_ansi_colors_valid_hex(self) -> None:
        dark_theme = Theme.create(is_dark=True)
        colors = TerminalSection().build(dark_theme)
        ansi_keys = [k for k in colors if k.startswith("terminal.ansi")]
        assert len(ansi_keys) == 16  # noqa: PLR2004
        for key in ansi_keys:
            assert isinstance(colors[key], TCol)
            assert HEX_RE.match(colors[key].hex), f"{key}: invalid hex '{colors[key].hex}'"
