# Changelog

All notable changes to the "vscode-rider-light-minimal-theme" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.4.0] - 2026-10-05

### Fixed

- **High Contrast Light preview**: uses the light palette and light diff tints. VS Code also gives that theme the `vscode-high-contrast` class, so the dark rules were winning
- **Preview horizontal rules**: now colored `--rlm-border`. The override set the top border, but VS Code draws `hr` as a bottom border
- **Preview task lists**: an item fades only when its own checkbox is checked, so a checked sub-item no longer fades its parent. Loose lists and the `label` option of markdown-it-task-lists are covered, and a checked sub-item under a checked parent stays at 60% opacity instead of 36%
- **Diff editor stacking**: line and text backgrounds now use different alpha levels (5%/15% light, 10%/25% dark) so word-level diffs pop above the row wash instead of compounding into a dark blob
- **Word highlight read/write distinction**: `editor.wordHighlightBackground` (18%) and `editor.wordHighlightStrongBackground` (28%) are no longer identical, restoring the refactoring-relevant signal
- **Active link feedback**: `textLink.activeForeground` now uses the darker accent hover color, providing visible press/click feedback
- **Indent guide zebra striping**: inactive guide opacity reduced from 15% to 5%, eliminating vertical stripe noise in deeply nested code
- **Status bar focus border**: now opaque accent (was 50% alpha, inconsistent with other focus indicators)
- **Inline chat placeholder**: uses muted foreground (was disabled gray, too faint for an active input surface)
- **Secondary button hover**: stays neutral gray (was accent blue, creating false primary-action affordance)
- **List inactive focus**: dimmer than active focus so focus-loss is visible when switching to the editor
- **Status bar prominent hover**: always stronger than base (was equal or inverted in dark mode)
- **Welcome page tile hover**: correctly darkens on light / lightens on dark (was inverted in both)
- **Terminal hover highlight**: uses alpha transparency (was solid, could obliterate CLI background colors)
- **Inlay hint background (light)**: uses alpha (was solid, punched through selection/find highlights)
- **Dark `terminal.ansiBlack`**: raised above terminal background so dim CLI content is visible
- **Dark minimap slider**: uses foreground-based alpha (was mid-gray, nearly invisible)
- **Dark inlay hint background**: bumped from 5% to 10% for visibility
- **Dark chat slash command**: uses lighter accent (was too dark on the tinted bubble background)
- **Secondary color AA floor**: `#906800` now passes 4.55:1 on panel_bg (was 4.27:1)
- **`textSeparator.foreground`**: uses border_subtle (was pure black, harsh on warm off-white)
- **Light minimap slider**: uses foreground base (was different color family than scrollbar, causing color-shift on hover)
- **Minimap find match**: bumped to 80% opacity (was 25-35%, invisible at minimap scale)

### Added

- C# support: TextMate rules and Roslyn semantic token styles, so C# uses the same role colors as the other languages
- `markdown.extension.editor.codeSpan.border` set to transparent, removing the box Markdown All in One draws around inline code in the Markdown editor
- `inputValidation.errorForeground`, `warningForeground`, `infoForeground` (completes the validation color set)
- `editorSuggestWidget.selectedForeground` (defensive against VS Code fallback inversion)
- `menu.background` and `menu.foreground` (prevents OS dark-mode fallback on Windows/Linux)
- `keybindingLabel.background`, `border`, `bottomBorder` (keycap styling in command palette)
- `editorHoverWidget.statusBarBackground` (grounds the "⌘ click" hint as a footer strip)
- `--rlm-code-bg` CSS variable (dedicated code-block background for WCAG AA syntax contrast)
- `--rlm-link-active` CSS variable (hover/active link color for markdown preview)
- Link `:hover`, `:active`, `:focus-visible` states in markdown preview
- Theme-aware diff highlight backgrounds in markdown preview (5% light / 15% dark via `color-mix`)
- `capabilities` declaration in `package.json` for virtual and untrusted workspaces
- Settings section in README with copy-paste config for the markdown preview toggle

### Changed

- Renamed the extension to Rider Light Minimal (ID `NikolaiFedorov.vscode-rider-light-minimal-theme`). The themes are now "Rider Light Minimal" and "Rider Light Minimal Dark", and the preview setting is `rider-light-minimal.markdownPreview.enabled`. After upgrading, reselect the theme and set the preview setting again
- Requires VS Code 1.110 or later (was 1.90)
- Markdown preview code blocks use `--rlm-code-bg` (editor bg) instead of `--rlm-panel` for better syntax contrast
- Markdown preview HTML/XML tags now use `--rlm-type` (purple) to match editor semantics
- Markdown preview CSS selectors now use `--rlm-type` (purple) to match editor semantics
- Markdown preview `::marker` scoped to `li::marker` (no longer colors `<details>` triangles)
- Markdown preview table striping scoped to `tbody tr` (no longer counts header row)
- Markdown preview heading borders use explicit shorthand (more robust than partial overrides)
- Removed `min-width: 200px` from preview layout (prevented narrow split-pane usage)
- `code.hljs { padding: 3px 5px }` scoped to inline code (`:not(pre)>code.hljs`); code blocks already overrode it
- Terminal ANSI white decision documented as intentional tradeoff in source code
- Markdown preview refresh on setting change is now guarded against rejection (Web extensions, restricted-mode)
- Configuration listener narrowed to the exact `rider-light-minimal.markdownPreview.enabled` key
- Markdown-it plugin now guards against double-wrapping if applied to the same renderer twice
- Theme generator is an installable uv project at the repo root; `just` recipes cover generating, testing, formatting, and packaging
- Automated extension tests: pytest contract tests (`extension.js`, `package.json`, `.vscodeignore`, and the preview CSS agree) and `node:test` behavior tests

