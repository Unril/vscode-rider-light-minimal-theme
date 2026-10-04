"""KotlinLang -- Kotlin TextMate + semantic overrides.

Kotlin LSP quirks addressed here:
  - variable [readonly] emitted for local vals without the `local` modifier,
    so the global `variable.readonly` -> field_const would color them as
    constants. Override to param (dark grey) for Kotlin.
"""

from typing import override

from theme_gen.core.font_style import FontStyle
from theme_gen.lang.protocol import BaseLanguage, SemanticTokenStyle, SemanticTokenValue, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class KotlinLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "kotlin"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr("Kotlin package names", "entity.name.package.kotlin", s.namespace),
            tcr(
                "Kotlin annotations",
                [
                    "entity.name.function.annotation.kotlin",
                    "entity.name.type.annotation-site.kotlin",
                    "meta.annotation.kotlin",
                    "punctuation.definition.annotation.kotlin",
                ],
                s.metadata,
            ),
            tcr("Enum members", "variable.other.enummember", s.enum_member),
            tcr("Kotlin interpolated variables", "variable.other.interpolated.kotlin", s.field),
            tcr("Kotlin interpolated expressions", "variable.other.interpolated.expression.kotlin", s.function),
        ]

    @override
    def semantic_token_overrides(self, theme: Theme) -> dict[str, SemanticTokenValue]:
        """Kotlin-scoped semantic token overrides.

        Kotlin LSP emits `variable [readonly]` for local vals without the
        `local` modifier, causing them to match the global `variable.readonly`
        -> field_const. Override to param so local vals look like variables.
        """
        s = theme.syntax
        # Keys are bare selectors -- registry auto-appends `:kotlin`
        return {
            "variable.readonly": s.param,
            "operator.declaration": SemanticTokenStyle(foreground=s.function_decl, font_style=FontStyle.ITALIC_BOLD),
            "operator.abstract": s.keyword,
        }
