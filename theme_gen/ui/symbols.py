"""SymbolSection -- symbol icon colors from EditorPalette."""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class SymbolSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        e = theme.editor
        s = e.symbols
        p = theme.palette
        return {
            "symbolIcon.classForeground": s.cls,
            "symbolIcon.functionForeground": s.function,
            "symbolIcon.methodForeground": s.function,
            "symbolIcon.interfaceForeground": s.interface,
            "symbolIcon.variableForeground": s.variable,
            "symbolIcon.constantForeground": s.constant,
            "symbolIcon.enumeratorForeground": s.enum,
            "symbolIcon.enumeratorMemberForeground": s.enum_member,
            "symbolIcon.propertyForeground": s.property,
            "symbolIcon.keywordForeground": s.keyword,
            "symbolIcon.namespaceForeground": s.namespace,
            "symbolIcon.stringForeground": s.string,
            "symbolIcon.numberForeground": s.number,
            # Additional symbol types
            "symbolIcon.arrayForeground": s.variable,
            "symbolIcon.booleanForeground": s.keyword,
            "symbolIcon.colorForeground": s.number,
            "symbolIcon.constructorForeground": s.function,
            "symbolIcon.eventForeground": s.property,
            "symbolIcon.fieldForeground": s.property,
            "symbolIcon.fileForeground": p.fg_muted,
            "symbolIcon.folderForeground": p.fg_muted,
            "symbolIcon.keyForeground": s.property,
            "symbolIcon.moduleForeground": s.namespace,
            "symbolIcon.nullForeground": s.keyword,
            "symbolIcon.objectForeground": s.variable,
            "symbolIcon.operatorForeground": p.fg_muted,
            "symbolIcon.packageForeground": s.namespace,
            "symbolIcon.referenceForeground": s.variable,
            "symbolIcon.snippetForeground": p.fg_muted,
            "symbolIcon.structForeground": s.cls,
            "symbolIcon.textForeground": p.foreground,
            "symbolIcon.typeParameterForeground": s.cls,
            "symbolIcon.unitForeground": s.number,
        }
