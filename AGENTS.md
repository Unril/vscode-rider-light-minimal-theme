# AGENTS.md

Guidance for AI coding agents working in this repo: what the product is, how the code is organized, and the conventions that must be preserved. Versions, dependencies, and tool settings live in `package.json`, `pyproject.toml`, and the `justfile`; read them there.

## Product

Rider Light Minimal is a light + dark color theme extension for VS Code, inspired by JetBrains Rider.

Not currently published. The VS Code Marketplace and Open VSX listings were withdrawn after the owner of another product objected to its name appearing in the extension name and elsewhere. Do not add another product's name to the extension's name, display name, description, keywords, or docs. The existing references are deliberate: JetBrains Rider (the inspiration, also in the name) and the languages and tools the theme supports. The extension is distributed as a locally built `.vsix` (see [Package](#package)).

### Goals

- Consistent syntax colors across every supported language -- a class is always purple, a function always green, regardless of language
- WCAG AA contrast (4.5:1 minimum) for all syntax colors on the background
- Dedicated semantic highlighting scopes for Kotlin LSP, Roslyn (C#), and basedpyright
- Full UI coverage (editor, terminal, debug, testing, VCS, and more), plus a 16-color ANSI palette at perceptually uniform lightness
- Themed markdown preview (colored headings, highlighted code blocks, styled tables, lists, blockquotes)

### Syntax palette (fixed roles)

| Role | Color |
| --- | --- |
| Functions | Green |
| Types / Classes | Purple |
| Keywords | Blue |
| Fields / Properties | Teal |
| Strings | Brown |
| Numbers | Magenta |
| Comments | Muted green |
| Metadata / Annotations | Olive |

## Code layout

### Extension

- `src/extension.js` wraps the rendered markdown preview in `<div class="rlm-preview">` while `rider-light-minimal.markdownPreview.enabled` is true. The hand-written `styles/markdown-preview.css` and `styles/markdown-highlight.css` apply only under that class.
- Activation: empty `activationEvents` plus `extensionDependencies: ["vscode.markdown-language-features"]`. Together they are the 0.3.2 fix for a `.vsix` install missing the plugin, so keep both and do not add `onLanguage:markdown`, the setting that fix removed. The extension needs no activation event of its own because VS Code's markdown extension activates every extension that contributes `markdown.markdownItPlugins` and calls its `extendMarkdownIt`. `test_extension_contract.py` pins both halves.
- `.vscodeignore` is an allowlist (`**`, then `!` patterns): a new file the extension needs ships only once a `!` pattern re-includes it.

### Theme generator (`theme_gen/`)

`theme_gen/` is the source of truth for every theme color. It is a flat-layout package installed editable into the root `.venv/`, so `theme_gen.*` imports resolve the same way for basedpyright, pytest, and the CLI. `uv sync` builds the full environment because `dev` and `test` are default groups.

- `pipeline.py` -- `build_theme_document()`, the one generation path, shared by `__main__.py` (`uv run -m theme_gen`) and the tests
- `core/tcol.py` -- `TCol`, the OKLCH color type
- `palette/` -- per-variant colors: `Palette`, `SyntaxPalette`, `EditorPalette`, composed by `Theme`
- `lang/` -- one module per language, merged by `registry.py`; `semantic.py` holds cross-language semantic rules
- `ui/` -- one `UISection` per UI area, merged by `composer.py`, which rejects duplicate keys
- `css/markdown_variables.py` -- emits `styles/markdown-variables.css`
- `token_query.py` -- CLI that queries the `*.tokens.yaml` exports in `examples/`

### Tests

- `theme_gen/tests/` (pytest): generator behavior, a snapshot test against `fixtures/`, and contract tests that keep `src/extension.js`, `package.json`, `.vscodeignore`, and the preview CSS in agreement
- `test/extension.test.js` (`node --test`): runs `src/extension.js` against a fake `vscode` module and a real markdown-it. `test/` has its own `package.json` (markdown-it, prettier, and the vsce and ovsx release tools) so the root manifest stays free of dev dependencies, and sits outside `src/` because `src/**` ships in the `.vsix`

### CI and release

- `.github/workflows/ci.yml` runs `just package` (every check, regeneration, and `vsce package`) on pushes and pull requests, then `git diff --exit-code`, so generated files that were not regenerated fail the build. It runs on `ubuntu-slim`, whose jobs are cut off at 15 minutes.
- `.github/workflows/publish.yml` runs when `package.json` changes on `master`. If the tag `v{version}` does not exist, it runs `just package`, publishes to Open VSX through trusted publishing, then creates the tag and GitHub release. Open VSX matches the workflow file name and the `open-vsx` environment name, so renaming either breaks publishing. `test_extension_contract.py` checks that `CHANGELOG.md` has a section for the current version, because the release notes come from it.
- Every action is pinned to a full commit SHA with its version in a trailing comment. `.github/dependabot.yml` keeps the actions, the `test/` npm packages, and the uv dependencies current.

### Other folders

- `examples/` -- sample sources for screenshots and visual checks, with `*.tokens.yaml` exports beside them
- `img/` -- screenshots and the extension icon
- `references/` -- local copies of upstream VS Code docs (theme colors, scope naming); gitignored, so it may be absent
- `scripts_old/` -- legacy scripts that predate `theme_gen/`; gitignored and not part of the build. Do not edit, run, or add to them
- `work/` -- gitignored scratch space; throwaway scripts go in `work/scripts/`

## Workflows

Run from the repo root; `just` lists every recipe.

```bash
just gen  # Regenerate themes/*.json and styles/markdown-variables.css
just test  # Every check -- the gate after any change
just py-verify  # Python gate only: lint, type-check, tests
just js-test  # Extension behavior tests only
just fmt  # Format TOML, Python, and JS
just update  # Upgrade uv.lock and test/package-lock.json; review the diffs, then run just test
uv run -m theme_gen.token_query FILE SNIPPET  # Query a .tokens.yaml export (or FILE --scope PATTERN)
```

Type checking fails only on diagnostics missing from `.basedpyright/baseline.json`. When a run pays off recorded debt, it shrinks the baseline; commit that diff.

### Test the extension locally

1. Open the workspace root in VS Code.
2. Press `F5` to launch the Extension Development Host.
3. `Cmd+K Cmd+T` and pick `Rider Light Minimal` or `Rider Light Minimal Dark`.

### Package

```bash
just package  # test + gen + vsce package -> vscode-rider-light-minimal-theme-{version}.vsix
```

`publish.yml` cuts releases. Release steps (version bump, CHANGELOG entry) and the one-time setup (the first upload, the trusted publisher) are in [CONTRIBUTING.md](CONTRIBUTING.md#publishing).

## Conventions

- `themes/*.json` and `styles/markdown-variables.css` are always regenerated by `just gen`. Never edit these files by hand -- change the Python source, regenerate, commit both.
- Docstrings are written for LLM readers that search with `rg`: one paragraph is one line, never hand-wrapped; code stays at 120. The line limit is 256 columns including indentation -- docformatter wraps a longer paragraph mid-sentence, so split it into separate paragraphs (blank line between) at a sentence boundary instead. `just fmt` reflows plain-prose docstrings, but leaves docstrings it reads as lists, tables, or indented blocks alone -- write those paragraphs on one line by hand.
- All color values flow through `TCol` (OKLCH). Never hardcode hex strings in generator code; derive from `Palette` or `SyntaxPalette`.
- Each language module in `theme_gen/lang/` implements `BaseLanguage` (TextMate rules) and optionally overrides `semantic_token_overrides`.
- Each UI section in `theme_gen/ui/` implements the `UISection` protocol: `build(theme) -> dict[str, TCol]`.
- All light/dark branching lives in `theme_gen/palette/` (`is_dark` plus the `with_min_contrast` / `mix` / `_tint` / `_overlay` helpers). UI sections and the CSS emitter read ready-made fields (`palette.git_added`, `editor.ansi`, `syntax.hue_shifted_quote`) and never test the variant -- a new dark-only tweak is a new palette field, not an `if` in a section.
- Hand-written preview CSS scopes every selector under `.rlm-preview`, so turning the setting off removes the styling. Theme-kind classes go on `body` (`body.vscode-dark .rlm-preview ...`). VS Code also gives high contrast light the `vscode-high-contrast` class, so dark rules use `body.vscode-high-contrast:not(.vscode-high-contrast-light)`. `test_extension_contract.py` enforces the `.rlm-preview` scoping; `test_css.py` enforces the `body` and high contrast rules.
- Tests include a snapshot test (`test_snapshot.py`) against `theme_gen/tests/fixtures/`. After an intentional output change: `just gen`, review the `themes/` diff, then copy `themes/Rider Light Minimal-color-theme.json` to `theme_gen/tests/fixtures/rider-light-minimal.snapshot.json` and `themes/Rider Light Minimal Dark-color-theme.json` to `theme_gen/tests/fixtures/rider-light-minimal-dark.snapshot.json`.
