"""Tests for CSS generation (markdown preview variables)."""

import re
from pathlib import Path

from theme_gen.css.markdown_variables import _extract_vars, build_css
from theme_gen.palette.theme import Theme

_CSS_VAR_RE = re.compile(r"^\s+--rlm-[\w-]+:\s+#[0-9A-Fa-f]{6,8};$")
_EXPECTED_VAR_COUNT = 31
_VARIANT_COUNT = 2  # light and dark; high contrast reuses them
_STYLES_DIR = Path(__file__).resolve().parents[2] / "styles"
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_DECLARATION_RE = re.compile(r"(--rlm-[\w-]+):\s*([^;]+);")
_REFERENCE_RE = re.compile(r"var\((--rlm-[\w-]+)")


def _hand_written_css() -> str:
    return "".join((_STYLES_DIR / name).read_text() for name in ("markdown-preview.css", "markdown-highlight.css"))


def _declarations_by_selector(css: str) -> dict[str, dict[str, str]]:
    """Map every selector in the generated CSS to the variable declarations its rule carries."""
    result: dict[str, dict[str, str]] = {}
    for rule in _RULE_RE.finditer(re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)):
        declarations = {m.group(1): m.group(2) for m in _DECLARATION_RE.finditer(rule.group(2))}
        for selector in rule.group(1).split(","):
            result[selector.strip()] = declarations
    return result


class TestExtractVars:
    def test_returns_list_of_css_lines(self) -> None:
        theme = Theme.create(is_dark=False)
        lines = _extract_vars(theme)
        assert isinstance(lines, list)
        assert len(lines) == _EXPECTED_VAR_COUNT

    def test_all_lines_are_valid_css_vars(self) -> None:
        theme = Theme.create(is_dark=False)
        for line in _extract_vars(theme):
            assert _CSS_VAR_RE.match(line), f"Invalid CSS var line: {line!r}"

    def test_dark_produces_different_values(self) -> None:
        light = _extract_vars(Theme.create(is_dark=False))
        dark = _extract_vars(Theme.create(is_dark=True))
        assert light != dark

    def test_contains_expected_var_names(self) -> None:
        lines = _extract_vars(Theme.create(is_dark=False))
        joined = "\n".join(lines)
        for name in [
            "fg",
            "accent",
            "keyword",
            "type",
            "function",
            "string",
            "comment",
            "error",
            "h1",
            "h2",
            "h3",
            "h1-quote",
            "metadata",
            "escape",
            "quote-fg",
        ]:
            assert f"--rlm-{name}:" in joined, f"Missing --rlm-{name}"


class TestBuildCss:
    def test_contains_both_variants(self) -> None:
        css = build_css()
        assert "body.vscode-light" in css
        assert "body.vscode-dark" in css

    def test_contains_header_comment(self) -> None:
        css = build_css()
        assert "Do not edit by hand" in css

    def test_light_and_dark_have_different_values(self) -> None:
        css = build_css()
        # Split at the dark section and check values differ
        parts = css.split("body.vscode-dark")
        assert len(parts) == 2  # noqa: PLR2004
        assert parts[0] != parts[1]


class TestShippedStylesheet:
    """markdown-variables.css ships in the .vsix, so it carries only what the hand-written styles use, once."""

    def test_every_generated_variable_is_used_by_a_stylesheet(self) -> None:
        defined = set(_declarations_by_selector(build_css())["body.vscode-light"])
        used = set(_REFERENCE_RE.findall(_hand_written_css()))
        assert defined - used == set(), f"unused variables shipped in the .vsix: {sorted(defined - used)}"

    def test_every_variable_a_stylesheet_uses_is_generated(self) -> None:
        defined = set(_declarations_by_selector(build_css())["body.vscode-light"])
        used = set(_REFERENCE_RE.findall(_hand_written_css()))
        assert used - defined == set(), f"variables used but never defined: {sorted(used - defined)}"

    def test_each_variable_is_declared_once_per_variant(self) -> None:
        css = build_css()
        for name in _declarations_by_selector(css)["body.vscode-light"]:
            assert len(re.findall(rf"^\s+{name}:", css, flags=re.MULTILINE)) == _VARIANT_COUNT, name

    def test_high_contrast_gets_the_matching_base_variables(self) -> None:
        by_selector = _declarations_by_selector(build_css())
        assert by_selector["body.vscode-high-contrast-light"] == by_selector["body.vscode-light"]
        assert by_selector["body.vscode-high-contrast"] == by_selector["body.vscode-dark"]
        assert by_selector["body.vscode-light"] != by_selector["body.vscode-dark"]
