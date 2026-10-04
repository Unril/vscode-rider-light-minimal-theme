"""Hue-shifted color series used by headings, bracket pairs, and SCM graph.

All three features share the same progressive hue rotation from a base color, stepping 24° per slot to produce visually distinct colors within a 120°+ arc.
"""

from theme_gen.core.tcol import TCol

# Degrees per step in the hue-shifted series (OKLCH hue rotation).
# 24° gives 6 visually distinct colors within a 144° arc.
HUE_SHIFT_STEP: float = 24.0


def hue_series(base: TCol, count: int) -> list[TCol]:
    """Generate *count* colors by rotating *base* hue in HUE_SHIFT_STEP increments."""
    return [base.shift_hue(i * HUE_SHIFT_STEP) for i in range(count)]
