// Behavior tests for src/extension.js: a real markdown-it engine, with the `vscode` module (which only the extension
// host provides) replaced by an in-memory fake. Run with `just js-test`.
const assert = require('node:assert/strict');
const Module = require('node:module');
const { beforeEach, describe, test } = require('node:test');
const MarkdownIt = require('markdown-it');

const SETTING = 'rider-light-minimal.markdownPreview.enabled';

const fake = {
    settings: new Map(),
    configurationListeners: [],
    listenerDisposables: [],
    executedCommands: [],
    commandOutcome: () => Promise.resolve(),
};

const vscodeFake = {
    workspace: {
        getConfiguration(section) {
            return {
                get(key, fallback) {
                    const fullKey = `${section}.${key}`;
                    return fake.settings.has(fullKey) ? fake.settings.get(fullKey) : fallback;
                },
            };
        },
        onDidChangeConfiguration(listener) {
            fake.configurationListeners.push(listener);
            const disposable = { dispose() {} };
            fake.listenerDisposables.push(disposable);
            return disposable;
        },
    },
    commands: {
        executeCommand(command) {
            fake.executedCommands.push(command);
            return fake.commandOutcome();
        },
    },
};

// Module._load is internal, but it can hand back the live fake object; the public module.registerHooks only supplies
// module source, so the fake would have to travel through a global. It is restored as soon as extension.js has bound
// its `vscode` import.
const originalLoad = Module._load;
Module._load = function (request, ...rest) {
    return request === 'vscode' ? vscodeFake : originalLoad.call(this, request, ...rest);
};
let extension;
try {
    extension = require('../src/extension.js');
} finally {
    Module._load = originalLoad;
}

function activate() {
    const context = { subscriptions: [] };
    return { context, api: extension.activate(context) };
}

function stockRender(markdown) {
    return new MarkdownIt().render(markdown);
}

// Mirrors ConfigurationChangeEvent.affectsConfiguration: true for the changed key and every section above it.
function changeConfiguration(changedKey) {
    const event = { affectsConfiguration: (section) => changedKey === section || changedKey.startsWith(`${section}.`) };
    for (const listener of fake.configurationListeners) {
        listener(event);
    }
}

beforeEach(() => {
    fake.settings.clear();
    fake.configurationListeners.length = 0;
    fake.listenerDisposables.length = 0;
    fake.executedCommands.length = 0;
    fake.commandOutcome = () => Promise.resolve();
});

describe('activate', () => {
    test('registers its configuration listener on the extension context, so it is disposed with the extension', () => {
        const { context } = activate();

        assert.deepEqual(context.subscriptions, fake.listenerDisposables);
        assert.equal(context.subscriptions.length, 1);
    });
});

describe('extendMarkdownIt', () => {
    test('returns the engine it was given, because VS Code renders with the returned instance', () => {
        const { api } = activate();
        const md = new MarkdownIt();

        assert.equal(api.extendMarkdownIt(md), md);
    });

    test('wraps the rendered preview in the rlm-preview container when the setting is enabled', () => {
        fake.settings.set(SETTING, true);
        const { api } = activate();
        const md = api.extendMarkdownIt(new MarkdownIt());

        assert.equal(md.render('# Title'), `<div class="rlm-preview">${stockRender('# Title')}</div>`);
    });

    test('renders byte-identical to stock markdown-it when the setting is disabled', () => {
        fake.settings.set(SETTING, false);
        const { api } = activate();
        const md = api.extendMarkdownIt(new MarkdownIt());

        assert.equal(md.render('# Title\n\n- item\n'), stockRender('# Title\n\n- item\n'));
    });

    test('reads the setting on every render, so toggling it needs no reload', () => {
        const { api } = activate();
        const md = api.extendMarkdownIt(new MarkdownIt());

        fake.settings.set(SETTING, false);
        const disabled = md.render('text');
        fake.settings.set(SETTING, true);
        const enabled = md.render('text');

        assert.equal(disabled, stockRender('text'));
        assert.equal(enabled, `<div class="rlm-preview">${stockRender('text')}</div>`);
    });

    test('wraps only once when applied to the same engine twice', () => {
        fake.settings.set(SETTING, true);
        const { api } = activate();
        const md = new MarkdownIt();

        api.extendMarkdownIt(md);
        api.extendMarkdownIt(md);

        assert.equal(md.render('text'), `<div class="rlm-preview">${stockRender('text')}</div>`);
    });

    test('wraps every engine it extends, because VS Code rebuilds the engine when plugin contributions change', () => {
        fake.settings.set(SETTING, true);
        const { api } = activate();

        const first = api.extendMarkdownIt(new MarkdownIt());
        const second = api.extendMarkdownIt(new MarkdownIt());

        assert.equal(first.render('a'), `<div class="rlm-preview">${stockRender('a')}</div>`);
        assert.equal(second.render('b'), `<div class="rlm-preview">${stockRender('b')}</div>`);
    });

    test('forwards the tokens, options and env VS Code passes to renderer.render', () => {
        fake.settings.set(SETTING, true);
        const { api } = activate();
        const md = api.extendMarkdownIt(new MarkdownIt());
        md.renderer.rules.text = (tokens, idx, options, env) => `${tokens[idx].content}|${options.breaks}|${env.label}`;
        const env = { label: 'from-env' };

        const html = md.renderer.render(md.parse('text', env), { ...md.options, breaks: true }, env);

        assert.equal(html, '<div class="rlm-preview"><p>text|true|from-env</p>\n</div>');
    });
});

describe('setting changes', () => {
    test('refresh open previews when the setting changes', () => {
        activate();

        changeConfiguration(SETTING);

        assert.deepEqual(fake.executedCommands, ['markdown.preview.refresh']);
    });

    // The sibling key guards the exact-key check: widening it to the whole section would refresh on every future setting.
    for (const unrelatedKey of ['editor.fontSize', 'rider-light-minimal.otherSetting']) {
        test(`do not refresh previews when an unrelated setting changes (${unrelatedKey})`, () => {
            activate();

            changeConfiguration(unrelatedKey);

            assert.deepEqual(fake.executedCommands, []);
        });
    }

    test('swallow a rejected refresh command instead of leaving an unhandled rejection', async () => {
        const unhandled = [];
        const recordUnhandled = (reason) => unhandled.push(reason);
        process.on('unhandledRejection', recordUnhandled);
        try {
            fake.commandOutcome = () => Promise.reject(new Error("command 'markdown.preview.refresh' not found"));
            activate();

            changeConfiguration(SETTING);
            // Unhandled rejections are reported after the microtask queue drains, before the next macrotask.
            await new Promise((resolve) => setImmediate(resolve));
        } finally {
            process.off('unhandledRejection', recordUnhandled);
        }

        assert.deepEqual(fake.executedCommands, ['markdown.preview.refresh']);
        assert.deepEqual(unhandled, []);
    });
});
