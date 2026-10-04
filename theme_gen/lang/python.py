"""PythonLang -- Python TextMate overrides."""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class PythonLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "python"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        return [
            tcr("Python import keywords", ["keyword.control.import.python", "keyword.control.from.python"], s.keyword),
            tcr("Python function declarations", "meta.function.python entity.name.function", s.function_decl),
            tcr(
                "Python function calls",
                ["source.python meta.function-call.python", "meta.function-call.generic.python"],
                s.function,
            ),
            tcr(
                "Python decorators",
                ["entity.name.function.decorator.python", "punctuation.definition.decorator.python"],
                s.metadata,
            ),
            tcr("Python built-in functions", "support.function.builtin.python", s.function_decl),
            tcr("Python magic methods (TM fallback)", "support.function.magic.python", s.function_decl),
            tcr("Python magic variables", "support.variable.magic.python", s.field),
            tcr(
                "Python self/cls",
                [
                    "variable.parameter.function.language.special.self.python",
                    "variable.parameter.function.language.special.cls.python",
                ],
                s.keyword,
            ),
            tcr("Python ALL_CAPS constants", "constant.other.caps.python", s.field_const),
            tcr("Python dict keys", "meta.structure.dictionary.key.python", s.field),
            tcr("Python f-string braces", "constant.character.format.placeholder.other.python", s.escape),
            tcr("Python ellipsis literal", "constant.other.ellipsis.python", s.keyword),
            tcr("Python property access", "meta.attribute.python", s.field),
            # String prefix (f, b, r, u) is part of the literal, not a keyword
            tcr("Python string prefix", "storage.type.string.python", s.string),
            # Hex/octal/binary prefix (0x, 0o, 0b) is part of the number
            tcr(
                "Python number prefix",
                ["storage.type.number.python", "storage.type.imaginary.number.python"],
                s.number,
            ),
        ]
