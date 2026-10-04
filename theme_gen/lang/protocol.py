"""Language protocol, shared types, and BaseLanguage default implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

from theme_gen.core.font_style import FontStyle
from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme


@dataclass(frozen=True)
class TokenColorRule:
    """A single VS Code tokenColors entry.

    scope accepts a single string or list of strings. color and style are optional -- omitted keys are absent from output.
    """

    name: str
    scope: str | list[str]
    color: TCol | None = None
    style: FontStyle | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialize to VS Code tokenColors format."""
        settings: dict[str, str] = {}
        if self.color is not None:
            settings["foreground"] = self.color.hex
        if self.style is not None:
            settings["fontStyle"] = self.style.value
        scopes = self.scope if isinstance(self.scope, list) else [self.scope]
        result: dict[str, object] = {"name": self.name, "scope": scopes, "settings": settings}
        return result


def tcr(
    name: str,
    scope: str | list[str],
    color: TCol | None = None,
    style: FontStyle | None = None,
) -> TokenColorRule:
    return TokenColorRule(name=name, scope=scope, color=color, style=style)


@dataclass(frozen=True)
class SemanticTokenStyle:
    """Value for a semanticTokenColors entry that needs both color and font style.

    Unlike TokenColorRule (which models a full tokenColors array entry with name, scope, and optional settings), this is just the value half of a key->value pair in the semanticTokenColors map. Most entries are plain TCol (color only); this class covers
    the ~8 entries that also set bold/italic. Serializes to {"foreground": "#hex", "fontStyle": "..."}.
    """

    foreground: TCol
    font_style: FontStyle

    def to_dict(self) -> dict[str, str]:
        return {"foreground": self.foreground.hex, "fontStyle": self.font_style.value}


type SemanticTokenValue = TCol | SemanticTokenStyle


class Language(Protocol):
    """Contract for language-specific token providers."""

    @property
    def id(self) -> str: ...

    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]: ...

    def semantic_token_overrides(self, theme: Theme) -> dict[str, SemanticTokenValue]: ...


class BaseLanguage(ABC):
    """Default implementation -- empty semantic overrides.

    Per-language classes inherit this and implement id + textmate_rules(). Override semantic_token_overrides() only when the language has entries.
    """

    @property
    @abstractmethod
    def id(self) -> str: ...

    @abstractmethod
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]: ...

    def semantic_token_overrides(
        self,
        theme: Theme,  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
    ) -> dict[str, SemanticTokenValue]:
        return {}
