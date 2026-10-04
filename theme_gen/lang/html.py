"""HtmlLang -- HTML TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class HtmlLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "html"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr(
                "HTML entities",
                ["punctuation.definition.entity.html", "constant.character.entity.html", "constant.character.entity"],
                s.escape,
            ),
        ]
