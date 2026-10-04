"""token_query CLI over exported .tokens.yaml files, with and without per-segment spans."""

import sys
from pathlib import Path

import pytest

from theme_gen.token_query import main

# Only some exporters write `span`; the Python/TS/... exports in examples/ omit it, the C# one has it.
_SEGMENT = "      - text: import\n        textmate: { scope: keyword.control.import.python, rest: [ source.python ] }\n"
_EXPORT_HEADER = "lines:\n  - lineNumber: 3\n    sourceText: import math\n    segments:\n"


def _run_cli(
    export_text: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> str:
    export = tmp_path / "sample.py.tokens.yaml"
    _ = export.write_text(export_text)
    monkeypatch.setattr(sys, "argv", ["token_query", str(export), "import"])
    main()
    return capsys.readouterr().out


def test_prints_segments_of_export_without_spans(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = _run_cli(_EXPORT_HEADER + _SEGMENT, tmp_path, monkeypatch, capsys)

    assert out == "L3: import math\n  'import' tm=keyword.control.import.python\n"


def test_prints_span_when_export_has_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = _run_cli(_EXPORT_HEADER + _SEGMENT + "        span: [ 0, 6 ]\n", tmp_path, monkeypatch, capsys)

    assert out == "L3: import math\n  0-6 'import' tm=keyword.control.import.python\n"
