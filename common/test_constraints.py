"""Unit tests for ergonomic and playability constraints."""

import pytest
from common.constraints import (
    validate,
    check_neck_width,
    check_string_spacing,
    check_scale_length,
    check_fingerboard_curvature,
    check_bow_clearance,
    NECK_WIDTH_TOP_MIN,
    NECK_WIDTH_TOP_MAX,
    NECK_WIDTH_BOTTOM_MIN,
    NECK_WIDTH_BOTTOM_MAX,
    MIN_STRING_SPACING_NUT,
    MAX_STRING_SPACING_NUT,
    MIN_STRING_SPACING_BRIDGE,
    MAX_STRING_SPACING_BRIDGE,
    SCALE_LENGTH_MIN,
    SCALE_LENGTH_MAX,
    FINGERBOARD_RADIUS_MIN,
    FINGERBOARD_RADIUS_MAX,
    BOW_CLEARANCE_C_BOUT_MIN,
    STRING_COUNT,
)

DEFAULTS = {
    "neck_width_top": 24.0,
    "neck_width_bottom": 34.0,
    "bridge_width_bottom": 40.0,
    "neck_length": 130.0,
    "length": 355.0,
    "fingerboard_length": 270.0,
    "bridge_y_offset": 0.0,
    "fingerboard_radius": 42.0,
    "c_bout": 110.0,
    "upper_bout": 168.0,
    "lower_bout": 208.0,
}


def default_params(**overrides):
    p = dict(DEFAULTS)
    p.update(overrides)
    return p


# -- validate() happy path --------------------------------------------

def test_default_params_pass():
    """Default CAD params: scale is 307.5mm (<310 min), bridge spacing 13.33mm OK.
    The scale length violation is a real finding -- the default neck+body produce
    a slightly short scale for full-size 4/4."""
    errs = validate(DEFAULTS)
    assert all("scale length" in e for e in errs)
    assert len(errs) == 1


# -- neck width -------------------------------------------------------

def test_neck_width_ok():
    assert check_neck_width(24.0, 34.0) == []


def test_neck_width_top_too_narrow():
    errs = check_neck_width(NECK_WIDTH_TOP_MIN - 1, 34.0)
    assert any("neck_width_top" in e and "min" in e for e in errs)


def test_neck_width_top_too_wide():
    errs = check_neck_width(NECK_WIDTH_TOP_MAX + 1, 34.0)
    assert any("neck_width_top" in e and "max" in e for e in errs)


def test_neck_width_bottom_too_narrow():
    errs = check_neck_width(24.0, NECK_WIDTH_BOTTOM_MIN - 1)
    assert any("neck_width_bottom" in e and "min" in e for e in errs)


def test_neck_width_bottom_too_wide():
    errs = check_neck_width(24.0, NECK_WIDTH_BOTTOM_MAX + 1)
    assert any("neck_width_bottom" in e and "max" in e for e in errs)


# -- string spacing ---------------------------------------------------

def test_string_spacing_ok():
    assert check_string_spacing(24.0, 40.0) == []


def test_string_spacing_nut_too_close():
    errs = check_string_spacing(16.0, 40.0)
    assert any("string spacing at nut" in e and "min" in e for e in errs)


def test_string_spacing_nut_too_wide():
    errs = check_string_spacing(30.0, 40.0)
    assert any("string spacing at nut" in e and "max" in e for e in errs)


def test_string_spacing_bridge_too_close():
    errs = check_string_spacing(24.0, 20.0)
    assert any("string spacing at bridge" in e and "min" in e for e in errs)


def test_string_spacing_bridge_too_wide():
    errs = check_string_spacing(24.0, 50.0)
    assert any("string spacing at bridge" in e and "max" in e for e in errs)


def test_string_spacing_negative_fan():
    errs = check_string_spacing(30.0, 30.0)
    assert any("must fan outward" in e for e in errs)


# -- scale length -----------------------------------------------------

def test_scale_length_ok():
    assert check_scale_length(360.0, 135.0, 275.0, -15.0) == []


def test_scale_length_ok_with_bridge_offset():
    assert check_scale_length(355.0, 130.0, 270.0, -20.0) == []


def test_scale_length_too_short():
    errs = check_scale_length(340.0, 100.0, 250.0, 0.0)
    assert any("scale length" in e and "min" in e for e in errs)


def test_scale_length_too_long():
    errs = check_scale_length(370.0, 150.0, 290.0, -20.0)
    assert any("scale length" in e and "max" in e for e in errs)


# -- fingerboard curvature --------------------------------------------

def test_fingerboard_curvature_ok():
    assert check_fingerboard_curvature(42.0) == []


def test_fingerboard_curvature_too_curved():
    errs = check_fingerboard_curvature(FINGERBOARD_RADIUS_MIN - 5)
    assert any("too curved" in e for e in errs)


def test_fingerboard_curvature_too_flat():
    errs = check_fingerboard_curvature(FINGERBOARD_RADIUS_MAX + 5)
    assert any("too flat" in e for e in errs)


# -- bow clearance ----------------------------------------------------

def test_bow_clearance_ok():
    assert check_bow_clearance(110.0, 40.0, 168.0, 208.0) == []


def test_bow_clearance_bridge_wider_than_bout():
    errs = check_bow_clearance(110.0, 180.0, 168.0, 208.0)
    assert any("bow clearance" in e for e in errs)


def test_bow_clearance_tight_upper_bout():
    assert check_bow_clearance(110.0, 40.0, 52.0, 208.0) == []


def test_bow_clearance_bridge_wider_than_lower_bout():
    errs = check_bow_clearance(110.0, 220.0, 168.0, 208.0)
    assert any("bow clearance" in e for e in errs)


# -- integration: validate() with various param sets ------------------

def test_validate_defaults():
    errs = validate(DEFAULTS)
    assert len(errs) == 1
    assert "scale length" in errs[0]


def test_validate_all_violations():
    bad = default_params(
        neck_width_top=18.0,
        neck_width_bottom=28.0,
        bridge_width_bottom=20.0,
        neck_length=100.0,
        length=340.0,
        fingerboard_radius=20.0,
        c_bout=120.0,
        upper_bout=40.0,
        lower_bout=50.0,
    )
    errs = validate(bad)
    assert len(errs) >= 4


def test_validate_boundary_pass():
    ok = default_params(
        neck_width_top=NECK_WIDTH_TOP_MIN,
        neck_width_bottom=NECK_WIDTH_BOTTOM_MIN,
        bridge_width_bottom=MIN_STRING_SPACING_BRIDGE * (STRING_COUNT - 1),
        neck_length=135.0,
        length=2 * (SCALE_LENGTH_MIN - 135.0 - 15.0),
        bridge_y_offset=-15.0,
        fingerboard_radius=FINGERBOARD_RADIUS_MIN,
        c_bout=110.0,
        upper_bout=2 * (MIN_STRING_SPACING_BRIDGE * (STRING_COUNT - 1) / 2.0 + BOW_CLEARANCE_C_BOUT_MIN),
        lower_bout=208.0,
    )
    errs = validate(ok)
    assert errs == []


# -- derived metric helpers -------------------------------------------

def test_string_spacing_derivation():
    from common.constraints import _string_spacing_nut, _string_spacing_bridge
    assert _string_spacing_nut(24.0) == pytest.approx(8.0)
    assert _string_spacing_bridge(40.0) == pytest.approx(40.0 / 3.0)


def test_scale_length_derivation():
    from common.constraints import _scale_length
    assert _scale_length(355.0, 130.0, 0.0) == pytest.approx(307.5)
