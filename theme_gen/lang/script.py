"""ScriptLang -- placeholder for future shell/Makefile/Dockerfile overrides.

All generic cross-language rules previously here have been moved to BaseSyntax.
"""

from typing import override

from theme_gen.lang.protocol import BaseLanguage, TokenColorRule
from theme_gen.palette.theme import Theme


class ScriptLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "script"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        return []
