"""JavaLang -- Java TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class JavaLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "java"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr("Java types", "storage.type.java", s.type),
            tcr(
                "Java annotations",
                ["storage.type.annotation.java", "punctuation.definition.annotation.java"],
                s.metadata,
            ),
            tcr(
                "Java imports",
                ["storage.modifier.import.java", "variable.language.wildcard.java", "storage.modifier.package.java"],
                s.namespace,
            ),
            tcr("Java enum constants", "constant.other.enum.java", s.enum_member),
            tcr("Java method declarations", "meta.method.identifier.java entity.name.function.java", s.function_decl),
        ]
