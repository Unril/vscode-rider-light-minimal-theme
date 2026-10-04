"""CssLang -- CSS/SCSS/LESS TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class CssLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "css"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr(
                "CSS/SCSS/LESS selectors",
                [
                    "entity.other.attribute-name.class.css",
                    "source.css entity.other.attribute-name.class",
                    "entity.other.attribute-name.id.css",
                    "entity.other.attribute-name.parent-selector.css",
                    "entity.other.attribute-name.parent.less",
                    "source.css entity.other.attribute-name.pseudo-class",
                    "entity.other.attribute-name.pseudo-class.css",
                    "entity.other.attribute-name.pseudo-element.css",
                    "source.css.less entity.other.attribute-name.id",
                    "entity.other.attribute-name.scss",
                ],
                s.type,
            ),
            tcr(
                "CSS property names",
                [
                    "support.type.property-name",
                    "support.type.vendored.property-name",
                    "source.css variable",
                    "source.coffee.embedded",
                ],
                s.keyword,
            ),
            tcr(
                "CSS property values",
                [
                    "support.constant.property-value",
                    "support.constant.font-name",
                    "support.constant.media-type",
                    "support.constant.media",
                    "support.constant.color",
                ],
                s.foreground,
            ),
            tcr("CSS color values", ["constant.other.color.rgb-value", "constant.other.rgb-value"], s.number),
        ]
