"""Snapshot integration test -- regenerates the theme and compares against the fixture.

The fixture at tests/fixtures/rider-light-minimal.snapshot.json is the source of truth.
If the generator changes produce different output, this test fails with a diff.

To update the fixture after intentional changes, copy the generated
theme JSON into the fixtures directory.
"""

import json
from pathlib import Path
from typing import cast

import pytest

from tests.conftest import generate_theme_dict

_FIXTURE = Path(__file__).parent / "fixtures" / "rider-light-minimal.snapshot.json"


class TestSnapshot:
    """Regenerate the theme and compare against the committed fixture."""

    @pytest.fixture(scope="class")
    def generated(self) -> dict[str, object]:
        return generate_theme_dict()

    @pytest.fixture(scope="class")
    def fixture(self) -> dict[str, object]:
        return cast("dict[str, object]", json.loads(_FIXTURE.read_text()))

    def test_fixture_exists(self) -> None:
        assert _FIXTURE.exists(), f"Fixture missing: {_FIXTURE}"

    def test_colors_match(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        gen_colors = cast("dict[str, object]", generated["colors"])
        fix_colors = cast("dict[str, object]", fixture["colors"])
        assert gen_colors == fix_colors, _diff_dicts(gen_colors, fix_colors, "colors")

    def test_token_colors_match(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        gen_tokens = generated["tokenColors"]
        fix_tokens = fixture["tokenColors"]
        assert gen_tokens == fix_tokens, "tokenColors mismatch (re-run main.py and update fixture)"

    def test_semantic_tokens_match(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        gen_sem = cast("dict[str, object]", generated["semanticTokenColors"])
        fix_sem = cast("dict[str, object]", fixture["semanticTokenColors"])
        assert gen_sem == fix_sem, _diff_dicts(gen_sem, fix_sem, "semanticTokenColors")

    def test_full_json_round_trip(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        """Serialized JSON must match byte-for-byte (modulo trailing newline)."""
        gen_text = json.dumps(generated, indent=2)
        fix_text = json.dumps(fixture, indent=2)
        assert gen_text == fix_text, "Full JSON mismatch -- run main.py and update fixture"


_DARK_FIXTURE = Path(__file__).parent / "fixtures" / "rider-light-minimal-dark.snapshot.json"


class TestDarkSnapshot:
    """Regenerate the dark theme and compare against the committed fixture."""

    @pytest.fixture(scope="class")
    def generated(self) -> dict[str, object]:
        return generate_theme_dict(is_dark=True)

    @pytest.fixture(scope="class")
    def fixture(self) -> dict[str, object]:
        return cast("dict[str, object]", json.loads(_DARK_FIXTURE.read_text()))

    def test_fixture_exists(self) -> None:
        assert _DARK_FIXTURE.exists(), f"Fixture missing: {_DARK_FIXTURE}"

    def test_colors_match(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        gen_colors = cast("dict[str, object]", generated["colors"])
        fix_colors = cast("dict[str, object]", fixture["colors"])
        assert gen_colors == fix_colors, _diff_dicts(gen_colors, fix_colors, "dark colors")

    def test_token_colors_match(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        assert generated["tokenColors"] == fixture["tokenColors"], "dark tokenColors mismatch"

    def test_semantic_tokens_match(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        gen_sem = cast("dict[str, object]", generated["semanticTokenColors"])
        fix_sem = cast("dict[str, object]", fixture["semanticTokenColors"])
        assert gen_sem == fix_sem, _diff_dicts(gen_sem, fix_sem, "dark semanticTokenColors")

    def test_full_json_round_trip(self, generated: dict[str, object], fixture: dict[str, object]) -> None:
        gen_text = json.dumps(generated, indent=2)
        fix_text = json.dumps(fixture, indent=2)
        assert gen_text == fix_text, "Dark full JSON mismatch -- run main.py and update fixture"


def _diff_dicts(gen: dict[str, object], fix: dict[str, object], label: str) -> str:
    """Build a human-readable diff summary for assertion messages."""
    lines: list[str] = [f"{label} mismatch:"]
    all_keys = sorted(set(gen) | set(fix))
    for key in all_keys:
        if key not in gen:
            lines.append(f"  MISSING in generated: {key} = {fix[key]}")
        elif key not in fix:
            lines.append(f"  EXTRA in generated:   {key} = {gen[key]}")
        elif gen[key] != fix[key]:
            lines.append(f"  CHANGED: {key}: {fix[key]} -> {gen[key]}")
    return "\n".join(lines[:30])
