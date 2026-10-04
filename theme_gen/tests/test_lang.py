"""Tests for lang layer: protocol types, BaseSyntax, GlobalSemanticTokens."""

import pytest

from theme_gen.core.font_style import FontStyle
from theme_gen.core.tcol import TCol
from theme_gen.lang.base import BaseSyntax
from theme_gen.lang.protocol import (
    BaseLanguage,
    SemanticTokenStyle,
    TokenColorRule,
)
from theme_gen.lang.semantic import GlobalSemanticTokens
from theme_gen.palette.syntax import SyntaxPalette
from theme_gen.palette.theme import Theme

_MIN_BASE_RULES = 50
_MIN_SEMANTIC_COUNT = 55


@pytest.fixture
def theme() -> Theme:
    return Theme.create()


@pytest.fixture
def syntax(theme: Theme) -> SyntaxPalette:
    return theme.syntax


# ── TokenColorRule ──


class TestTokenColorRule:
    def test_to_dict_with_color_and_style(self) -> None:
        col = TCol("#FF0000")
        rule = TokenColorRule(name="Test", scope="comment", color=col, style=FontStyle.ITALIC)
        d = rule.to_dict()
        assert d["name"] == "Test"
        assert d["scope"] == ["comment"]
        settings = d["settings"]
        assert isinstance(settings, dict)
        assert settings["foreground"] == col.hex
        assert settings["fontStyle"] == "italic"

    def test_to_dict_color_only(self) -> None:
        col = TCol("#00FF00")
        rule = TokenColorRule(name="Green", scope=["a", "b"], color=col)
        d = rule.to_dict()
        assert d["scope"] == ["a", "b"]
        settings = d["settings"]
        assert isinstance(settings, dict)
        assert "foreground" in settings
        assert "fontStyle" not in settings

    def test_to_dict_style_only(self) -> None:
        rule = TokenColorRule(name="Bold", scope="strong", style=FontStyle.BOLD)
        d = rule.to_dict()
        settings = d["settings"]
        assert isinstance(settings, dict)
        assert "foreground" not in settings
        assert settings["fontStyle"] == "bold"

    def test_to_dict_no_settings(self) -> None:
        rule = TokenColorRule(name="Empty", scope="x")
        d = rule.to_dict()
        assert d["settings"] == {}

    def test_frozen(self) -> None:
        rule = TokenColorRule(name="X", scope="y")
        with pytest.raises(AttributeError):
            rule.name = "Z"  # type: ignore[misc]  # pyright: ignore[reportAttributeAccessIssue]  # frozen dataclass


# ── SemanticTokenStyle ──


class TestSemanticTokenStyle:
    def test_to_dict(self) -> None:
        col = TCol("#AABBCC")
        style = SemanticTokenStyle(foreground=col, font_style=FontStyle.ITALIC)
        d = style.to_dict()
        assert d["foreground"] == col.hex
        assert d["fontStyle"] == "italic"

    def test_to_dict_none_style(self) -> None:
        col = TCol("#112233")
        style = SemanticTokenStyle(foreground=col, font_style=FontStyle.NONE)
        d = style.to_dict()
        assert d["fontStyle"] == ""

    def test_frozen(self) -> None:
        style = SemanticTokenStyle(foreground=TCol("#000000"), font_style=FontStyle.BOLD)
        with pytest.raises(AttributeError):
            style.foreground = TCol("#FFFFFF")  # type: ignore[misc]  # pyright: ignore[reportAttributeAccessIssue]  # frozen dataclass


# ── BaseLanguage ──


class TestBaseLanguage:
    def test_default_semantic_overrides_empty(self) -> None:
        # BaseSyntax inherits the default empty semantic_token_overrides from BaseLanguage
        lang = BaseSyntax()
        theme = Theme.create()
        assert lang.semantic_token_overrides(theme) == {}  # exact empty dict check intentional

    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            _ = BaseLanguage()  # pyright: ignore[reportAbstractUsage]  # intentional: asserting abstractness


# ── BaseSyntax ──


class TestBaseSyntax:
    def test_id(self) -> None:
        assert BaseSyntax().id == "base"

    def test_returns_list_of_token_color_rules(self, theme: Theme) -> None:
        rules = BaseSyntax().textmate_rules(theme)
        assert isinstance(rules, list)
        assert all(isinstance(r, TokenColorRule) for r in rules)

    def test_rule_count_at_least_50(self, theme: Theme) -> None:
        rules = BaseSyntax().textmate_rules(theme)
        assert len(rules) >= _MIN_BASE_RULES

    def test_first_rule_is_global_settings(self, theme: Theme) -> None:
        rules = BaseSyntax().textmate_rules(theme)
        assert rules[0].name == "Global settings"
        assert rules[0].color == theme.syntax.foreground

    def test_last_rule_is_cross_lang(self, theme: Theme) -> None:
        rules = BaseSyntax().textmate_rules(theme)
        assert rules[-1].name == "Go/C#/Groovy/Java storage types"

    def test_all_rules_have_names(self, theme: Theme) -> None:
        rules = BaseSyntax().textmate_rules(theme)
        for r in rules:
            assert r.name, f"Rule missing name: {r}"

    def test_all_rules_serialize(self, theme: Theme) -> None:
        rules = BaseSyntax().textmate_rules(theme)
        for r in rules:
            d = r.to_dict()
            assert "name" in d
            assert "scope" in d
            assert "settings" in d

    def test_inherits_base_language(self) -> None:
        assert isinstance(BaseSyntax(), BaseLanguage)
        assert BaseSyntax().semantic_token_overrides(Theme.create()) == {}


# ── GlobalSemanticTokens ──


class TestGlobalSemanticTokens:
    def test_returns_dict(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        assert isinstance(tokens, dict)

    def test_entry_count_at_least_55(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        assert len(tokens) >= _MIN_SEMANTIC_COUNT

    def test_values_are_tcol_or_style(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        for key, val in tokens.items():
            assert isinstance(val, (TCol, SemanticTokenStyle)), f"{key}: {type(val)}"

    def test_standard_types_present(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        for key in [
            "function",
            "class",
            "variable",
            "parameter",
            "keyword",
            "string",
            "number",
            "comment",
        ]:
            assert key in tokens, f"Missing standard type: {key}"

    def test_comment_has_italic_style(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        val = tokens["comment"]
        assert isinstance(val, SemanticTokenStyle)
        assert val.font_style == FontStyle.ITALIC

    def test_function_maps_to_syntax_function(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        assert tokens["function"] == syntax.function

    def test_no_language_scoped_selectors(self, syntax: SyntaxPalette) -> None:
        tokens = GlobalSemanticTokens(syntax).build()
        for key in tokens:
            assert ":" not in key, f"Global token has language scope: {key}"
