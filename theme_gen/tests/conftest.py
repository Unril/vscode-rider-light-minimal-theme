"""Shared test fixtures and helpers."""

from typing import TYPE_CHECKING

import pytest

from lang.base import BaseSyntax
from lang.csharp import CSharpLang
from lang.css import CssLang
from lang.html import HtmlLang
from lang.java import JavaLang
from lang.js import JavaScriptLang
from lang.json_lang import JsonLang
from lang.kotlin import KotlinLang
from lang.markdown import MarkdownLang
from lang.python import PythonLang
from lang.registry import LanguageRegistry
from lang.script import ScriptLang
from lang.semantic import GlobalSemanticTokens
from lang.ts import TypeScriptLang
from lang.yaml import YamlLang
from palette.theme import Theme
from ui.base import BaseSection
from ui.chat import ChatSection
from ui.composer import ColorMapComposition
from ui.debug import DebugSection
from ui.editor import EditorSection
from ui.lists import ListSection
from ui.panels import PanelSection
from ui.symbols import SymbolSection
from ui.tabs import TabSection
from ui.terminal import TerminalSection
from ui.testing import TestingSection
from ui.vcs import VcsSection
from ui.widgets import WidgetSection

if TYPE_CHECKING:
    from collections.abc import Callable

    from lang.protocol import Language


def generate_theme_dict(*, is_dark: bool = False) -> dict[str, object]:
    """Full generation pipeline matching main.py -- single source of truth for tests."""
    theme = Theme.create(is_dark=is_dark)

    composition = ColorMapComposition(
        [
            BaseSection(),
            ListSection(),
            EditorSection(),
            TabSection(),
            WidgetSection(),
            PanelSection(),
            VcsSection(),
            ChatSection(),
            SymbolSection(),
            TerminalSection(),
            DebugSection(),
            TestingSection(),
        ],
    )
    colors = {k: v.hex for k, v in composition.build(theme).items()}

    registry = LanguageRegistry(GlobalSemanticTokens(theme.syntax))
    lang_factories: list[Callable[[], Language]] = [
        BaseSyntax,
        JavaLang,
        KotlinLang,
        CSharpLang,
        PythonLang,
        JavaScriptLang,
        TypeScriptLang,
        CssLang,
        HtmlLang,
        MarkdownLang,
        YamlLang,
        JsonLang,
        ScriptLang,
    ]
    for lang_cls in lang_factories:
        registry.register(lang_cls())

    token_colors = [rule.to_dict() for rule in registry.build_token_colors(theme)]
    semantic_tokens = registry.build_semantic_tokens(theme)

    name = "Rider Light Minimal Dark" if is_dark else "Rider Light Minimal"
    theme_type = "dark" if is_dark else "light"

    return {
        "$schema": "vscode://schemas/color-theme",
        "name": name,
        "type": theme_type,
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
        "semanticTokenColors": semantic_tokens,
    }


@pytest.fixture(scope="session")
def theme_output() -> dict[str, object]:
    """Session-scoped fixture: full light theme dict generated once per test run."""
    return generate_theme_dict()


@pytest.fixture(scope="session")
def dark_theme_output() -> dict[str, object]:
    """Session-scoped fixture: full dark theme dict generated once per test run."""
    return generate_theme_dict(is_dark=True)
