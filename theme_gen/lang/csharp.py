"""CSharpLang -- C# TextMate + semantic overrides.

Targets the built-in C# grammar (source.cs) and the Roslyn-based semantic
tokenizer. The grammar uses `.cs`-suffixed scopes for most constructs;
this module handles C#-specific scopes not covered by base rules.

Semantic overrides target Roslyn LSP types that some configurations emit
(extensionMethod, delegate, recordClass, etc.) -- these are no-ops when
the server emits only standard types, but color correctly when available.
"""

from typing import override

from core.font_style import FontStyle
from lang.protocol import BaseLanguage, SemanticTokenStyle, SemanticTokenValue, TokenColorRule, tcr
from palette.theme import Theme


class CSharpLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "csharp"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr("C# namespace names", "entity.name.type.namespace.cs", s.namespace),
            tcr(
                "C# preprocessor",
                [
                    "keyword.preprocessor.if.cs",
                    "keyword.preprocessor.else.cs",
                    "keyword.preprocessor.elif.cs",
                    "keyword.preprocessor.endif.cs",
                    "keyword.preprocessor.define.cs",
                    "keyword.preprocessor.undef.cs",
                    "keyword.preprocessor.region.cs",
                    "keyword.preprocessor.endregion.cs",
                    "keyword.preprocessor.nullable.cs",
                    "keyword.preprocessor.pragma.cs",
                    "entity.name.variable.preprocessor.symbol.cs",
                ],
                s.keyword,
            ),
            tcr(
                "C# field and property declarations",
                ["entity.name.variable.field.cs", "entity.name.variable.property.cs", "entity.name.variable.event.cs"],
                s.field,
            ),
            tcr("C# enum members", "entity.name.variable.enum-member.cs", s.enum_member),
            tcr("C# interpolation punctuation", "punctuation.definition.interpolation.begin.cs", s.keyword),
            tcr("C# interpolation end", "punctuation.definition.interpolation.end.cs", s.keyword),
            tcr(
                "C# XML doc comment tags",
                ["entity.name.tag.localname.cs", "punctuation.definition.tag.cs"],
                s.comment,
                FontStyle.ITALIC,
            ),
        ]

    @override
    def semantic_token_overrides(self, theme: Theme) -> dict[str, SemanticTokenValue]:
        """C#-scoped semantic token overrides.

        These target Roslyn LSP token types that some configurations emit.
        Standard types (class, struct, interface, method, property, etc.)
        are already handled by GlobalSemanticTokens.
        """
        s = theme.syntax
        return {
            "method": SemanticTokenStyle(foreground=s.function_decl, font_style=FontStyle.BOLD),
            "extensionMethod": SemanticTokenStyle(foreground=s.function, font_style=FontStyle.ITALIC),
            "delegate": s.type,
            "recordClass": s.type,
            "recordStruct": s.type,
            "stringVerbatim": s.string,
            "stringEscapeCharacter": s.escape,
            "preprocessorKeyword": s.keyword,
            "preprocessorText": s.foreground,
            "excludedCode": s.comment,
            "controlKeyword": s.control,
            "operatorOverloaded": s.function,
            "xmlDocCommentAttributeName": s.field,
            "xmlDocCommentAttributeQuotes": s.string,
            "xmlDocCommentAttributeValue": s.string,
            "xmlDocCommentComment": SemanticTokenStyle(foreground=s.comment, font_style=FontStyle.ITALIC),
            "xmlDocCommentDelimiter": s.comment,
            "xmlDocCommentName": s.type,
            "xmlDocCommentText": s.comment,
        }
