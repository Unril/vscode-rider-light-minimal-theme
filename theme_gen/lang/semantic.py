"""GlobalSemanticTokens -- ~59 global semanticTokenColors entries.

Covers all 23 standard VS Code token types, key modifier combinations,
and widely-emitted custom types from rust-analyzer, pylance, and other LSPs.
"""

from theme_gen.core.font_style import FontStyle
from theme_gen.lang.protocol import SemanticTokenStyle, SemanticTokenValue
from theme_gen.palette.syntax import SyntaxPalette


class GlobalSemanticTokens:
    """Builds the global (non-language-scoped) semanticTokenColors map."""

    def __init__(self, syntax: SyntaxPalette) -> None:
        self._s: SyntaxPalette = syntax

    def build(self) -> dict[str, SemanticTokenValue]:
        s = self._s
        return {
            # ── Functions and methods (standard) ──
            "function": s.function,
            "function.declaration": SemanticTokenStyle(foreground=s.function_decl, font_style=FontStyle.BOLD),
            "function.defaultLibrary": s.function,
            "method": s.function,
            "method.declaration": SemanticTokenStyle(foreground=s.function_decl, font_style=FontStyle.BOLD),
            # ── Types (standard + custom) ──
            "class": s.type,
            "interface": s.type,
            "type": s.type,
            "enum": s.type,
            "struct": s.type,
            "typeParameter": SemanticTokenStyle(foreground=s.type, font_style=FontStyle.BOLD),
            "typeAlias": s.type,
            "builtinType": s.type,
            "lifetime": s.type,
            # .defaultLibrary modifier -- stdlib types
            "type.defaultLibrary": s.type,
            "class.defaultLibrary": s.type,
            "enum.defaultLibrary": s.type,
            "interface.defaultLibrary": s.type,
            "struct.defaultLibrary": s.type,
            # ── Properties and variables (standard) ──
            "property": s.field,
            "property.declaration": s.field,
            "property.readonly": SemanticTokenStyle(foreground=s.field, font_style=FontStyle.NONE),
            "property.readonly.static": s.field_const,
            "variable": s.param,
            "variable.readonly": s.field_const,
            "variable.readonly.local": s.param,
            "variable.constant": s.field_const,
            "variable.defaultLibrary.readonly": s.field_const,
            "variable.defaultLibrary": s.field_const,
            "variable.readonly.defaultLibrary": s.field_const,
            "parameter": s.param,
            "selfParameter": s.keyword,  # Pylance: Python self/cls
            "clsParameter": s.keyword,  # Pylance: Python cls
            "enumMember": s.enum_member,
            "event": s.field,
            # ── Keywords and literals (standard + custom) ──
            "keyword": s.keyword,
            "keyword.controlFlow": s.control,
            "boolean": s.keyword,
            "string": s.string,
            "number": s.number,
            "regexp": s.string,
            "operator": s.punct,
            "operatorOverload": s.punct,
            "memberOperatorOverload": s.keyword,
            "punctuation": s.punct,
            "label": s.foreground,
            "macro": s.keyword,
            "macro.declaration": s.function_decl,
            # ── Annotations and metadata (standard + custom) ──
            "namespace": s.namespace,
            "comment": SemanticTokenStyle(foreground=s.comment, font_style=FontStyle.ITALIC),
            "decorator": s.metadata,
            "attribute": s.metadata,
            "builtinAttribute": s.metadata,
            "generic.attribute": s.metadata,
            "derive.declaration": s.metadata,
            "annotation": s.metadata,  # Java LSP: annotations
            # ── Java-specific types ──
            "record": s.type,
            "recordComponent": s.field,
            "annotationMember": s.field,
            "modifier": s.keyword,
            # ── Escape and format sequences (custom) ──
            "escapeSequence": s.escape,
            "formatSpecifier": s.escape,
            # ── VS Code built-in extras ──
            "newOperator": s.keyword,
            "stringLiteral": s.string,
            "customLiteral": s.function,
            "numberLiteral": s.number,
        }
