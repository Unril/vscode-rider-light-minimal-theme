"""LanguageRegistry -- aggregates Language instances into final token structures.

Owns two cross-cutting concerns:
  - _output_tokens(): 4 terminal/output panel rules
  - _style_reset(): font-style reset (must be last)

Aggregation order invariant (TextMate last-match-wins for font-style):
  1. BaseSyntax rules
  2. Per-language overrides (registration order)
  3. Output tokens
  4. Style reset (MUST be last)
"""

from theme_gen.core.font_style import FontStyle
from theme_gen.core.tcol import TCol
from theme_gen.lang.protocol import (
    Language,
    SemanticTokenValue,
    TokenColorRule,
    tcr,
)
from theme_gen.lang.semantic import GlobalSemanticTokens
from theme_gen.palette.theme import Theme


class LanguageRegistry:
    """Collects Language instances and builds aggregated token structures."""

    def __init__(self, semantic: GlobalSemanticTokens) -> None:
        self._languages: list[Language] = []
        self._semantic: GlobalSemanticTokens = semantic

    def register(self, lang: Language) -> None:
        self._languages.append(lang)

    def build_token_colors(self, theme: Theme) -> list[TokenColorRule]:
        """Aggregate TM rules: base -> per-lang -> output -> style reset."""
        rules: list[TokenColorRule] = []
        for lang in self._languages:
            rules.extend(lang.textmate_rules(theme))
        rules.extend(_output_tokens(theme))
        rules.extend(_style_reset())
        return rules

    def build_semantic_tokens(self, theme: Theme) -> dict[str, str | dict[str, str]]:
        """Merge global + per-language semantic tokens, serialized to hex/dict.

        Per-language overrides get ':language' suffix appended automatically.
        """
        result: dict[str, str | dict[str, str]] = {}

        # Global entries (bare selectors)
        for selector, value in self._semantic.build().items():
            result[selector] = _serialize_value(value)

        # Per-language entries (auto-suffixed with :language)
        for lang in self._languages:
            overrides = lang.semantic_token_overrides(theme)
            for selector, value in overrides.items():
                scoped = f"{selector}:{lang.id}"
                result[scoped] = _serialize_value(value)

        return result


def _serialize_value(value: SemanticTokenValue) -> str | dict[str, str]:
    if isinstance(value, TCol):
        return value.hex
    return value.to_dict()


def _output_tokens(theme: Theme) -> list[TokenColorRule]:
    """Terminal and output panel log-level tokens."""
    e = theme.editor
    o = e.output
    return [
        tcr("Info token", "token.info-token", o.info),
        tcr("Warn token", "token.warn-token", o.warn),
        tcr("Error token", "token.error-token", o.error),
        tcr("Debug token", "token.debug-token", o.debug),
    ]


def _style_reset() -> list[TokenColorRule]:
    """Strip inherited font styles from broad scopes (must be last)."""
    return [
        tcr(
            "Reset font styles",
            [
                "entity.name.function",
                "entity.name.type",
                "entity.name.tag",
                "variable",
                "variable.parameter",
                "keyword",
                "storage",
                "storage.type",
                "storage.modifier",
                "string",
                "constant",
                "constant.numeric",
                "support",
                "support.function",
                "support.class",
                "support.type",
            ],
            style=FontStyle.NONE,
        ),
    ]
