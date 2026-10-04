# AGENTS.md

Guidance for AI coding agents working in this repo. Covers what the product is, the tech stack, how the code is laid out, and the conventions that must be preserved.

## Product

Rider light minimal is a light + dark color theme extension for VS Code, inspired by JetBrains Rider.

Not currently published. The VS Code Marketplace and Open VSX listings were withdrawn after the Kiro team objected to the word "kiro" in the extension name and elsewhere; do not reintroduce it in names, keywords, or docs. The extension is distributed as a locally built `.vsix` (see Packaging).

### Goals

- Consistent syntax colors across all supported languages (Kotlin, Java, C#, TypeScript, JavaScript, Python, Markdown, YAML, JSON, HTML, CSS, shell scripts) -- a class is always purple, a function always green, regardless of language
- WCAG AA contrast (4.5:1 minimum) for all syntax colors on the background
- Dedicated semantic highlighting scopes for Kotlin LSP, Roslyn (C#), and basedpyright
- 523 UI colors covering editor, terminal, debug, testing, VCS, and more
- Full 16-color ANSI terminal palette at perceptually uniform lightness
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

## Tech stack

### Extension package

- Format: VS Code color theme extension (`package.json` with `contributes.themes`)
- Engine: VS Code `^1.110.0`
- Entry: `src/extension.js` (registers a markdown-it plugin that wraps the preview when `rider-light-minimal.markdownPreview.enabled` is true)
- Activation: `extensionDependencies: ["vscode.markdown-language-features"]` + empty `activationEvents`. The markdown engine discovers the plugin via the `'api'` pattern (same as `markdown-math` and `markdown-mermaid`). Using `onLanguage:markdown` causes a race where the engine initializes before the plugin registers.
- Outputs (generated, not hand-edited):
  - `themes/Rider Light Minimal-color-theme.json`
  - `themes/Rider Light Minimal Dark-color-theme.json`
  - `styles/markdown-variables.css` (paired with hand-written `styles/markdown-preview.css` and `styles/markdown-highlight.css`)

### Theme generator (`theme_gen/`)

- Language: Python 3.14 (pinned in the root `.python-version`)
- Project: the root `pyproject.toml`; `theme_gen/` is a flat-layout package (`uv_build`) installed editable into the root `.venv/`, so `theme_gen.*` imports resolve the same way for basedpyright, pytest, and the CLI -- no `PYTHONPATH`, `extraPaths`, or `cwd`
- Package manager: `uv` (lockfile `uv.lock`, committed). `dev` and `test` are default groups, so a plain `uv sync` builds the full environment
- Runtime dependencies:
  - `coloraide` -- OKLCH color math and gamut mapping
  - `scipy` -- contrast optimization (`with_min_contrast`)
- Linter/formatter: `ruff` (line length 120, target py314, `ALL` rules minus the `ignore` list in `pyproject.toml`) and `docformatter` (docstring reflow at 256)
- Type checker: `basedpyright` (configured in `[tool.basedpyright]`; existing warnings recorded in `.basedpyright/baseline.json`, so only new ones fail). In VS Code it runs through the basedpyright extension (`detachhead.basedpyright`); the Python extension's own language server is off in `.vscode/settings.json`
- Test runner: `pytest` (`[tool.pytest]`: importlib import mode, `strict`, warnings are errors)
- TOML formatter: `taplo` (scope in `.taplo.toml`)

### Common commands

Run from the repo root. `just` lists every recipe; the `uv` equivalents are in the `justfile`.

```bash
just gen  # Regenerate both theme JSONs and the markdown-variables CSS (uv run -m theme_gen)
just py-verify  # Lint + type-check (new diagnostics fail) + tests -- the gate after Python changes
just py-test  # Tests only; extra args pass through
just fmt  # taplo, then docformatter + ruff check --fix + ruff format
just py-update  # Upgrade uv.lock and sync; review the uv.lock diff, then run just py-verify
uv run -m theme_gen.token_query FILE SNIPPET  # Query an exported .tokens.yaml (or FILE --scope PATTERN)
```

### Testing the extension locally

1. Open the workspace root in VS Code.
2. Press `F5` to launch the Extension Development Host.
3. `Cmd+K Cmd+T` and pick `Rider Light Minimal` or `Rider Light Minimal Dark`.

### Packaging

```bash
npm install -g @vscode/vsce  # once
just package  # py-verify + gen + vsce package -> vscode-rider-light-minimal-theme-{version}.vsix
```

## Project structure

```text
vscode-rider-light-minimal-theme/
  package.json  # Extension manifest (themes, markdown preview, config)
  pyproject.toml  # Python project: deps, uv/ruff/basedpyright/pytest/docformatter config
  uv.lock  # Pinned lockfile (commit this)
  .python-version  # 3.14
  justfile  # gen / py-verify / fmt recipes
  .taplo.toml  # TOML formatter scope and width
  .basedpyright/baseline.json  # Recorded type-check debt; plain runs shrink it as debt is paid -- commit that diff
  src/
    extension.js  # Extension entry (markdown-it preview wrapper)
  styles/
    markdown-variables.css  # Generated by theme_gen/css/markdown_variables.py
    markdown-preview.css  # Hand-written preview styles
    markdown-highlight.css  # Hand-written highlight.js scope styles
  themes/
    Rider Light Minimal-color-theme.json  # Generated -- do not edit by hand
    Rider Light Minimal Dark-color-theme.json  # Generated -- do not edit by hand
  theme_gen/  # Python generator package (source of truth for theme colors)
    __main__.py  # `uv run -m theme_gen`: writes themes/*.json and styles/markdown-variables.css
    pipeline.py  # build_theme_document(): the one generation path, shared by __main__ and tests
    token_query.py  # CLI: query exported .tokens.yaml files
    core/
      tcol.py  # TCol: OKLCH color type with contrast/alpha/mix helpers
      font_style.py  # FontStyle enum (bold, italic, underline)
      hue_series.py  # Hue harmony utilities
    palette/
      palette.py  # Palette dataclass: seed + derived colors for a variant
      syntax.py  # SyntaxPalette: 17 named syntax roles + hue_shifted series
      editor.py  # EditorPalette helpers (tints, overlays)
      ansi.py  # AnsiColors: 16 terminal colors per variant (EditorPalette.ansi)
      theme.py  # Theme: composes Palette + SyntaxPalette (light or dark)
    lang/
      protocol.py  # Language protocol + TokenColorRule + SemanticTokenStyle
      base.py  # BaseSyntax: shared TextMate rules across all languages
      registry.py  # LanguageRegistry: merges all rules into final lists
      semantic.py  # GlobalSemanticTokens: cross-language semantic rules
      java.py, kotlin.py, csharp.py, python.py, js.py, ts.py,
      css.py, html.py, markdown.py, yaml.py, json_lang.py, script.py
    ui/
      protocol.py  # UISection protocol: build(theme) -> dict[str, TCol]
      composer.py  # ColorMapComposition: merges all UI sections
      base.py, editor.py, tabs.py, widgets.py, panels.py, vcs.py,
      chat.py, symbols.py, terminal.py, debug.py, testing.py, lists.py
    css/
      markdown_variables.py  # Emits styles/markdown-variables.css from the palette
    tests/
      conftest.py
      test_tcol.py, test_palette.py, test_theme.py, test_lang.py,
      test_registry.py, test_ui.py, test_css.py, test_generate_theme.py, test_token_query.py,
      test_snapshot.py  # Snapshot regression test against fixtures/
      fixtures/  # Snapshot JSONs -- copies of themes/*.json (see Conventions)
  examples/  # Sample source files for screenshot/visual testing
    src/main/{csharp,java,kotlin,py,ts,js,other}/...  # each sample has a *.tokens.yaml export beside it (token_query input)
    build.gradle.kts, settings.gradle.kts, gradlew{,.bat}
  references/  # Upstream docs (VS Code theme colors, scope naming, etc.)
  scripts_old/  # Legacy extraction scripts -- NOT part of the build
  img/  # Screenshots and marketplace icon
```

## Conventions

- `themes/*.json` and `styles/markdown-variables.css` are always regenerated by `just gen`. Never edit these files by hand -- change the Python source, regenerate, commit both.
- Docstrings are written for LLM readers that search with `rg`: one paragraph is one line, never hand-wrapped; code stays at 120. The line limit is 256 columns including indentation -- docformatter wraps a longer paragraph mid-sentence, so split it into separate paragraphs (blank line between) at a sentence boundary instead. `just fmt` reflows plain-prose docstrings, but leaves docstrings it reads as lists, tables, or indented blocks alone -- write those paragraphs on one line by hand.
- All color values flow through `TCol` (OKLCH). Never hardcode hex strings in generator code; derive from `Palette` or `SyntaxPalette`.
- Each language module in `theme_gen/lang/` implements `BaseLanguage` (TextMate rules) and optionally overrides `semantic_token_overrides`.
- Each UI section in `theme_gen/ui/` implements the `UISection` protocol: `build(theme) -> dict[str, TCol]`.
- All light/dark branching lives in `theme_gen/palette/` (`is_dark` plus the `with_min_contrast` / `mix` / `_tint` / `_overlay` helpers). UI sections and the CSS emitter read ready-made fields (`palette.git_added`, `editor.ansi`, `syntax.hue_shifted_quote`) and never test the variant -- a new dark-only tweak is a new palette field, not an `if` in a section.
- Tests include a snapshot test (`test_snapshot.py`) against `theme_gen/tests/fixtures/`. After an intentional output change: `just gen`, review the `themes/` diff, then copy `themes/Rider Light Minimal-color-theme.json` to `theme_gen/tests/fixtures/rider-light-minimal.snapshot.json` and `themes/Rider Light Minimal Dark-color-theme.json` to `theme_gen/tests/fixtures/rider-light-minimal-dark.snapshot.json`.
- `scripts_old/` is archived reference material; do not add new scripts there. Put throwaway exploration scripts under `work/scripts/`.
