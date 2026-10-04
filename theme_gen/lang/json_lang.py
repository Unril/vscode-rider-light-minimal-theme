"""JsonLang -- JSON TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class JsonLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "json"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr("JSON property keys", "support.type.property-name.json", s.field),
            tcr("JSON constants", "constant.language.json", s.keyword),
        ]