### Removed

- `--rlm-bg` and `--rlm-warning` CSS variables (no stylesheet used them)
- `--rlm-quote-fg` CSS variable (same color as `--rlm-muted`, which blockquotes now use)

## [0.3.2] - 2026-05-13

### Fixed

- Markdown preview styling not applying on recent VS Code versions. The extension declared no activation events, so the markdown-it plugin that injects the `.rlm-preview` wrapper was never registered after VS Code's move away from implicit activation. Added `"activationEvents": ["onLanguage:markdown"]` so the plugin activates when any markdown file or preview opens.
- Markdown-it plugin not discovered by the preview engine when installed as a `.vsix`. The `onLanguage:markdown` activation event caused a race: the markdown engine initialized its plugin chain before the extension finished activating. Fixed by declaring `"extensionDependencies": ["vscode.markdown-language-features"]` and using an empty `activationEvents` array, which lets the markdown engine discover and activate the plugin via the `'api'` pattern (same mechanism used by `markdown-math` and `markdown-mermaid`).

## [0.3.1] - 2026-04-04

### Fixed

- CSS variables now defined on `body.vscode-light` / `body.vscode-dark` directly, fixing preview styling not applying when the markdown-it plugin hadn't activated yet
- Code block highlight.js scope ordering: `title.class` (type color) now correctly overrides bare `title` (function color)
- Removed font-size/font-family overrides that broke user `--markdown-font-size` settings

### Added

- Colored heading hierarchy (H1-H6) using hue-shifted series shared with bracket pairs and SCM graph
- `SyntaxPalette.hue_shifted` field as single source for bracket, heading, and SCM graph colors
- Lighter quote variants (`--rlm-h*-quote`) for blockquote borders by nesting depth (up to 6 levels)
- Heading colors (`--rlm-h*`) for list markers by nesting depth (up to 6 levels)
- Alternating disc/square bullet shapes for nested unordered lists
- Inline code colored with comment-green to match editor styling
- Table styling: rounded corners, zebra striping, horizontal-only separators
- Task list styling: checked items get line-through and reduced opacity
- Max-width (980px) layout for comfortable reading on wide monitors
- Consistent 16px block spacing for paragraphs, lists, tables, and code blocks
- Markdown preview screenshots in README

### Changed

- Moved installation, generator, and testing docs from README to CONTRIBUTING.md

## [0.3.0] - 2026-04-03

### Added

- Markdown preview styling with theme-matched colors for both light and dark variants
- Colored heading hierarchy (H1-H6) using the same hue-shifted series as bracket pairs and SCM graph
- Syntax highlighting in preview code blocks via highlight.js scope mapping to theme colors
- Inline code colored with comment-green to match editor styling
- Colored list markers, blockquote accent borders, and nested blockquote distinction
- Table styling: rounded corners, zebra striping, horizontal-only separators
- Task list styling: checked items get line-through and reduced opacity
- Max-width (980px) layout for comfortable reading on wide monitors
- Setting `rider-light-minimal.markdownPreview.enabled` to toggle preview styling (default: on)
- CSS variables generated on `body.vscode-light` / `body.vscode-dark` for reliable theming
- `SyntaxPalette.hue_shifted` field: single source for bracket, SCM graph, heading, and preview heading colors

## [0.2.0] - 2026-03-26

### Added

- Dark theme variant ("Rider light minimal Dark") with warm-tinted background (OKLCH H=82)
- Same 8 syntax hues as light theme with contrast-matched dark lightness tiers
- Bidirectional `with_min_contrast` -- lightens on dark backgrounds, darkens on light
- `TCol.mix` for blending two colors in sRGB space
- Dark-aware ANSI terminal colors (Lab L*=60 normal, L*=68 bright)
- Dark-aware editor highlights with scaled alpha overlays
- Staged git decoration colors using accent/foreground mix
- Missing UI keys: peek view foregrounds, editor marker navigation, notification borders, markdown alert colors, status bar warning/error states, menu border

### Changed

- Extension renamed to "Rider light minimal" (covers both variants)
- `SyntaxPalette.create` accepts `is_dark` and `foreground` parameters
- `Palette` includes `is_dark` field
- `EditorPalette.create` uses `_tint` and `_overlay` helpers instead of inline conditionals
- `editorInfo.foreground` uses accent blue instead of muted gray
- `descriptionForeground` uses muted foreground instead of full foreground
- `button.hoverBackground` is lighter than button on dark theme
- Warning hue shifted from olive (H=75) to orange-amber (H=55)
- `minimap.background` and `editorOverviewRuler.background` match editor background
- Scrollbar/minimap slider alpha reduced for dark theme
- `panelTitle.activeBackground` matches panel background

## [0.1.0] - 2026-03-25

### Added

- 17 syntax roles generated from an OKLCH harmony wheel with 45° hue spacing
- All syntax roles pass WCAG AA (4.5:1) contrast on white
- Full cross-language support: Kotlin, Java, TypeScript, JavaScript, Python, Markdown, YAML, JSON, HTML, CSS
- 465 UI colors covering editor, terminal, debug, testing, VCS, panels, and more
- 16-color ANSI terminal palette generated from standard hues at perceptually uniform CIELab lightness
- Debug token expressions and debug icons (Variables/Watch view, breakpoints, toolbar)
- Testing icons with pass/fail/skip states and coverage indicators
- SCM graph colors using the same hue-shifted series as bracket pair colorization
- Merge conflict colors (current/incoming/common)
- Additional symbol icons (array, boolean, constructor, event, field, module, struct, etc.)
- Secondary (complementary gold) color applied to lightbulb, gutter comment markers, list filter matches, and git blame
- Python-based generator (`theme_gen/`) with snapshot integration tests
- Extension icon
