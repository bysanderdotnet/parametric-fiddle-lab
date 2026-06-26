import os
import sys

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
_REPO_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
sys.path.insert(0, _REPO_DIR)

import importlib.util
_spec = importlib.util.spec_from_file_location("calibrate_objective",
    os.path.join(_SCRIPT_DIR, "calibrate_objective.py"))
_cal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cal)
load_reference = _cal.load_reference
compute_correlation = _cal.compute_correlation
compute_weighted_targets = _cal.compute_weighted_targets
calibrate = _cal.calibrate
MODE_KEYS = _cal.MODE_KEYS


def test_load_reference():
    ref_path = os.path.join(_REPO_DIR, 'data', 'reference_measurements.json')
    ref = load_reference(ref_path)
    assert "entries" in ref
    assert len(ref["entries"]) >= 5
    assert "calibration_targets" in ref
    assert ref["calibration_targets"]["a0_hz"] == 285.0


def test_compute_correlation_perfect():
    xs = [1, 2, 3, 4, 5]
    corr = compute_correlation(xs, xs)
    assert corr is not None
    assert abs(corr - 1.0) < 1e-10


def test_compute_correlation_inverse():
    xs = [1, 2, 3, 4, 5]
    ys = [5, 4, 3, 2, 1]
    corr = compute_correlation(xs, ys)
    assert corr is not None
    assert abs(corr - (-1.0)) < 1e-10


def test_compute_correlation_insufficient():
    assert compute_correlation([1, 2], [1, 2]) is None
    assert compute_correlation([1], [1]) is None
    assert compute_correlation([], []) is None


def test_compute_correlation_constant():
    xs = [1, 2, 3, 4, 5]
    ys = [5, 5, 5, 5, 5]
    assert compute_correlation(xs, ys) is None


def test_compute_weighted_targets():
    entries = [
        {"id": "a", "mass_g": 400.0, "modes": {"a0_hz": 300.0, "b1_minus_hz": 400.0, "b1_plus_hz": 500.0}},
        {"id": "b", "mass_g": 200.0, "modes": {"a0_hz": 280.0, "b1_minus_hz": 420.0, "b1_plus_hz": 550.0}},
    ]
    targets = compute_weighted_targets(entries)
    assert abs(targets["a0_hz"] - 286.67) < 0.1
    assert abs(targets["b1_minus_hz"] - 413.33) < 0.1
    assert abs(targets["b1_plus_hz"] - 533.33) < 0.1


def test_calibrate_report_contains_targets():
    entries = [
        {"id": "test-1", "mass_g": 380.0, "label": "test",
         "modes": {"a0_hz": 285.0, "a1_hz": 460.0, "b1_minus_hz": 410.0,
                   "b1_plus_hz": 535.0, "cbr_hz": 320.0}}
    ]
    report = calibrate(entries)
    assert "Calibrated Targets" in report
    assert "target_a0_hz" in report


def test_calibrate_with_sim_mappings():
    entries = [
        {"id": "test-1", "mass_g": 380.0, "label": "test",
         "modes": {"a0_hz": 285.0, "a1_hz": 460.0, "b1_minus_hz": 410.0,
                   "b1_plus_hz": 535.0, "cbr_hz": 320.0}}
    ]
    sim_mappings = [
        {"entry_id": "test-1", "simulation": {"a0_hz": 280.0, "a1_hz": 455.0,
                                               "b1_minus_hz": 405.0, "b1_plus_hz": 530.0,
                                               "cbr_hz": 315.0}}
    ]
    report = calibrate(entries, sim_mappings=sim_mappings)
    assert "Simulation vs Measurement" in report
    assert "MEETS TARGET" in report


def test_calibrate_report_entry_table():
    entries = [
        {"id": "e1", "mass_g": 350.0, "label": "x",
         "modes": {"a0_hz": 280.0, "a1_hz": 450.0, "b1_minus_hz": 400.0,
                   "b1_plus_hz": 530.0, "cbr_hz": 310.0}},
        {"id": "e2", "mass_g": 420.0, "label": "y",
         "modes": {"a0_hz": 290.0, "a1_hz": 470.0, "b1_minus_hz": 420.0,
                   "b1_plus_hz": 540.0, "cbr_hz": 330.0}},
    ]
    report = calibrate(entries)
    for eid in ["e1", "e2"]:
        assert eid in report
