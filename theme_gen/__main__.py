"""Regenerate themes/*.json and styles/markdown-variables.css in place: `uv run -m theme_gen` or `just gen`.

Output paths are resolved from this file's location, so they point at the repo only under the editable install that `uv sync` creates; a non-editable install would write under .venv instead.
"""

import json
from pathlib import Path

from theme_gen.css.markdown_variables import build_css as build_markdown_css
from theme_gen.pipeline import build_theme_document

_REPO_ROOT = Path(__file__).resolve().parent.parent
_THEMES_DIR = _REPO_ROOT / "themes"
_MARKDOWN_VARS_OUTPUT = _REPO_ROOT / "styles" / "markdown-variables.css"


def main() -> None:
    _THEMES_DIR.mkdir(parents=True, exist_ok=True)
    for is_dark in (False, True):
        document = build_theme_document(is_dark=is_dark)
        out_path = _THEMES_DIR / f"{document['name']}-color-theme.json"
        _ = out_path.write_text(json.dumps(document, indent=2) + "\n")
        nc, nt, ns = len(document["colors"]), len(document["tokenColors"]), len(document["semanticTokenColors"])
        print(f"Wrote {nc} colors, {nt} tokenColors, {ns} semanticTokenColors to {out_path}")

    _MARKDOWN_VARS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _ = _MARKDOWN_VARS_OUTPUT.write_text(build_markdown_css())
    print(f"Wrote markdown variables to {_MARKDOWN_VARS_OUTPUT}")


if __name__ == "__main__":
    main()
