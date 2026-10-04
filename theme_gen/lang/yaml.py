"""YamlLang -- YAML TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class YamlLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "yaml"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr("YAML keys", "entity.name.tag.yaml", s.field),
            # Unquoted plain values -- string color (matches quoted strings)
            # Must come BEFORE the constant overrides so they can win via longer scope
            tcr("YAML unquoted values", ["string.unquoted.plain.out.yaml", "string.unquoted.plain.in.yaml"], s.string),
            # Numbers -- use compound scopes to beat string.unquoted.plain.out.yaml (30 chars)
            tcr(
                "YAML numbers",
                [
                    "string.unquoted.plain.out.yaml constant.numeric.integer.decimal.yaml",
                    "string.unquoted.plain.out.yaml constant.numeric.integer.hexadecimal.yaml",
                    "string.unquoted.plain.out.yaml constant.numeric.integer.octal.yaml",
                    "string.unquoted.plain.out.yaml constant.numeric.float.yaml",
                    "string.unquoted.plain.out.yaml constant.numeric.float.inf.yaml",
                    "string.unquoted.plain.out.yaml constant.numeric.float.nan.yaml",
                    "string.unquoted.plain.out.yaml constant.other.timestamp.yaml",
                    "string.unquoted.plain.in.yaml constant.numeric.integer.decimal.yaml",
                    "string.unquoted.plain.in.yaml constant.numeric.float.yaml",
                    "constant.numeric.integer.decimal.yaml",
                    "constant.numeric.integer.hexadecimal.yaml",
                    "constant.numeric.integer.octal.yaml",
                    "constant.numeric.float.yaml",
                    "constant.numeric.float.inf.yaml",
                    "constant.numeric.float.nan.yaml",
                    "constant.other.timestamp.yaml",
                    # Grammar quirk: fractional parts get constant.language.value.yaml
                    "constant.language.value.yaml",
                    # Grammar quirk: exponent parts (e-4) get constant.language.merge.yaml
                    "constant.numeric.float.yaml constant.language.merge.yaml",
                ],
                s.number,
            ),
            # Booleans -- compound scope beats string.unquoted.plain.out.yaml
            tcr(
                "YAML booleans",
                ["string.unquoted.plain.out.yaml constant.language.boolean.yaml", "constant.language.boolean.yaml"],
                s.keyword,
            ),
            # Null -- compound scope beats string.unquoted.plain.out.yaml
            tcr(
                "YAML null",
                ["string.unquoted.plain.out.yaml constant.language.null.yaml", "constant.language.null.yaml"],
                s.keyword,
            ),
            tcr("YAML merge key", "constant.language.merge.yaml", s.keyword),
            tcr("YAML sequence dash", "punctuation.definition.block.sequence.item.yaml", s.punct),
            tcr("YAML anchor/alias names", ["variable.other.anchor.yaml", "variable.other.alias.yaml"], s.field),
        ]
