"""ChatSection -- chat, inline chat, interactive, agent sessions."""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class ChatSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        e = theme.editor
        w = e.widgets
        fg = p.foreground

        return {
            "chat.slashCommandBackground": p.drop_bg,
            "chat.slashCommandForeground": w.slash_cmd_fg,
            "chat.editedFileForeground": w.chat_edited_fg,
            "chat.requestBorder": p.drop_bg,
            "chat.requestBackground": p.accent_wash,
            # Avatar sits on elevated surface so it reads as "floating on the
            # chat panel." Was panel_bg (same as chat body), which made avatars
            # blend into the background.
            "chat.avatarBackground": p.surface_elevated,
            "chat.avatarForeground": p.accent,
            "chat.linesAddedForeground": w.chat_lines_add,
            "chat.linesRemovedForeground": w.chat_lines_remove,
            "chat.requestCodeBorder": p.accent.a25,
            "chat.requestBubbleBackground": p.accent_wash,
            "chat.requestBubbleHoverBackground": p.drop_bg,
            "chat.checkpointSeparator": p.border,
            # Inline Chat — white bg, shadow handles separation
            "inlineChat.background": p.background,
            "inlineChat.foreground": fg,
            "inlineChat.shadow": p.shadow,
            "inlineChatInput.border": p.border,
            "inlineChatInput.focusBorder": p.accent,
            "inlineChatInput.placeholderForeground": p.fg_muted,
            "inlineChatInput.background": p.background,
            "inlineChatDiff.inserted": p.diff_insert,
            "inlineChatDiff.removed": p.diff_remove,
            # Interactive -- active code block has accent border (you're editing it);
            # inactive uses border_subtle so it recedes (you've moved on from it).
            # The inverse (border vs accent) would make inactive loom louder than active.
            "interactive.activeCodeBorder": p.accent,
            "interactive.inactiveCodeBorder": p.border_subtle,
            # Notebook
            "notebook.cellBorderColor": p.border,
            "notebook.selectedCellBackground": w.notebook_cell_bg,
            # Ports
            "ports.iconRunningProcessForeground": p.success,
            # Agent sessions
            "agentSessionReadIndicator.foreground": p.fg_muted,
        }
