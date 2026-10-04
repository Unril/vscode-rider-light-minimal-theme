"""MarkdownLang -- Markdown TextMate overrides.

Headings are teal bold with subtle hue shift per level, inline code is comment
green, links are function green with blue underlined URLs, structural chrome
(list markers, blockquotes, table pipes, code fences) is muted grey.
"""

from collections.abc import Iterator
from typing import override

from theme_gen.core.font_style import FontStyle
from theme_gen.core.tcol import TCol
from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


def _heading_rules(colors: list[TCol], fallback: TCol) -> Iterator[TokenColorRule]:
    """Heading rules using the theme's hue-shifted series."""
    style = FontStyle.BOLD
    for level, color in enumerate(colors, start=1):
        prefix = f"heading.{level}.markdown"
        yield tcr(f"Markdown H{level} text", f"{prefix} entity.name.section.markdown", color, style)
        yield tcr(f"Markdown H{level} markers", f"{prefix} punctuation.definition.heading.markdown", color, style)
    # Fallback for headings without level scope
    yield tcr("Markdown heading text", "entity.name.section.markdown", fallback, style)
    yield tcr("Markdown heading markers", "punctuation.definition.heading.markdown", fallback, style)


class MarkdownLang(BaseLanguage):
    @property
    @override
    def id(self) -> str:
        return "markdown"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        p = theme.palette

        return [
            *_heading_rules(theme.syntax.hue_shifted, theme.syntax.hue_shifted[0]),
            # ── Inline code ──
            tcr(
                "Markdown inline code",
                ["markup.inline.raw.string.markdown", "punctuation.definition.raw.markdown"],
                s.comment,
            ),
            # ── Body text ──
            tcr("Markdown body text", "meta.paragraph.markdown", s.foreground),
            # ── Emphasis markers ──
            tcr(
                "Markdown bold/italic markers",
                ["punctuation.definition.bold.markdown", "punctuation.definition.italic.markdown"],
                p.fg_muted,
            ),
            tcr(
                "Markdown strikethrough",
                ["markup.strikethrough.markdown", "punctuation.definition.strikethrough.markdown"],
                p.fg_muted,
            ),
            # ── Links and images ──
            tcr("Markdown link text", "string.other.link.title.markdown", s.function),
            tcr("Markdown link description", "string.other.link.description.markdown", s.keyword),
            tcr("Markdown link URL", "markup.underline.link.markdown", s.keyword, FontStyle.UNDERLINE),
            tcr("Markdown image URL", "markup.underline.link.image.markdown", s.keyword, FontStyle.UNDERLINE),
            tcr(
                "Markdown link brackets",
                [
                    "punctuation.definition.link.title.begin.markdown",
                    "punctuation.definition.link.title.end.markdown",
                    "punctuation.definition.link.description.begin.markdown",
                    "punctuation.definition.link.description.end.markdown",
                ],
                p.fg_muted,
            ),
            tcr(
                "Markdown link metadata",
                [
                    "punctuation.definition.metadata.markdown",
                    "string.other.link.description.title.markdown",
                    "punctuation.definition.string.begin.markdown",
                    "punctuation.definition.string.end.markdown",
                ],
                p.fg_muted,
            ),
            # ── Frontmatter ──
            tcr("Markdown frontmatter YAML keys", "meta.embedded.block.frontmatter entity.name.tag.yaml", s.field),
            tcr(
                "Markdown frontmatter delimiters",
                ["punctuation.definition.begin.frontmatter", "punctuation.definition.end.frontmatter"],
                p.fg_muted,
            ),
            # ── Tables ──
            tcr("Markdown table pipes", "punctuation.definition.table.markdown", p.fg_muted),
            tcr("Markdown table separator", "punctuation.separator.table.markdown", p.fg_muted),
            # ── Fenced code ──
            tcr("Markdown fenced code body", "markup.fenced_code.block.markdown", s.foreground),
            tcr("Markdown code fence delimiters", "punctuation.definition.markdown", s.comment),
            tcr(
                "Markdown code fence language",
                ["fenced_code.block.language.markdown", "fenced_code.block.language"],
                p.fg_muted,
            ),
            # ── Structural chrome ──
            tcr("Markdown horizontal rule", "meta.separator.markdown", p.fg_muted),
            tcr(
                "Markdown list markers",
                [
                    "text.html.markdown beginning.punctuation.definition.list",
                    "punctuation.definition.list.begin.markdown",
                ],
                p.fg_muted,
            ),
            tcr("Markdown blockquote marker", "punctuation.definition.quote.begin.markdown", p.fg_muted),
        ]
