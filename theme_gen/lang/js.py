"""JavaScriptLang -- JavaScript/JSX TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class JavaScriptLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "javascript"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr(
                "JS import/export keywords",
                [
                    "keyword.control.import.js",
                    "keyword.control.import.jsx",
                    "keyword.control.export.js",
                    "keyword.control.export.jsx",
                    "keyword.control.default.js",
                    "keyword.control.default.jsx",
                    "keyword.control.from.js",
                    "keyword.control.from.jsx",
                ],
                s.keyword,
            ),
            tcr(
                "JS constructor calls",
                ["new.expr.js entity.name.function.js", "new.expr.jsx entity.name.function.jsx"],
                s.type,
            ),
        ]
