# Security policy

Rider Light Minimal is a color theme with a small markdown-preview plugin (`src/extension.js`) and preview stylesheets. This page explains how to report a security problem in it.

## Reporting a vulnerability

Report it privately through GitHub's [private vulnerability reporting](https://github.com/Unril/vscode-rider-light-minimal-theme/security/advisories/new). Do not open a public issue or pull request for it.

Include the affected version, the steps to reproduce, and what an attacker could do with it.

## Scope

In scope:

- the extension as published to Open VSX or attached to a GitHub release: `src/extension.js`, the preview stylesheets, and `package.json`
- the GitHub Actions workflows that build and publish it

VS Code itself, its built-in markdown extension, and other extensions are maintained elsewhere; report problems in them to their maintainers.
