"""Contracts between src/extension.js, package.json, .vscodeignore and the hand-written preview stylesheets.

Each value lives in two hand-maintained places, so a rename in only one of them breaks the preview without any error; these tests catch it instead.
"""

import json
import re
from pathlib import Path, PurePosixPath
from typing import NamedTuple, TypedDict, cast

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GENERATED_STYLESHEET = "styles/markdown-variables.css"  # variables on body only; nothing to scope
_WRAPPER_CLASS_RE = re.compile(r'class="([\w-]+)"')
_CONFIGURATION_SECTION_RE = re.compile(r"getConfiguration\((\w+)")
_SETTING_GET_RE = re.compile(r"\.get\((\w+), (true|false)\)")
_RULE_RE = re.compile(r"([^{}]+)\{[^{}]*\}")
_SELECTOR_LIST_COMMA_RE = re.compile(r",(?![^()]*\))")  # not inside :has(...) / :is(...)


class _Setting(TypedDict):
    default: object


class _Configuration(TypedDict):
    properties: dict[str, _Setting]


class _Theme(TypedDict):
    path: str


# Functional form because the markdown keys contain dots.
_Contributes = TypedDict(
    "_Contributes",
    {
        "markdown.markdownItPlugins": bool,
        "markdown.previewStyles": list[str],
        "configuration": _Configuration,
        "themes": list[_Theme],
    },
)


class _Manifest(TypedDict):
    main: str
    browser: str
    icon: str
    activationEvents: list[str]
    extensionDependencies: list[str]
    contributes: _Contributes


class _SettingRead(NamedTuple):
    key: str
    fallback: bool


def _manifest() -> _Manifest:
    return cast("_Manifest", json.loads((_REPO_ROOT / "package.json").read_text()))


def _extension_source() -> str:
    return (_REPO_ROOT / "src" / "extension.js").read_text()


def _string_constant(source: str, name: str) -> str:
    match = re.search(rf"const {name} = '([^']*)';", source)
    assert match is not None, f"extension.js no longer declares `const {name} = '...';`"
    return match.group(1)


def _wrapper_class() -> str:
    match = _WRAPPER_CLASS_RE.search(_extension_source())
    assert match is not None, 'extension.js no longer wraps the preview in a literal class="..."'
    return match.group(1)


def _setting_read_by_extension() -> _SettingRead:
    """The full setting key extension.js reads via getConfiguration(section).get(key, fallback), and that fallback."""
    source = _extension_source()
    sections = list(_CONFIGURATION_SECTION_RE.finditer(source))
    gets = list(_SETTING_GET_RE.finditer(source))
    # With a second setting read, a first-match search would silently check the wrong pair; extend the tests instead.
    assert len(sections) == 1, "expected exactly one getConfiguration(<constant>, ...) call in extension.js"
    assert len(gets) == 1, "expected exactly one .get(<constant>, true|false) call in extension.js"
    key = f"{_string_constant(source, sections[0].group(1))}.{_string_constant(source, gets[0].group(1))}"
    return _SettingRead(key=key, fallback=gets[0].group(2) == "true")


def _selectors(css: str) -> list[str]:
    without_comments = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    return [
        selector.strip()
        for rule in _RULE_RE.finditer(without_comments)
        for selector in _SELECTOR_LIST_COMMA_RE.split(rule.group(1))
    ]


def _files_the_manifest_references() -> list[str]:
    manifest = _manifest()
    contributes = manifest["contributes"]
    paths = [
        manifest["main"],
        manifest["browser"],
        manifest["icon"],
        *contributes["markdown.previewStyles"],
        *(theme["path"] for theme in contributes["themes"]),
    ]
    # main and browser name the same file; a duplicate would also be a duplicate parametrize id.
    return list(dict.fromkeys(PurePosixPath(path).as_posix() for path in paths))


def _hand_written_preview_stylesheets() -> list[str]:
    styles = (PurePosixPath(path).as_posix() for path in _manifest()["contributes"]["markdown.previewStyles"])
    return [path for path in styles if path != _GENERATED_STYLESHEET]


def _vscodeignore_reincludes() -> list[str]:
    lines = (_REPO_ROOT / ".vscodeignore").read_text().splitlines()
    return [line.removeprefix("!") for line in map(str.strip, lines) if line.startswith("!")]


class TestPreviewWrapperClass:
    """The stylesheets apply only under the class extension.js wraps the preview in, which is what lets the setting switch them off."""

    @pytest.mark.parametrize("stylesheet", _hand_written_preview_stylesheets())
    def test_every_selector_is_scoped_to_the_wrapper_class(self, stylesheet: str) -> None:
        scope = re.compile(rf"\.{re.escape(_wrapper_class())}(?![\w-])")
        selectors = _selectors((_REPO_ROOT / stylesheet).read_text())
        assert selectors, f"no rules parsed from {stylesheet}"
        assert [selector for selector in selectors if not scope.search(selector)] == []


class TestPreviewSetting:
    def test_extension_reads_the_setting_the_manifest_declares(self) -> None:
        declared = _manifest()["contributes"]["configuration"]["properties"]
        assert _setting_read_by_extension().key in declared

    def test_extension_fallback_matches_the_manifest_default(self) -> None:
        setting = _setting_read_by_extension()
        declared = _manifest()["contributes"]["configuration"]["properties"]
        assert declared[setting.key]["default"] is setting.fallback


class TestManifestWiring:
    def test_registers_a_markdown_it_plugin(self) -> None:
        assert _manifest()["contributes"]["markdown.markdownItPlugins"] is True

    # This test and the next pin the 0.3.2 activation fix; why: AGENTS.md, Code layout > Extension > Activation.
    def test_declares_no_activation_events(self) -> None:
        assert _manifest()["activationEvents"] == []

    def test_depends_on_the_built_in_markdown_extension(self) -> None:
        assert "vscode.markdown-language-features" in _manifest()["extensionDependencies"]

    @pytest.mark.parametrize("path", _files_the_manifest_references())
    def test_referenced_file_exists(self, path: str) -> None:
        assert (_REPO_ROOT / path).is_file()

    @pytest.mark.parametrize("path", _files_the_manifest_references())
    def test_referenced_file_is_reincluded_by_the_vscodeignore_allowlist(self, path: str) -> None:
        # .vscodeignore starts with `**`, so a file ships only if a `!` pattern re-includes it.
        assert any(PurePosixPath(path).full_match(pattern) for pattern in _vscodeignore_reincludes())
