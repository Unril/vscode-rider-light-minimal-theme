"""Tests for CSS generation (markdown preview variables)."""

import re

from css.markdown_variables import _extract_vars, build_css
from palette.theme import Theme

_CSS_VAR_RE = re.compile(r"^\s+--rlm-[\w-]+:\s+#[0-9A-Fa-f]{6,8};$")
_EXPECTED_VAR_COUNT = 33


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
            "bg",
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
