"""Theme -> VS Code color theme document.

The single generation path for `uv run -m theme_gen` and the tests.
"""

from collections.abc import Callable
from typing import TypedDict

from theme_gen.lang.base import BaseSyntax
from theme_gen.lang.csharp import CSharpLang
from theme_gen.lang.css import CssLang
from theme_gen.lang.html import HtmlLang
from theme_gen.lang.java import JavaLang
from theme_gen.lang.js import JavaScriptLang
from theme_gen.lang.json_lang import JsonLang
from theme_gen.lang.kotlin import KotlinLang
from theme_gen.lang.markdown import MarkdownLang
from theme_gen.lang.protocol import Language
from theme_gen.lang.python import PythonLang
from theme_gen.lang.registry import LanguageRegistry
from theme_gen.lang.script import ScriptLang
from theme_gen.lang.semantic import GlobalSemanticTokens
from theme_gen.lang.ts import TypeScriptLang
from theme_gen.lang.yaml import YamlLang
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

# Functional form because `$schema` is not an identifier.
ThemeDocument = TypedDict(
    "ThemeDocument",
    {
        "$schema": str,
        "name": str,
        "type": str,
        "semanticHighlighting": bool,
        "colors": dict[str, str],
        "tokenColors": list[dict[str, object]],
        "semanticTokenColors": dict[str, str | dict[str, str]],
    },
)

# Order matters: BaseSyntax first, then per-language overrides (TextMate is last-match-wins; see LanguageRegistry).
_LANGUAGES: tuple[Callable[[], Language], ...] = (
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
)

_UI_SECTIONS: tuple[Callable[[], UISection], ...] = (
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
)


def build_theme_document(*, is_dark: bool) -> ThemeDocument:
    theme = Theme.create(is_dark=is_dark)

    composition = ColorMapComposition([cls() for cls in _UI_SECTIONS])
    colors = {k: v.hex for k, v in composition.build(theme).items()}

    registry = LanguageRegistry(GlobalSemanticTokens(theme.syntax))
    for lang_cls in _LANGUAGES:
        registry.register(lang_cls())

    return {
        "$schema": "vscode://schemas/color-theme",
        "name": "Rider Light Minimal Dark" if is_dark else "Rider Light Minimal",
        "type": "dark" if is_dark else "light",
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": [rule.to_dict() for rule in registry.build_token_colors(theme)],
        "semanticTokenColors": registry.build_semantic_tokens(theme),
    }
