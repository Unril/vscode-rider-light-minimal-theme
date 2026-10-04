"""TestingSection -- test explorer icons, coverage indicators, peek views."""

from typing import override

from theme_gen.core.tcol import TCol
from theme_gen.palette.theme import Theme
from theme_gen.ui.protocol import UISection


class TestingSection(UISection):
    __test__: bool = False  # not a pytest test class

    @override
    def build(self, theme: Theme) -> dict[str, TCol]:
        p = theme.palette

        return {
            # Test explorer icons
            "testing.iconPassed": p.success,
            "testing.iconFailed": p.error,
            "testing.iconErrored": p.error,
            "testing.iconSkipped": p.fg_muted,
            "testing.iconQueued": p.fg_muted,
            "testing.iconUnset": p.fg_muted,
            # Retired (dimmed) variants
            "testing.iconPassed.retired": p.success.a50,
            "testing.iconFailed.retired": p.error.a50,
            "testing.iconErrored.retired": p.error.a50,
            "testing.iconSkipped.retired": p.fg_disabled,
            "testing.iconQueued.retired": p.fg_disabled,
            "testing.iconUnset.retired": p.fg_disabled,
            # Run action
            "testing.runAction": p.success,
            # Peek view
            "testing.peekBorder": p.error,
            "testing.peekHeaderBackground": p.error_bg,
            "testing.messagePeekBorder": p.accent,
            "testing.messagePeekHeaderBackground": p.info_bg,
            # Coverage
            "testing.coveredBackground": p.success.a05,
            "testing.coveredBorder": p.success.a25,
            "testing.coveredGutterBackground": p.success.a25,
            "testing.uncoveredBackground": p.error.a05,
            "testing.uncoveredBorder": p.error.a25,
            "testing.uncoveredGutterBackground": p.error.a25,
        }
