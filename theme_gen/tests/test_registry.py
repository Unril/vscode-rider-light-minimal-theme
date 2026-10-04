"""Tests for LanguageRegistry and per-language classes."""

from collections.abc import Callable
from typing import override

import pytest

from theme_gen.core.tcol import TCol
from theme_gen.lang.base import BaseSyntax
from theme_gen.lang.css import CssLang
from theme_gen.lang.html import HtmlLang
from theme_gen.lang.java import JavaLang
from theme_gen.lang.js import JavaScriptLang
from theme_gen.lang.json_lang import JsonLang
from theme_gen.lang.kotlin import KotlinLang
from theme_gen.lang.markdown import MarkdownLang
from theme_gen.lang.protocol import BaseLanguage, SemanticTokenValue, TokenColorRule
from theme_gen.lang.python import PythonLang
from theme_gen.lang.registry import LanguageRegistry
from theme_gen.lang.script import ScriptLang
from theme_gen.lang.semantic import GlobalSemanticTokens
from theme_gen.lang.ts import TypeScriptLang
from theme_gen.lang.yaml import YamlLang
from theme_gen.palette.theme import Theme


@pytest.fixture
def theme() -> Theme:
    return Theme.create()


@pytest.fixture
def full_registry(theme: Theme) -> LanguageRegistry:
    reg = LanguageRegistry(GlobalSemanticTokens(theme.syntax))
    lang_factories: list[Callable[[], BaseLanguage]] = [
        BaseSyntax,
        JavaLang,
        KotlinLang,
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
        reg.register(lang_cls())
    return reg


# ── Per-language classes ──

ALL_LANGS: list[Callable[[], BaseLanguage]] = [
    BaseSyntax,
    JavaLang,
    KotlinLang,
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


_MIN_SEMANTIC_COUNT = 55


class TestPerLanguageClasses:
    @pytest.mark.parametrize("lang_cls", ALL_LANGS)
    def test_has_id(self, lang_cls: Callable[[], BaseLanguage]) -> None:
        lang = lang_cls()
        assert isinstance(lang.id, str)
        assert len(lang.id) > 0

    @pytest.mark.parametrize("lang_cls", ALL_LANGS)
    def test_returns_token_color_rules(self, lang_cls: Callable[[], BaseLanguage], theme: Theme) -> None:
        rules = lang_cls().textmate_rules(theme)
        assert isinstance(rules, list)
        assert all(isinstance(r, TokenColorRule) for r in rules)

    @pytest.mark.parametrize("lang_cls", ALL_LANGS)
    def test_inherits_base_language(self, lang_cls: Callable[[], BaseLanguage]) -> None:
        assert isinstance(lang_cls(), BaseLanguage)

    def test_unique_ids(self) -> None:
        ids = [cls().id for cls in ALL_LANGS]
        assert len(ids) == len(set(ids))

    def test_js_ts_both_have_import_export_rules(self, theme: Theme) -> None:
        js_names = {r.name for r in JavaScriptLang().textmate_rules(theme)}
        assert "JS import/export keywords" in js_names
        ts_names = {r.name for r in TypeScriptLang().textmate_rules(theme)}
        assert "TS import/export keywords" in ts_names


# ── LanguageRegistry ──


class TestLanguageRegistry:
    def test_build_token_colors_returns_list(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        rules = full_registry.build_token_colors(theme)
        assert isinstance(rules, list)
        assert all(isinstance(r, TokenColorRule) for r in rules)

    def test_aggregation_order_output_before_reset(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        rules = full_registry.build_token_colors(theme)
        names = [r.name for r in rules]
        info_idx = names.index("Info token")
        reset_idx = names.index("Reset font styles")
        assert info_idx < reset_idx

    def test_style_reset_is_last(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        rules = full_registry.build_token_colors(theme)
        assert rules[-1].name == "Reset font styles"

    def test_base_rules_come_first(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        rules = full_registry.build_token_colors(theme)
        assert rules[0].name == "Global settings"

    def test_build_semantic_tokens_returns_dict(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        tokens = full_registry.build_semantic_tokens(theme)
        assert isinstance(tokens, dict)
        assert len(tokens) >= _MIN_SEMANTIC_COUNT

    def test_semantic_values_are_serialized(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        tokens = full_registry.build_semantic_tokens(theme)
        for key, val in tokens.items():
            assert isinstance(val, (str, dict)), f"{key}: {type(val)}"

    def test_global_tokens_have_no_colon(self, full_registry: LanguageRegistry, theme: Theme) -> None:
        global_tokens = GlobalSemanticTokens(theme.syntax).build()
        sem = full_registry.build_semantic_tokens(theme)
        for key in global_tokens:
            assert key in sem
            assert ":" not in key

    def test_per_lang_overrides_get_suffix(self, theme: Theme) -> None:
        """If a language provides overrides, they get :language suffix."""

        class FakeLang(BaseLanguage):
            @property
            @override
            def id(self) -> str:
                return "fake"

            @override
            def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
                return []

            @override
            def semantic_token_overrides(self, theme: Theme) -> dict[str, SemanticTokenValue]:
                return {"parameter": TCol("#FF0000")}

        reg = LanguageRegistry(GlobalSemanticTokens(theme.syntax))
        reg.register(FakeLang())
        tokens = reg.build_semantic_tokens(theme)
        assert "parameter:fake" in tokens
        assert tokens["parameter:fake"] == TCol("#FF0000").hex
