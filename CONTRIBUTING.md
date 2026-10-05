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
just test  # everything: py-verify, the JS format check, then the extension tests (needs Node)
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

`just js-test` runs the behavior tests for `src/extension.js` (needs Node; it installs `test/`'s dev dependencies from the lockfile first). The contract tests that keep `src/extension.js`, `package.json`, `.vscodeignore` and the preview CSS in agreement run under `just py-verify`.

## Build the extension

Packaging the extension as a `.vsix` uses [`vsce`](https://github.com/microsoft/vscode-vsce) (the VS Code Extension Manager), which `just package` installs from `test/package-lock.json`. From the repo root:

```bash
# Verify the generator and the extension, regenerate the outputs, and package -- writes vscode-rider-light-minimal-theme-{version}.vsix
just package
```

Install the resulting `.vsix` locally for a smoke test. Name it exactly: old builds stay in the repo root (`*.vsix` is gitignored), so a `*.vsix` glob can pick the previous version.

```bash
code --uninstall-extension nikolaifedorov.vscode-rider-light-minimal-theme
code --install-extension "vscode-rider-light-minimal-theme-$(jq -r .version package.json).vsix"
```

Reload the editor window (`Cmd+Shift+P` -> `Developer: Reload Window`) and select the theme via `Cmd+K Cmd+T`.

### Publishing

The extension is not published yet under its current name. The listings under the previous name were withdrawn (see [Installation](#installation)); never publish under that name.

A push to `master` that changes `version` in `package.json` publishes that version to Open VSX, unless the tag `v{version}` already exists. `.github/workflows/publish.yml` runs every check, packages the `.vsix`, publishes it through [trusted publishing](https://github.com/eclipse-openvsx/openvsx/wiki/Trusted-Publishing), then creates the GitHub release `v{version}` with the matching `CHANGELOG.md` section as its notes. The VS Code Marketplace is published by hand with `test/node_modules/.bin/vsce publish` (see the [vsce publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)).

To release:

1. Bump `version` in `package.json`
2. Add a `CHANGELOG.md` entry under a new `## [x.y.z] - YYYY-MM-DD` heading (a contract test fails without it)
3. Run `just test`, then commit and push to `master`

If a release run fails and the fix does not touch `package.json`, start Publish by hand from the Actions tab on `master`. Re-running the failed run would reuse its old commit, and the fixing push does not trigger the workflow.

Set up once, before the first release:

1. Upload the first version by hand, because Open VSX registers a trusted publisher only for an extension that already has an active version. Run `just package`, then `OVSX_PAT={token} test/node_modules/.bin/ovsx publish vscode-rider-light-minimal-theme-{version}.vsix` with a token from [open-vsx.org/user-settings/tokens](https://open-vsx.org/user-settings/tokens), and delete the token afterwards
2. Register the trusted publisher at [open-vsx.org/user-settings/trusted-publishers](https://open-vsx.org/user-settings/trusted-publishers): provider GitHub Actions, owner `Unril`, repository `vscode-rider-light-minimal-theme`, workflow `publish.yml`, environment `open-vsx`
3. Create the `open-vsx` environment under the repository's Settings > Environments and limit its deployment branches to `master`; that rule is the only thing stopping a branch from publishing

Until step 2 is done, a version bump on `master` fails in the `publish-open-vsx` job, and no tag or GitHub release is created.
