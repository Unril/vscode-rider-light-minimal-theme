// @ts-check
const vscode = require('vscode');

const configSection = 'rider-light-minimal';
const enabledKey = 'markdownPreview.enabled';
const fullKey = `${configSection}.${enabledKey}`;
const WRAPPED = Symbol.for('rider-light-minimal.markdownPreviewWrapped');

function isEnabled() {
    const settings = vscode.workspace.getConfiguration(configSection, null);
    return settings.get(enabledKey, true);
}

function refreshMarkdownPreview() {
    // Guard against rejection during activation or when the command isn't
    // registered (Web extensions, restricted-mode environments).
    vscode.commands.executeCommand('markdown.preview.refresh').then(undefined, () => {});
}

exports.activate = function (/** @type {vscode.ExtensionContext} */ ctx) {
    ctx.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            // Narrow to the exact setting so future keys don't trigger
            // needless preview refreshes.
            if (e.affectsConfiguration(fullKey)) {
                refreshMarkdownPreview();
            }
        }),
    );

    return {
        extendMarkdownIt(/** @type {import('markdown-it')} */ md) {
            return md.use(plugin);
        },
    };
};

function plugin(/** @type {import('markdown-it')} */ md) {
    if (/** @type {any} */ (md.renderer)[WRAPPED]) {
        return md;
    }
    const render = md.renderer.render;
    md.renderer.render = (...args) => {
        if (!isEnabled()) {
            return render.apply(md.renderer, args);
        }
        return `<div class="rlm-preview">${render.apply(md.renderer, args)}</div>`;
    };
    /** @type {any} */ (md.renderer)[WRAPPED] = true;
    return md;
}
