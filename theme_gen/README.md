# theme-gen

Python generator for the Rider Light Minimal themes. It derives every color from OKLCH seeds and writes `themes/*.json` and `styles/markdown-variables.css` at the repo root.

## Setup

The project is defined by the repo-root `pyproject.toml`; this directory is the `theme_gen` package, installed editable into the root `.venv/`. Install [uv] and [just], then from the repo root:

```bash
uv sync  # dev and test are default groups, so this is the full environment
```

uv downloads Python 3.14 (pinned in `.python-version`) if it is missing. For editor type checking, install the basedpyright VS Code extension (`detachhead.basedpyright`); `.vscode/settings.json` turns off the Python extension's own language server.

## Commands

Run from the repo root:

```bash
just gen  # regenerate the theme JSONs and the markdown CSS
just py-verify  # lint, type-check, test
just fmt  # format TOML, docstrings, and code
```

`just --list` shows every recipe. Most are one or two `uv run ...` lines in the `justfile` that also work without `just`; the exception is `docformatter --in-place`, which exits 3 when it changed files.

## Layout and conventions

See [AGENTS.md](../AGENTS.md) for the package layout, the syntax palette roles, and the generator conventions.

[uv]: https://docs.astral.sh/uv/
[just]: https://just.systems/
