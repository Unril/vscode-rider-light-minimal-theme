"""BaseSyntax -- shared TextMate rules covering minimal scope conventions.

~64 language-agnostic rules targeting comment, constant, entity, invalid,
keyword, markup, punctuation, storage, string, support, and variable scopes.
"""

from typing import override

from theme_gen.core.font_style import FontStyle
from theme_gen.lang.protocol import BaseLanguage, TokenColorRule, tcr
from theme_gen.palette.theme import Theme


class BaseSyntax(BaseLanguage):
    """Shared TextMate rules -- implements Language protocol with id='base'."""

    @property
    @override
    def id(self) -> str:
        return "base"

    @override
    def textmate_rules(self, theme: Theme) -> list[TokenColorRule]:
        s = theme.syntax
        error = theme.editor.output.error
        return [
            # Global settings (TextMate convention)
            tcr("Global settings", [], s.foreground),
            # ── Comments ──
            tcr(
                "Comments",
                ["comment", "punctuation.definition.comment"],
                s.comment,
                FontStyle.ITALIC,
            ),
            tcr(
                "Doc comments",
                [
                    "comment.block.documentation",
                    "comment.block",
                    "string.quoted.docstring",
                ],
                s.comment,
                FontStyle.ITALIC,
            ),
            tcr(
                "Doc comment tags",
                [
                    "keyword.other.documentation",
                    "storage.type.class.jsdoc",
                    "punctuation.definition.block.tag.jsdoc",
                ],
                s.comment,
                FontStyle.ITALIC,
            ),
            tcr(
                "Doc comment tag values",
                ["variable.other.jsdoc", "entity.name.type.instance.jsdoc"],
                s.string,
            ),
            # ── Keywords ──
            tcr("Keywords", ["keyword", "keyword.declaration"], s.keyword),
            tcr("Control keywords", "keyword.control", s.control),
            tcr("Storage", ["storage", "storage.type", "storage.modifier"], s.keyword),
            tcr(
                "Arrow function (=>)",
                [
                    "storage.type.function.arrow.ts",
                    "storage.type.function.arrow.tsx",
                    "storage.type.function.arrow.js",
                    "storage.type.function.arrow.jsx",
                    "storage.type.function.arrow.java",
                    "storage.type.function.arrow.kotlin",
                ],
                s.function,
            ),
            tcr("Operators", "keyword.operator", s.punct),
            tcr(
                "Keyword-like operators",
                [
                    "keyword.operator.expression",
                    "keyword.operator.new",
                    "keyword.operator.ternary",
                    "keyword.operator.optional",
                    "keyword.operator.expression.instanceof",
                    "keyword.operator.expression.keyof",
                    "keyword.operator.expression.typeof",
                    "keyword.operator.expression.delete",
                    "keyword.operator.expression.void",
                    "keyword.operator.expression.in",
                    "keyword.operator.expression.of",
                    "keyword.operator.sizeof",
                    "keyword.operator.alignof",
                    "keyword.operator.typeid",
                    "keyword.operator.alignas",
                    "keyword.operator.instanceof",
                    "keyword.operator.cast",
                    "keyword.operator.wordlike",
                    "keyword.operator.logical.python",
                    "keyword.operator.noexcept",
                    "keyword.other.operator",
                    "entity.name.operator",
                    "keyword.other.using",
                    "keyword.other.directive.using",
                    "source.cpp keyword.operator.new",
                    "source.cpp keyword.operator.delete",
                ],
                s.keyword,
            ),
            tcr("Keyword other unit", "keyword.other.unit", s.number),
            # ── Entity names ──
            tcr("Entity names (catch-all)", "entity.name", s.type),
            tcr(
                "Functions",
                ["entity.name.function", "support.function", "variable.function"],
                s.function,
            ),
            tcr(
                "Function declarations",
                [
                    "entity.name.function.definition",
                    "entity.name.function.declaration",
                    "meta.definition.function entity.name.function",
                    "meta.definition.method entity.name.function",
                ],
                s.function_decl,
            ),
            tcr(
                "Types, classes, interfaces",
                [
                    "entity.name.type",
                    "entity.name.class",
                    "support.class",
                    "support.type",
                    "entity.other.inherited-class",
                    "entity.name.scope-resolution",
                    "entity.other.attribute",
                    "support.constant.math",
                    "support.constant.dom",
                    "support.constant.json",
                    "punctuation.separator.namespace.ruby",
                ],
                s.type,
            ),
            tcr(
                "Namespaces, packages, modules",
                ["entity.name.namespace", "entity.name.type.module"],
                s.namespace,
            ),
            tcr(
                "Tags",
                ["entity.name.tag", "meta.tag", "punctuation.definition.tag"],
                s.type,
            ),
            tcr("Entity name selector", "entity.name.selector", s.type),
            tcr("Labels", "entity.name.label", s.foreground),
            # ── Variables ──
            tcr(
                "Variables",
                [
                    "variable",
                    "support.variable",
                    "entity.name.variable",
                    "meta.definition.variable.name",
                ],
                s.param,
            ),
            tcr("Parameters", "variable.parameter", s.param),
            tcr(
                "Properties, fields",
                [
                    "variable.other.property",
                    "variable.other.object.property",
                    "variable.other.member",
                    "variable.object.property",
                    "support.variable.property",
                ],
                s.field,
            ),
            tcr("Constants", "variable.other.constant", s.field_const),
            tcr("Language variables (this/self/super)", "variable.language", s.keyword),
            # ── Strings ──
            tcr(
                "Strings",
                ["string", "string.quoted", "meta.embedded.assembly"],
                s.string,
            ),
            tcr("String punctuation", "punctuation.definition.string", s.string),
            tcr("Escape characters", "constant.character.escape", s.escape),
            # ── Constants ──
            tcr("Constants (catch-all)", "constant", s.field_const),
            tcr(
                "Numbers",
                [
                    "constant.numeric",
                    "keyword.operator.plus.exponent",
                    "keyword.operator.minus.exponent",
                    "meta.delimiter.decimal.period",
                ],
                s.number,
            ),
            tcr("Language constants (boolean, null)", "constant.language", s.keyword),
            tcr(
                "Constant character",
                ["constant.character", "constant.other.option"],
                s.keyword,
            ),
            tcr("Constant regexp", "constant.regexp", s.string),
            tcr("Constant placeholder", "constant.other.placeholder", s.foreground),
            # ── Punctuation ──
            tcr("Punctuation", "punctuation", s.punct),
            # ── Misc generic ──
            tcr("Attribute names", "entity.other.attribute-name", s.comment),
            tcr("Section headings", "entity.name.section", s.field, FontStyle.BOLD),
            tcr("Support (framework)", "support", s.function),
            tcr("Invalid (catch-all)", "invalid", error),
            tcr("Invalid illegal", "invalid.illegal", error),
            tcr(
                "Deprecated",
                "invalid.deprecated",
                s.deprecated,
                FontStyle.STRIKETHROUGH,
            ),
            # ── Regex ──
            tcr("Regex", "string.regexp", s.string),
            tcr("Regex anchors", "keyword.control.anchor.regexp", s.keyword),
            tcr("Regex quantifiers", "keyword.operator.quantifier.regexp", s.keyword),
            tcr(
                "Regex character class",
                [
                    "constant.other.character-class.regexp",
                    "constant.character.character-class.regexp",
                    "constant.other.character-class.set.regexp",
                    "constant.character.set.regexp",
                ],
                s.type,
            ),
            tcr(
                "Regex brackets",
                "punctuation.definition.character-class.regexp",
                s.field,
            ),
            tcr("Regex escape characters", "constant.character.escape.regexp", s.escape),
            tcr(
                "Regex groups",
                [
                    "punctuation.definition.group.regexp",
                    "punctuation.definition.group.assertion.regexp",
                    "punctuation.character.set.begin.regexp",
                    "punctuation.character.set.end.regexp",
                    "keyword.operator.negation.regexp",
                    "support.other.parenthesis.regexp",
                ],
                s.field,
            ),
            tcr("Regex alternation", "keyword.operator.or.regexp", s.keyword),
            # ── Markup ──
            tcr("Markup bold", "markup.bold", style=FontStyle.BOLD),
            tcr("Markup italic", "markup.italic", style=FontStyle.ITALIC),
            tcr(
                "Markup bold italic",
                ["markup.bold markup.italic", "markup.italic markup.bold"],
                style=FontStyle.ITALIC_BOLD,
            ),
            tcr("Markup underline", "markup.underline", style=FontStyle.UNDERLINE),
            tcr(
                "Markup strikethrough",
                "markup.strikethrough",
                style=FontStyle.STRIKETHROUGH,
            ),
            tcr("Markup heading", "markup.heading", s.field, FontStyle.BOLD),
            tcr("Markup inserted", "markup.inserted", s.function),
            tcr("Markup deleted", "markup.deleted", error),
            tcr("Markup changed", "markup.changed", s.keyword),
            tcr("Markup inline raw", "markup.inline.raw", s.comment),
            # ── Emphasis/Strong (TextMate generic) ──
            tcr("Emphasis", "emphasis", style=FontStyle.ITALIC),
            tcr("Strong", "strong", style=FontStyle.BOLD),
            # ── Preprocessor ──
            tcr(
                "Preprocessor",
                ["meta.preprocessor", "entity.name.function.preprocessor"],
                s.keyword,
            ),
            tcr("Preprocessor string", "meta.preprocessor.string", s.string),
            tcr("Preprocessor numeric", "meta.preprocessor.numeric", s.number),
            # ── Diff ──
            tcr("Diff header", "meta.diff.header", s.keyword),
            # ── Cross-language generic scopes (moved from per-lang modules) ──
            tcr(
                "Object literal keys",
                "meta.object-literal.key",
                s.field,
            ),
            tcr(
                "Template expression punctuation",
                [
                    "punctuation.definition.template-expression.begin",
                    "punctuation.definition.template-expression.end",
                    "punctuation.section.embedded",
                ],
                s.keyword,
            ),
            tcr(
                "Reset embedded expression colors",
                [
                    "meta.template.expression",
                    "meta.embedded",
                    "source.groovy.embedded",
                    "string meta.image.inline.markdown",
                    "variable.legacy.builtin.python",
                ],
                s.foreground,
            ),
            tcr("Primitive type keywords", "support.type.primitive", s.keyword),
            tcr(
                "Strings in markup/YAML/XML/HTML",
                [
                    "string.comment.buffered.block.pug",
                    "string.quoted.pug",
                    "string.interpolated.pug",
                    "string.unquoted.block.yaml",
                    "string.quoted.single.yaml",
                    "string.quoted.double.xml",
                    "string.quoted.single.xml",
                    "string.unquoted.cdata.xml",
                    "string.quoted.double.html",
                    "string.quoted.single.html",
                    "string.unquoted.html",
                    "string.quoted.single.handlebars",
                    "string.quoted.double.handlebars",
                ],
                s.string,
            ),
            tcr(
                "PHP embedded punctuation",
                [
                    "punctuation.section.embedded.begin.php",
                    "punctuation.section.embedded.end.php",
                ],
                s.type,
            ),
            tcr("Git rebase function", "support.function.git-rebase", s.field),
            tcr("Git rebase SHA", "constant.sha.git-rebase", s.number),
            tcr(
                "Custom literal operator",
                [
                    "entity.name.operator.custom-literal",
                    "support.constant.handlebars",
                    "source.powershell variable.other.member",
                ],
                s.function,
            ),
            tcr(
                "Go/C#/Groovy/Java storage types",
                [
                    "storage.type.numeric.go",
                    "storage.type.byte.go",
                    "storage.type.boolean.go",
                    "storage.type.string.go",
                    "storage.type.uintptr.go",
                    "storage.type.error.go",
                    "storage.type.rune.go",
                    "storage.type.cs",
                    "storage.type.generic.cs",
                    "storage.type.modifier.cs",
                    "storage.type.variable.cs",
                    "storage.type.generic.java",
                    "storage.type.object.array.java",
                    "storage.type.primitive.array.java",
                    "storage.type.primitive.java",
                    "storage.type.token.java",
                    "storage.type.groovy",
                    "storage.type.annotation.groovy",
                    "storage.type.parameters.groovy",
                    "storage.type.generic.groovy",
                    "storage.type.object.array.groovy",
                    "storage.type.primitive.array.groovy",
                    "storage.type.primitive.groovy",
                    "meta.type.cast.expr",
                    "meta.type.new.expr",
                ],
                s.type,
            ),
        ]
