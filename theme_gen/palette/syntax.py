"""SyntaxPalette -- generative syntax colors from OKLCH parameters.

17 syntax roles organized into 8 hue clusters derived from
coloraide's harmony('wheel', count=8), which spaces them exactly 45° apart
in OkLCh. This guarantees every adjacent cluster pair is maximally separated
and perceptually distinct.

Cluster layout (seeded from string_hue, default 40° = brown):
  [0]  40°  string    brown    (#8C6C41 ≈  40°)
  [1]  85°  metadata  olive    (#808000 ≈  85°)
  [2] 130°  comment   green    (#248700 ≈ 130°)
  [3] 175°  function  green    (#00855F ≈ 175°)
  [4] 220°  field     teal     (#0093A1 ≈ 220°)
  [5] 265°  keyword   blue     (#0F54D6 ≈ 265°)
  [6] 310°  type      purple   (#6B2FBA ≈ 310°)
  [7] 355°  number    magenta  (#AB2F6B ≈ 355°)

Lightness tiers (CIELab L* targets):
  Bright  Lab L*=54  string, metadata, number, field, comment
  Mid     Lab L*=44  function, keyword, control, escape, enum_member
  Dark    Lab L*=34  type, namespace, function_decl, punct
  Ident   Lab L*=28  param
  V.dark  Lab L*=24  field_const

Using CIELab L* (not OkLCh L) as the lightness axis ensures perceptual
uniformity across hues. At the same OkLCh L, purple (310°) has a much lower
Lab L* than blue (265°), making it appear darker/more prominent. By targeting
the same Lab L* per tier, all roles within a tier have similar visual weight
regardless of hue.

Contrast floors:
  All text roles: 4.5:1 — WCAG AA minimum for normal text.
  Dark anchors (function_decl, field_const):
    No floor — already dark enough by construction.
"""

from dataclasses import dataclass
from typing import Self

from coloraide import Color

from core.hue_series import hue_series
from core.tcol import TCol

# Bracket pairs, SCM graph, and markdown headings all share this count.
_HUE_SERIES_COUNT = 6

# CIELab L* targets per lightness tier (light variant).
# These produce consistent visual weight across all hues (10-point steps).
_LAB_BRIGHT = 54.0  # string, metadata, number, field -- prominent literals
_LAB_MID = 44.0  # comment, function, keyword, control, escape, enum_member
_LAB_DARK = 34.0  # type, namespace, function_decl, punct -- structural anchors
_LAB_IDENT = 28.0  # param -- dark base text; identifiers sit below colored roles
_LAB_ANCHOR = 24.0  # field_const -- deepest anchor, constants are visually fixed

# CIELab L* targets for dark variant.
# Calibrated to produce clear visual hierarchy on dark backgrounds.
# Bright bumped to 56 for WCAG AA margin; Mid at 64 gives 8-unit gap
# (matching the 10-unit gap in light theme for similar visual separation).
_DARK_LAB_BRIGHT = 60.0
_DARK_LAB_MID = 62.0
_DARK_LAB_DARK = 70.0
_DARK_LAB_IDENT = 76.0
_DARK_LAB_ANCHOR = 80.0

# Chroma reduction for dark variant (Hunt effect: colors appear more
# saturated at lower luminance levels, so we reduce chroma to match
# the perceived saturation of the light theme).
_DARK_CHROMA_SCALE = 0.85

# Mapping from light tier -> dark tier for substitution
_LIGHT_TO_DARK_LAB: dict[float, float] = {
    _LAB_BRIGHT: _DARK_LAB_BRIGHT,
    _LAB_MID: _DARK_LAB_MID,
    _LAB_DARK: _DARK_LAB_DARK,
    _LAB_IDENT: _DARK_LAB_IDENT,
    _LAB_ANCHOR: _DARK_LAB_ANCHOR,
}

# Chroma bands (scaled by chroma_scale)
_C_ZERO = 0.00
_C_LOW = 0.05
_C_STRING = 0.08  # muted brown for strings (Rider #8C6C41 ≈ C=0.072)
_C_MID = 0.12
_C_VIVID = 0.16  # vivid for comment, number, escape (Rider comment ≈ 0.177)
_C_ACCENT = 0.20  # keyword, type — matches Rider (#0F54D6 C=0.210, #6B2FBA C=0.203)

# Contrast floors. 4.6 target (not 4.5) absorbs sRGB quantization loss so
# rounded 8-bit output reliably meets WCAG AA 4.5:1. Without the buffer,
# Brent's OKLCH solution converges in float precision but the rounded hex
# can miss AA by ~0.02 (e.g., string color at 4.47:1 instead of 4.50:1).
_FLOOR_STRUCTURAL = 4.6  # WCAG AA — keyword, type, param, punct, namespace, escape
_FLOOR_SEMANTIC = 4.6  # WCAG AA — function, field, comment, string, metadata, number
_FLOOR_NONE = 0.0  # dark anchors — function_decl, field_const
_CI_STRING = 0  # 40°  brown
_CI_META = 1  # 85°  olive
_CI_COMMENT = 2  # 130° green
_CI_FUNCTION = 3  # 175° green
_CI_FIELD = 4  # 220° teal
_CI_KEYWORD = 5  # 265° blue
_CI_TYPE = 6  # 310° purple
_CI_NUMBER = 7  # 355° magenta

