"""UISection protocol -- contract for UI color section providers."""

from typing import Protocol

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme


class UISection(Protocol):
    """Each section returns a dict of VS Code color key -> TCol."""

    def build(self, theme: Theme) -> dict[str, TCol]: ...
