# Contributing

Pull requests are welcome. Repository: [github.com/Unril/vscode-rider-light-minimal-theme](https://github.com/Unril/vscode-rider-light-minimal-theme)

## Installation

The extension is not currently published to the VS Code Marketplace or Open VSX. Build the `.vsix` (see [Build the extension](#build-the-extension)) and install it directly:

```bash
code --install-extension vscode-rider-light-minimal-theme-{version}.vsix
```

## Generator

Both theme JSON files and the markdown-preview CSS variables are generated from the Python package in `theme_gen/`. The project (`pyproject.toml`, `uv.lock`) lives at the repo root and needs [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/). From the repo root:

```bash
uv sync  # once: creates .venv from uv.lock, with theme_gen installed editable
just gen  # regenerate (same as uv run -m theme_gen)
just py-verify  # lint, type-check, test
```

`just gen` writes:

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

From the repo root:

```bash
# Verify the generator, regenerate the outputs, and package -- writes vscode-rider-light-minimal-theme-{version}.vsix
just package
```

Install the resulting `.vsix` locally for a smoke test. Name it exactly: old builds stay in the repo root (`*.vsix` is gitignored), so a `*.vsix` glob can pick the previous version.

```bash
code --uninstall-extension nikolaifedorov.vscode-rider-light-minimal-theme
code --install-extension "vscode-rider-light-minimal-theme-$(jq -r .version package.json).vsix"
```

Reload the editor window (`Cmd+Shift+P` -> `Developer: Reload Window`) and select the theme via `Cmd+K Cmd+T`.

### Publishing

The extension is currently withdrawn from both registries (see [Installation](#installation)); do not republish under the old name. Publishing to a registry is a separate step. See the [vsce publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) for the marketplace; Open VSX uses [`ovsx`](https://github.com/eclipse/openvsx/wiki/Publishing-Extensions).

Before publishing:

1. Bump `version` in `package.json`
2. Add a `CHANGELOG.md` entry under a new `## [x.y.z] - YYYY-MM-DD` heading, and re-add `!CHANGELOG.md` to `.vscodeignore` (it is left out of the `.vsix` while the extension is unpublished)
3. Run `just package` (verifies, regenerates theme outputs, and produces the final `.vsix`)
4. Commit and tag the release
5. Publish via `vsce publish` (marketplace) and/or `ovsx publish "vscode-rider-light-minimal-theme-$(jq -r .version package.json).vsix"` (Open VSX)
