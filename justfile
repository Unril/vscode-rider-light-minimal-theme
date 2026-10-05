# Task runner for the theme generator (theme_gen/) and repo configs. `just` lists recipes.

# Recipe arguments reach the shell as "$@", so a quoted `-k "a and not b"` stays one argument.
set positional-arguments

[private]
_default:
    @just --list

# Regenerate themes/*.json and styles/markdown-variables.css from theme_gen/
[group('python')]
gen:
    uv run -m theme_gen

# Run the Python tests (extra args pass through, e.g. `just py-test -k "snapshot and not Dark"`)
[group('python')]
py-test *args:
    uv run pytest "$@"

# Lint without writing (ruff check + ruff format --check); the read-only half of py-fmt
[group('python')]
py-lint:
    uv run ruff check .
    uv run ruff format --check .

# Warnings fail too. Existing debt (mostly `Any` from the untyped ruamel.yaml load in token_query.py) is recorded in
# .basedpyright/baseline.json, so only NEW diagnostics fail. A run that finds debt paid off shrinks the baseline itself
# -- commit that diff. `uv run basedpyright --writebaseline` records EVERY current diagnostic, new ones included; use it
# only to accept them deliberately (e.g. after enabling a rule) and review its diff.

# Type-check with basedpyright; only diagnostics not in the baseline fail
[group('python')]
py-typecheck:
    uv run basedpyright

# Reflow docstrings, then lint-fix and format (docformatter + ruff check --fix + ruff format)
[group('python')]
py-fmt:
    #!/usr/bin/env bash
    set -euo pipefail
    # docformatter FIRST: it is the only step that reflows docstring prose (ruff treats docstring text as verbatim).
    # ruff format runs LAST so the lint fixes' output (import sorting, unquoted annotations) is formatted too.
    # docformatter's exit 3 means "files were reformatted" -- success here.
    uv run docformatter --in-place theme_gen || [ $? -eq 3 ]
    uv run ruff check --fix .
    uv run ruff format .

# Lint, type-check, then test -- the gate after Python changes
[group('python')]
py-verify: py-lint py-typecheck py-test

# Upgrade the locked Python dependencies and sync; does NOT verify -- review the uv.lock diff, then run py-verify
[group('python')]
py-update:
    uv lock --upgrade
    uv sync --locked

# Install test/'s JS dev dependencies (markdown-it, prettier, vsce, ovsx) from its lockfile, without install scripts
[private]
_js-deps:
    npm --prefix test ci --ignore-scripts --no-audit --no-fund

# Run the extension behavior tests (node:test)
[group('extension')]
js-test: _js-deps
    node --test test/extension.test.js

# Check the extension's JS formatting without writing; the read-only half of js-fmt
[group('extension')]
js-lint: _js-deps
    test/node_modules/.bin/prettier --check 'src/**/*.js' 'test/*.js'

# Format the extension's JS with prettier (.prettierrc.json; indent and width come from .editorconfig)
[group('extension')]
js-fmt: _js-deps
    test/node_modules/.bin/prettier --write 'src/**/*.js' 'test/*.js'

# Upgrade test/package-lock.json within the package.json ranges; does NOT verify -- review the diff, then run test
[group('extension')]
js-update:
    npm --prefix test update --ignore-scripts --no-audit --no-fund

# Release build: run every test, regenerate themes/ and styles/, then package the .vsix
[group('extension')]
package: test gen
    test/node_modules/.bin/vsce package

# Format TOML files (taplo; scope in .taplo.toml)
[group('config')]
config-fmt:
    uv run taplo fmt

# Format everything: TOML, then Python, then JS
fmt: config-fmt py-fmt js-fmt

# Run every check: the Python gate (lint, type-check, tests), the JS format check, then the extension behavior tests
test: py-verify js-lint js-test

# Upgrade every locked dependency, Python then JS; does NOT verify -- review the lockfile diffs, then run test
update: py-update js-update