# (cluster_index, lab_l_target, chroma_band, contrast_floor) per role
_SPECS: dict[str, tuple[int, float, float, float]] = {
    # String cluster: muted brown; deprecated shares hue + strikethrough style
    "string": (_CI_STRING, _LAB_BRIGHT, _C_STRING, _FLOOR_SEMANTIC),
    "deprecated": (_CI_STRING, _LAB_BRIGHT, _C_STRING, _FLOOR_SEMANTIC),
    # Metadata cluster: olive annotations — bright, prominent
    "metadata": (_CI_META, _LAB_BRIGHT, _C_MID, _FLOOR_SEMANTIC),
    # Comment cluster: muted green — recedes behind code (bright tier, low chroma)
    "comment": (_CI_COMMENT, _LAB_BRIGHT, _C_MID, _FLOOR_SEMANTIC),
    # Function cluster: calls mid, declarations dark (no floor — already dark)
    "function": (_CI_FUNCTION, _LAB_MID, _C_MID, _FLOOR_SEMANTIC),
    "function_decl": (_CI_FUNCTION, _LAB_DARK, _C_MID, _FLOOR_NONE),
    # Field cluster: bright (clearly above function), enum mid, const very dark
    "field": (_CI_FIELD, _LAB_BRIGHT, _C_MID, _FLOOR_SEMANTIC),
    "enum_member": (_CI_FIELD, _LAB_MID, _C_MID, _FLOOR_SEMANTIC),
    "field_const": (_CI_FIELD, _LAB_ANCHOR, _C_LOW, _FLOOR_NONE),
    # Keyword cluster: structural — WCAG AA required
    "keyword": (_CI_KEYWORD, _LAB_MID, _C_ACCENT, _FLOOR_STRUCTURAL),
    "control": (_CI_KEYWORD, _LAB_MID, _C_ACCENT, _FLOOR_STRUCTURAL),
    # Achromatic: punctuation recedes (dark)
    "punct": (_CI_KEYWORD, _LAB_DARK, _C_ZERO, _FLOOR_STRUCTURAL),
    # Param: field-family tint at low chroma — recognizable as data, darker than fields
    "param": (_CI_FIELD, _LAB_IDENT, _C_LOW, _FLOOR_STRUCTURAL),
    # Type cluster: structural anchors — WCAG AA required
    "type": (_CI_TYPE, _LAB_DARK, _C_ACCENT, _FLOOR_STRUCTURAL),
    "namespace": (_CI_TYPE, _LAB_DARK, _C_MID, _FLOOR_STRUCTURAL),
    "escape": (_CI_TYPE, _LAB_MID, _C_VIVID, _FLOOR_STRUCTURAL),
    # Number cluster: vivid magenta — bright, prominent
    "number": (_CI_NUMBER, _LAB_BRIGHT, _C_VIVID, _FLOOR_SEMANTIC),
}


@dataclass(frozen=True)
class SyntaxPalette:
    """17 syntax color roles + foreground/background.

    Cluster hues are derived from coloraide harmony('wheel', count=8),
    guaranteeing 45° separation between every adjacent cluster.
    Lightness is set by targeting CIELab L* per tier for perceptual uniformity.
    Contrast floors are per-role: 4.5:1 for all text roles (WCAG AA).
    """

    keyword: TCol
    control: TCol
    type: TCol
    function: TCol
    string: TCol
    number: TCol
    comment: TCol
    function_decl: TCol
    namespace: TCol
    field: TCol
    field_const: TCol
    escape: TCol
    metadata: TCol
    enum_member: TCol
    param: TCol
    punct: TCol
    deprecated: TCol
    foreground: TCol
    background: TCol
    hue_shifted: list[TCol]
    """6 hue-rotated colors from enum_member for brackets, SCM graph, and headings."""

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        *,
        string_hue: float = 40.0,
        background: TCol,
        foreground: TCol | None = None,
        is_dark: bool = False,
        lightness: float = 0.50,
        chroma_scale: float = 1.0,
    ) -> Self:
        """Generate all syntax colors from minimal parameters.

        string_hue seeds the harmony wheel at the string/brown cluster (40° by
        default, matching Rider Light's #8C6C41). The remaining 7 clusters are
        placed at 45° intervals by coloraide's wheel harmony in OkLCh space.

        background is the editor background -- used for WCAG AA correction.
        foreground overrides the default foreground (black for light, light gray for dark).
        Lightness per role is set by targeting CIELab L* (see _SPECS).
        Contrast floors are per-role (see _SPECS and module docstring).
        """
        # Derive 8 evenly-spaced hues via coloraide harmony
        seed = Color("oklch", [lightness, _C_MID * chroma_scale, string_hue])
        wheel = seed.harmony("wheel", count=8, space="oklch")
        hues = [c.get("hue") % 360 for c in wheel]

        def _make(role: str) -> TCol:
            cluster_idx, lab_l_target, c_band, floor = _SPECS[role]
            if is_dark:
                lab_l_target = _LIGHT_TO_DARK_LAB[lab_l_target]
            hue = hues[cluster_idx]
            chrom = c_band * chroma_scale
            if is_dark:
                chrom *= _DARK_CHROMA_SCALE
            col = TCol.from_lab_l(lab_l_target, chrom, hue)
            return col.with_min_contrast(background, floor)

        colors = {role: _make(role) for role in _SPECS}
        if foreground is None:
            # Fallback foreground -- normally provided by Theme.create() from Palette
            foreground = TCol.from_oklch(0.83, 0.0, 0.0) if is_dark else TCol.from_oklch(0.0, 0.0, 0.0)
        return cls(
            **colors,
            foreground=foreground,
            background=background,
            hue_shifted=hue_series(colors["enum_member"], _HUE_SERIES_COUNT),
        )
