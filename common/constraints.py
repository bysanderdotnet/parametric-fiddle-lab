"""Ergonomic and playability constraint validation.

Validates a violin parameter set against luthiery best-practice constraints:
left-hand reach (neck), string spacing, scale length, fingerboard curvature,
and bow clearance at the C-bout. Returns a list of human-readable violation
messages (empty = all pass).
"""

STRING_COUNT = 4

# -- String spacing constraints --
# Violins have 4 strings. Adjacent pair spacing at nut ~5.5-8.5 mm.
# At bridge, standard 4/4 violin bridge is ~41-42 mm wide -> spacing
# ~13.7-14.0 mm between outer E and G strings.
MIN_STRING_SPACING_NUT = 5.5
MAX_STRING_SPACING_NUT = 8.5
MIN_STRING_SPACING_BRIDGE = 8.0
MAX_STRING_SPACING_BRIDGE = 14.5

# -- Scale length --
# Full-size violin 4:4 scale is ~328-330 mm (nut to bridge).
# 7/8 (~310 mm), 3/4 (~280 mm). We target full-size range.
SCALE_LENGTH_MIN = 310.0
SCALE_LENGTH_MAX = 335.0

# -- Neck width (left-hand reach) --
# Full-size: ~23-24 mm at nut, ~34-36 mm at body joint.
# Too wide = small hands can't reach; too narrow = cramped spacing.
NECK_WIDTH_TOP_MIN = 22.0
NECK_WIDTH_TOP_MAX = 27.0
NECK_WIDTH_BOTTOM_MIN = 32.0
NECK_WIDTH_BOTTOM_MAX = 38.0

# -- Fingerboard curvature (radius) --
# 42 mm is standard violin "medium" radius. Flatter = easier double stops,
# rounder = easier single-string fingering. 36-50 mm accepted range.
FINGERBOARD_RADIUS_MIN = 36.0
FINGERBOARD_RADIUS_MAX = 50.0

# -- Bow clearance at C-bout --
# The bow can hit the C-bout upper/lower corners when bowing the outer
# strings (E and G). The relevant distance is from the outer string path
# (at the bridge) to the nearest protruding C-bout corner. A violin bow
# has ~5-6 mm diameter; we need at least 5 mm clearance.
BOW_CLEARANCE_C_BOUT_MIN = 5.0


def _string_spacing_nut(neck_width_top):
    return neck_width_top / (STRING_COUNT - 1)


def _string_spacing_bridge(bridge_width_bottom):
    return bridge_width_bottom / (STRING_COUNT - 1)


def _scale_length(body_length, neck_length, bridge_y_offset):
    """Vibrating string length = nut-to-bridge distance.

    Nut is at y = body_length/2 + neck_length.
    Bridge is at y = bridge_y_offset (default 0), approximately at the
    center of the F-holes / bridge area.
    """
    return body_length / 2.0 + neck_length - bridge_y_offset


def check_neck_width(neck_width_top, neck_width_bottom):
    errors = []
    if neck_width_top < NECK_WIDTH_TOP_MIN:
        errors.append(
            f"neck_width_top ({neck_width_top:.1f}) < min ({NECK_WIDTH_TOP_MIN}) -- "
            "neck too narrow at nut; string spacing cramped"
        )
    if neck_width_top > NECK_WIDTH_TOP_MAX:
        errors.append(
            f"neck_width_top ({neck_width_top:.1f}) > max ({NECK_WIDTH_TOP_MAX}) -- "
            "neck too wide at nut; hard for small hands to reach"
        )
    if neck_width_bottom < NECK_WIDTH_BOTTOM_MIN:
        errors.append(
            f"neck_width_bottom ({neck_width_bottom:.1f}) < min ({NECK_WIDTH_BOTTOM_MIN}) -- "
            "neck too narrow at body joint; may feel unstable"
        )
    if neck_width_bottom > NECK_WIDTH_BOTTOM_MAX:
        errors.append(
            f"neck_width_bottom ({neck_width_bottom:.1f}) > max ({NECK_WIDTH_BOTTOM_MAX}) -- "
            "neck too wide at body joint; left-hand reach compromised"
        )
    return errors


