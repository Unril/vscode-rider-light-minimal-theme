"""Tests for CSS generation (markdown preview variables)."""

import re
from collections import defaultdict
from pathlib import Path

import pytest

from theme_gen.css.markdown_variables import _extract_vars, build_css
from theme_gen.palette.theme import Theme

_CSS_VAR_RE = re.compile(r"^\s+--rlm-[\w-]+:\s+#[0-9A-Fa-f]{6,8};$")
_EXPECTED_VAR_COUNT = 30
_VARIANT_COUNT = 2  # light and dark; high contrast reuses them
_STYLES_DIR = Path(__file__).resolve().parents[2] / "styles"
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_SELECTOR_LIST_COMMA_RE = re.compile(r",(?![^()]*\))")  # not inside :has(...) / :is(...)
_DECLARATION_RE = re.compile(r"(--rlm-[\w-]+):\s*([^;]+);")
_REFERENCE_RE = re.compile(r"var\((--rlm-[\w-]+)")
# The body classes VS Code's webview sets per theme kind (src/vs/workbench/contrib/webview/browser/pre/index.html).
# High contrast light also gets vscode-high-contrast, for backwards compatibility.
_BODY_CLASSES_BY_THEME_KIND = {
    "light": frozenset({"vscode-light"}),
    "dark": frozenset({"vscode-dark"}),
    "high-contrast": frozenset({"vscode-high-contrast"}),
    "high-contrast-light": frozenset({"vscode-high-contrast-light", "vscode-high-contrast"}),
}
_BODY_SELECTOR_RE = re.compile(r"body((?:\.[\w-]+)+)((?::not\(\.[\w-]+\))*)")
_THEME_KIND_CLASS_RE = re.compile(r"\.vscode-(?:light|dark|high-contrast)")
_CLASS_RE = re.compile(r"\.([\w-]+)")


def _hand_written_css() -> str:
    return "".join((_STYLES_DIR / name).read_text() for name in ("markdown-preview.css", "markdown-highlight.css"))


def _declarations_by_selector(css: str) -> dict[str, dict[str, str]]:
    """Map every selector in the CSS to the variable declarations its rule carries (none for rules that only read them)."""
    result: dict[str, dict[str, str]] = {}
    for rule in _RULE_RE.finditer(re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)):
        declarations = {m.group(1): m.group(2) for m in _DECLARATION_RE.finditer(rule.group(2))}
        for selector in _SELECTOR_LIST_COMMA_RE.split(rule.group(1)):
            result[selector.strip()] = declarations
    return result


def _body_selector_matches(selector: str, body_classes: frozenset[str]) -> bool:
    """Whether a `body.a.b:not(.c)` selector matches a body carrying these classes; any other shape fails the test."""
    match = _BODY_SELECTOR_RE.fullmatch(selector)
    assert match is not None, f"unsupported body selector: {selector!r}"
    required = {m.group(1) for m in _CLASS_RE.finditer(match.group(1))}
    excluded = {m.group(1) for m in _CLASS_RE.finditer(match.group(2))}
    return required <= body_classes and not excluded & body_classes


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


class TestThemeKinds:
    """Each theme kind's body classes must select exactly one variant; with two, the later rule silently wins."""

    @pytest.mark.parametrize(
        ("theme_kind", "variant_selector"),
        [
            ("light", "body.vscode-light"),
            ("dark", "body.vscode-dark"),
            ("high-contrast", "body.vscode-dark"),
            ("high-contrast-light", "body.vscode-light"),
        ],
    )
    def test_theme_kind_gets_exactly_its_variant_variables(self, theme_kind: str, variant_selector: str) -> None:
        by_selector = _declarations_by_selector(build_css())
        body_classes = _BODY_CLASSES_BY_THEME_KIND[theme_kind]
        matched = [rules for selector, rules in by_selector.items() if _body_selector_matches(selector, body_classes)]
        assert matched == [by_selector[variant_selector]]

    def test_hand_written_rules_put_theme_kind_classes_on_body(self) -> None:
        # The variant check below only sees body-qualified selectors; a bare `.vscode-high-contrast ...` would dodge it.
        selectors = _declarations_by_selector(_hand_written_css())
        assert [s for s in selectors if _THEME_KIND_CLASS_RE.search(s) and not s.startswith("body.")] == []

    @pytest.mark.parametrize("theme_kind", _BODY_CLASSES_BY_THEME_KIND)
    def test_theme_kind_matches_one_variant_of_each_hand_written_rule(self, theme_kind: str) -> None:
        variants_by_rule: defaultdict[str, list[str]] = defaultdict(list)
        for selector in _declarations_by_selector(_hand_written_css()):
            body, _, rest = selector.partition(" ")
            if body.startswith("body"):
                variants_by_rule[rest].append(body)
        assert variants_by_rule, "no variant-specific rules parsed; drop this test if they were removed on purpose"
        body_classes = _BODY_CLASSES_BY_THEME_KIND[theme_kind]
        # Zero matches means the kind lost the rule (e.g. a deleted variant line); two means the later one silently wins.
        mismatches = {
            rule: matched
            for rule, bodies in variants_by_rule.items()
            if len(matched := [body for body in bodies if _body_selector_matches(body, body_classes)]) != 1
        }
        assert mismatches == {}
