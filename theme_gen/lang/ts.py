"""TypeScriptLang -- TypeScript/TSX TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class TypeScriptLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "typescript"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr(
                "TS import/export keywords",
                [
                    "keyword.control.import.ts",
                    "keyword.control.import.tsx",
                    "keyword.control.export.ts",
                    "keyword.control.export.tsx",
                    "keyword.control.default.ts",
                    "keyword.control.default.tsx",
                    "keyword.control.from.ts",
                    "keyword.control.from.tsx",
                ],
                s.keyword,
            ),
            tcr(
                "TS constructor calls",
                ["new.expr.ts entity.name.function.ts", "new.expr.tsx entity.name.function.tsx"],
                s.type,
            ),
            tcr(
                "TS type aliases in imports",
                ["variable.other.readwrite.alias.ts", "variable.other.readwrite.alias.tsx"],
                s.type,
            ),
        ]
