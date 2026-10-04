"""Theme -- top-level frozen dataclass composing all palettes."""

from dataclasses import dataclass
from typing import Self

from theme_gen.palette.editor import EditorPalette
from theme_gen.palette.palette import Palette
from theme_gen.palette.syntax import SyntaxPalette


@dataclass(frozen=True)
class Theme:
    """Top-level theme: palette + syntax + editor + variant flag."""

    palette: Palette
    syntax: SyntaxPalette
    editor: EditorPalette
    is_dark: bool

    @classmethod
    def create(
        cls,
        *,
        accent_hue: float = 262.0,
        is_dark: bool = False,
    ) -> Self:
        """Build full theme chain from accent_hue + variant."""
        palette = Palette.for_dark(accent_hue) if is_dark else Palette.for_light(accent_hue)

        syntax = SyntaxPalette.create(
            background=palette.background,
            foreground=palette.foreground,
            is_dark=is_dark,
        )
        editor = EditorPalette.create(syntax, palette)
        return cls(
            palette=palette,
            syntax=syntax,
            editor=editor,
            is_dark=is_dark,
        )
