"""Generate markdown-variables.css with theme colors as CSS custom properties.

The generated file defines --rlm-* CSS variables once per variant (light, dark; the two high-contrast body classes share those rules), consumed by the static markdown-preview.css and markdown-highlight.css stylesheets.

It ships in the .vsix, so it defines only variables those stylesheets use (test_css.py enforces this).
"""

from theme_gen.palette.theme import Theme

_HEADER = """\
/*
 * Rider light minimal -- Generated CSS custom properties for markdown preview.
 * Do not edit by hand. Regenerate with: just gen (or uv run -m theme_gen)
 */
"""


def _extract_vars(theme: Theme) -> list[str]:
    """Extract CSS custom properties from a theme."""
    p = theme.palette
    s = theme.syntax

    pairs = [
        # Surfaces
        ("fg", p.foreground),
        ("accent", p.accent),
        ("border", p.border),
        ("panel", p.panel_bg),
        ("muted", p.fg_muted),
        # Code block background -- uses editor bg (not panel_bg) so syntax
        # colors pass WCAG AA. On panel_bg, string/comment/field/number/metadata
        # land at ~4.2:1; on editor bg they pass at ~4.6:1.
        ("code-bg", p.background),
        # Link active state (darker accent for press/hover feedback)
        ("link-active", p.accent_hover),
        # Syntax
        ("keyword", s.keyword),
        ("type", s.type),
        ("function", s.function),
        ("string", s.string),
        ("number", s.number),
        ("comment", s.comment),
        ("field", s.field),
        ("metadata", s.metadata),
        ("escape", s.escape),
        # Status
        ("error", p.error),
        ("success", p.success),
        # Headings + quote variants: same hue-shifted series
        *((f"h{i}", c) for i, c in enumerate(s.hue_shifted, start=1)),
        *((f"h{i}-quote", c) for i, c in enumerate(s.hue_shifted_quote, start=1)),
    ]
    return [f"    --rlm-{name}: {col.hex};" for name, col in pairs]


def build_css() -> str:
    """Build the full CSS string with light and dark variables."""
    light = Theme.create(is_dark=False)
    dark = Theme.create(is_dark=True)

    light_vars = "\n".join(_extract_vars(light))
    dark_vars = "\n".join(_extract_vars(dark))

    return (
        f"{_HEADER}\n"
        f"/* Light variant. High contrast maps to the matching base variant so the preview\n"
        f"   doesn't break when users switch to accessibility themes. */\n\n"
        f"body.vscode-light,\nbody.vscode-high-contrast-light {{\n{light_vars}\n}}\n\n"
        f"/* Dark variant */\n\n"
        # VS Code also gives high contrast light the vscode-high-contrast class; without the :not() this later,
        # equally specific rule would win there.
        f"body.vscode-dark,\nbody.vscode-high-contrast:not(.vscode-high-contrast-light) {{\n{dark_vars}\n}}\n"
    )