def check_string_spacing(neck_width_top, bridge_width_bottom):
    errors = []
    s_nut = _string_spacing_nut(neck_width_top)
    s_bridge = _string_spacing_bridge(bridge_width_bottom)

    if s_nut < MIN_STRING_SPACING_NUT:
        errors.append(
            f"string spacing at nut ({s_nut:.2f} mm) < min ({MIN_STRING_SPACING_NUT}) -- "
            "strings too close for precise fingering"
        )
    if s_nut > MAX_STRING_SPACING_NUT:
        errors.append(
            f"string spacing at nut ({s_nut:.2f} mm) > max ({MAX_STRING_SPACING_NUT}) -- "
            "strings too far apart, awkward for chord shapes"
        )
    if s_bridge < MIN_STRING_SPACING_BRIDGE:
        errors.append(
            f"string spacing at bridge ({s_bridge:.2f} mm) < min ({MIN_STRING_SPACING_BRIDGE}) -- "
            "strings too close for clear bowing"
        )
    if s_bridge > MAX_STRING_SPACING_BRIDGE:
        errors.append(
            f"string spacing at bridge ({s_bridge:.2f} mm) > max ({MAX_STRING_SPACING_BRIDGE}) -- "
            "strings too far apart; bow-arm strain"
        )

    if s_bridge <= s_nut:
        errors.append(
            f"bridge spacing ({s_bridge:.2f}) <= nut spacing ({s_nut:.2f}) -- "
            "strings must fan outward from nut to bridge"
        )
    return errors


def check_scale_length(body_length, neck_length, fingerboard_length, bridge_y_offset):
    errors = []
    scale = _scale_length(body_length, neck_length, bridge_y_offset)
    if scale < SCALE_LENGTH_MIN:
        errors.append(
            f"scale length ({scale:.1f} mm) < min ({SCALE_LENGTH_MIN}) -- "
            "string tension too low; pitch and response suffer"
        )
    if scale > SCALE_LENGTH_MAX:
        errors.append(
            f"scale length ({scale:.1f} mm) > max ({SCALE_LENGTH_MAX}) -- "
            "string tension too high; hard to press and bend"
        )
    return errors


def check_fingerboard_curvature(fingerboard_radius):
    errors = []
    if fingerboard_radius < FINGERBOARD_RADIUS_MIN:
        errors.append(
            f"fingerboard_radius ({fingerboard_radius:.1f} mm) < min ({FINGERBOARD_RADIUS_MIN}) -- "
            "too curved; single-string fingering awkward"
        )
    if fingerboard_radius > FINGERBOARD_RADIUS_MAX:
        errors.append(
            f"fingerboard_radius ({fingerboard_radius:.1f} mm) > max ({FINGERBOARD_RADIUS_MAX}) -- "
            "too flat; double-stop fingering unstable"
        )
    return errors


def check_bow_clearance(c_bout, bridge_width_bottom, upper_bout, lower_bout):
    """Check bow clearance at C-bout corners.

    The bow contacts strings between bridge and fingerboard. The C-bout
    upper/lower corners protrude inward from the bouts. The relevant
    clearance is from the outer string x-position at the bridge
    (bridge_width_bottom/2) to the nearest C-bout corner x-position,
    approximated as the minimum of upper_bout/2 and lower_bout/2.
    """
    errors = []
    outer_string_x = bridge_width_bottom / 2.0
    bout_clearance_x = min(upper_bout, lower_bout) / 2.0
    clearance = bout_clearance_x - outer_string_x
    if clearance < BOW_CLEARANCE_C_BOUT_MIN:
        errors.append(
            f"bow clearance at C-bout corners ({clearance:.1f} mm) < min "
            f"({BOW_CLEARANCE_C_BOUT_MIN}) -- "
            "bow may hit the C-bout corners when bowing outer strings"
        )
    return errors


def validate(params):
    """Run all ergonomic and playability constraints on a parameter dict.

    Parameters
    ----------
    params : dict
        Must contain keys for all relevant geometry parameters.
        Expected keys: neck_width_top, neck_width_bottom, bridge_width_bottom,
        neck_length, length (body), fingerboard_length, bridge_y_offset,
        fingerboard_radius, c_bout, upper_bout, lower_bout.

    Returns
    -------
    errors : list of str
        Human-readable constraint violations. Empty list = all pass.
    """
    errors = []
    errors += check_neck_width(
        params.get("neck_width_top", 24.0),
        params.get("neck_width_bottom", 34.0),
    )
    errors += check_string_spacing(
        params.get("neck_width_top", 24.0),
        params.get("bridge_width_bottom", 40.0),
    )
    errors += check_scale_length(
        params.get("length", 355.0),
        params.get("neck_length", 130.0),
        params.get("fingerboard_length", 270.0),
        params.get("bridge_y_offset", 0.0),
    )
    errors += check_fingerboard_curvature(
        params.get("fingerboard_radius", 42.0),
    )
    errors += check_bow_clearance(
        params.get("c_bout", 110.0),
        params.get("bridge_width_bottom", 40.0),
        params.get("upper_bout", 168.0),
        params.get("lower_bout", 208.0),
    )
    return errors
