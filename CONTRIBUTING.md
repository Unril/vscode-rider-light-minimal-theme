# Contributing

Pull requests are welcome; they need the CI check `test` to pass before merging. Repository: [github.com/Unril/vscode-rider-light-minimal-theme](https://github.com/Unril/vscode-rider-light-minimal-theme). To report a vulnerability, see [SECURITY.md](SECURITY.md).

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

The listings under the previous name were withdrawn (see [Installation](#installation)); never publish under that name.

A push to `master` that changes `version` in `package.json` publishes that version, unless the tag `v{version}` already exists. `.github/workflows/publish.yml` runs every check and packages the `.vsix`. It then publishes the `.vsix` to Open VSX through [trusted publishing](https://github.com/eclipse-openvsx/openvsx/wiki/Trusted-Publishing) and to the VS Code Marketplace with a Microsoft Entra ID token (see the [vsce publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)). When both succeed, it creates the GitHub release `v{version}` with the matching `CHANGELOG.md` section as its notes. The repository stores no registry token.

To release:

1. Bump `version` in `package.json`
2. Add a `CHANGELOG.md` entry under a new `## [x.y.z] - YYYY-MM-DD` heading (a contract test fails without it)
3. Run `just test`, then commit and push to `master`

If a release run fails for a reason outside the repository (registry setup, a network error), use "Re-run failed jobs" on that run: it reuses the `.vsix` it already built. If the fix is a commit and does not touch `package.json`, start Publish by hand from the Actions tab on `master`. Re-running the failed run would reuse its old commit, and the fixing push does not trigger the workflow. Both publish jobs skip a version their registry already has, so a registry that accepted the version keeps that build: if the fix changes anything that ships in the `.vsix`, or `master` has moved past the release commit, bump the version instead. Published GitHub releases are immutable, so a bad release is fixed with a new version, not by replacing its `.vsix` or moving its tag.

Set up each registry once, before its first release. Until a registry is set up, its publish job fails, and no tag or GitHub release is created.

#### Open VSX

1. Upload the first version by hand, because Open VSX registers a trusted publisher only for an extension that already has an active version. Run `just package`, then `OVSX_PAT={token} test/node_modules/.bin/ovsx publish vscode-rider-light-minimal-theme-{version}.vsix` with a token from [open-vsx.org/user-settings/tokens](https://open-vsx.org/user-settings/tokens), and delete the token afterwards
2. Register the trusted publisher at [open-vsx.org/user-settings/trusted-publishers](https://open-vsx.org/user-settings/trusted-publishers): provider GitHub Actions, owner `Unril`, repository `vscode-rider-light-minimal-theme`, workflow `publish.yml`, environment `open-vsx`
3. Create the `open-vsx` environment under the repository's Settings > Environments and limit its deployment branches to `master`; that rule is the only thing stopping a branch from publishing

#### VS Code Marketplace

One Entra app registration publishes every extension of the `NikolaiFedorov` publisher. Steps 1-3 are done once; steps 4-5 are repeated for each extension's repository.

1. In the [Microsoft Entra admin center](https://entra.microsoft.com), register an app under App registrations: single tenant, no redirect URI. Note its Application (client) ID and Directory (tenant) ID
2. Get the app's Marketplace member ID: create a temporary client secret on the app, sign in with `az login --service-principal --username {client-id} --password {secret} --tenant {tenant-id} --allow-no-subscriptions`, run `az rest -u https://app.vssps.visualstudio.com/_apis/profile/profiles/me --resource 499b84ac-1321-427f-aa17-267ca6975798 --query id -o tsv`, then delete the secret
3. At [marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage), add that ID as a member of the `NikolaiFedorov` publisher with the Contributor role
4. Add a federated credential to the app: scenario "GitHub Actions deploying Azure resources", organization `Unril`, repository `vscode-rider-light-minimal-theme`, entity type Environment, environment `vs-marketplace`. Leave the optional owner and repository ID fields empty, and check that the Subject reads `repo:Unril/vscode-rider-light-minimal-theme:environment:vs-marketplace`; Entra matches it case-sensitively
5. Create the `vs-marketplace` environment, limited to `master` like `open-vsx`, with the environment variables `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` set to the app's client and tenant IDs

Once the Marketplace supports vsce's own trusted publishing (`vsce publish --oidc`), it can replace the app registration.
