"""VcsSection -- diff editor, git decorations, minimap VCS markers."""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class VcsSection(UISection):
    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette
        e = theme.editor
        git_added, git_modified, git_deleted = p.git_added, p.git_modified, p.git_deleted

        return {
            # Diff editor -- line and text use DIFFERENT alpha levels. VS Code
            # stacks them additively, so when a modified line contains word-level
            # changes both backgrounds paint the same pixels. Equal alpha
            # produced a dark blob (~28% effective). Now: faint line wash + full
            # text highlight, so word diffs pop above the row.
            "diffEditor.insertedTextBackground": p.diff_insert,
            "diffEditor.removedTextBackground": p.diff_remove,
            "diffEditor.insertedLineBackground": p.diff_insert_line,
            "diffEditor.removedLineBackground": p.diff_remove_line,
            "diffEditorOverview.insertedForeground": p.gutter_add,
            "diffEditorOverview.removedForeground": p.gutter_del,
            "diffEditor.unchangedRegionBackground": p.panel_bg,
            # Minimap -- sits on panel_bg so it reads as a distinct slab next to the editor.
            # foregroundOpacity encodes the opacity in the alpha channel of an #RRGGBBAA
            # hex; the RGB portion is ignored by VS Code. Use fg with 0.99 alpha so the
            # generated JSON has an 8-digit hex that clearly signals "full opacity applied".
            # Default VS Code treatment fades minimap text to ~75%, which washes out colors
            # on our panel_bg slab; pushing to ~100% keeps syntax silhouettes legible.
            "minimap.background": p.panel_bg,
            "minimap.foregroundOpacity": p.foreground.with_alpha(0.99),
            # Minimap find match -- minimap renders decorations as tiny dots;
            # low-alpha colors become invisible at that scale. Use warning.a80
            # so search hits are clearly visible in the minimap gutter.
            "minimap.findMatchHighlight": p.warning.a80,
            "minimap.selectionHighlight": e.selection.primary,
            "minimap.selectionOccurrenceHighlight": e.selection.highlight,
            "minimap.errorHighlight": p.minimap_error,
            "minimap.warningHighlight": p.minimap_warning,
            "minimap.infoHighlight": p.accent.a50,
            "minimapSlider.background": p.minimap_slider,
            "minimapSlider.hoverBackground": p.scrollbar_thumb,
            "minimapSlider.activeBackground": p.scrollbar_hover,
            "minimapGutter.addedBackground": p.gutter_add,
            "minimapGutter.modifiedBackground": p.gutter_mod,
            "minimapGutter.deletedBackground": p.gutter_del,
            # Git decorations -- push away from the sidebar surface so `M`/`A`/`D`
            # badges stay readable at small sizes. Applies to both the file tree
            # (sidebar) and the SCM viewlet per theme-color.md.
            "gitDecoration.addedResourceForeground": git_added,
            "gitDecoration.modifiedResourceForeground": git_modified,
            "gitDecoration.deletedResourceForeground": git_deleted,
            "gitDecoration.untrackedResourceForeground": git_added,
            "gitDecoration.ignoredResourceForeground": p.fg_disabled,
            "gitDecoration.conflictingResourceForeground": git_deleted,
            "gitDecoration.renamedResourceForeground": git_added,
            "gitDecoration.stageModifiedResourceForeground": git_modified.mix(p.foreground),
            "gitDecoration.stageDeletedResourceForeground": git_deleted.mix(p.foreground),
            # Git blame -- warm muted for historical annotations
            "git.blame.editorDecorationForeground": p.secondary.a50,
            # Merge conflicts
            "merge.currentHeaderBackground": p.success.a25,
            "merge.currentContentBackground": p.success.a15,
            "merge.incomingHeaderBackground": p.accent.a25,
            "merge.incomingContentBackground": p.accent.a15,
            "merge.commonHeaderBackground": p.fg_muted.a25,
            "merge.commonContentBackground": p.fg_muted.a15,
            # SCM graph -- same hue-shifted series as bracket pair colorization
            **{f"scmGraph.foreground{i + 1}": color for i, color in enumerate(theme.syntax.hue_shifted[:5])},
        }
