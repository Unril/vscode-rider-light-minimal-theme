# Contributing

Pull requests are welcome. Repository: [github.com/Unril/vscode-rider-light-minimal-theme](https://github.com/Unril/vscode-rider-light-minimal-theme)

## Installation

Install from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=NikolaiFedorov.vscode-rider-light-minimal-theme) or [Open VSX](https://open-vsx.org/extension/NikolaiFedorov/vscode-rider-light-minimal-theme), or search for "Rider light minimal" in the Extensions view.

Or install a `.vsix` directly:

```bash
code --install-extension vscode-rider-light-minimal-theme-*.vsix
```

## Generator

Both theme JSON files and the markdown-preview CSS variables are generated from Python source in `theme_gen/`.

Run as an executable script from the workspace root:

```bash
./theme_gen/main.py
# or
uv run ./theme_gen/main.py
```

The shebang uses `uv run --script` + a [PEP 723](https://peps.python.org/pep-0723/) inline metadata block, so `uv` materializes a cached venv with `coloraide` and `scipy` on the first run. No project setup required.

For development (editable imports, tests, linters), work inside the project venv:

```bash
cd theme_gen
uv sync --all-groups  # once, creates .venv from uv.lock
uv run main.py  # regenerate
uv run -m pytest
uv run ruff check .
uv run mypy .
```

Either path writes:

- `themes/Rider Light Minimal-color-theme.json`
- `themes/Rider Light Minimal Dark-color-theme.json`
- `styles/markdown-variables.css`

Never edit those outputs by hand. Change the Python source and regenerate.

## Test Locally

1. Open this folder in VS Code
2. Press `F5` to launch the Extension Development Host
3. `Cmd+K Cmd+T` and select "Rider Light Minimal" or "Rider Light Minimal Dark"

## Build the extension

Packaging the extension as a `.vsix` requires [`vsce`](https://github.com/microsoft/vscode-vsce) (the VS Code Extension Manager).

Install `vsce` once:

```bash
npm install -g @vscode/vsce
```

From the workspace root:

```bash
# Regenerate generated outputs first (only required when Python source changed)
./theme_gen/main.py

# Package the extension -- writes vscode-rider-light-minimal-theme-{version}.vsix in the repo root
vsce package
```

Install the resulting `.vsix` locally for a smoke test:

```bash
code --install-extension vscode-rider-light-minimal-theme-*.vsix
```

Reload the editor window (`Cmd+Shift+P` -> `Developer: Reload Window`) and select the theme via `Cmd+K Cmd+T`.

### Publishing

Publishing to a registry is a separate step. See the [vsce publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) for the marketplace; Open VSX uses [`ovsx`](https://github.com/eclipse/openvsx/wiki/Publishing-Extensions).

Before publishing:

1. Bump `version` in `package.json`
2. Add a `CHANGELOG.md` entry under a new `## [x.y.z] - YYYY-MM-DD` heading
3. Regenerate theme outputs if the Python source changed
4. Commit and tag the release
5. Run `vsce package` to produce the final `.vsix`
6. Publish via `vsce publish` (marketplace) and/or `ovsx publish *.vsix` (Open VSX)
