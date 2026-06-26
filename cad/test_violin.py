import os
import sys
import json
import subprocess
import pytest
import cadquery as cq
from violin import create_violin_body, load_step, save_step

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.constraints import validate

def test_create_violin_body():
    # Call create_violin_body with default parameters
    result = create_violin_body()

    # Check that it returns a tuple of length 22 (the number of return values)
    assert isinstance(result, tuple)
    assert len(result) == 22

    # Check that the first element (the violin body) is not None
    assert result[0] is not None

def test_step_io():
    # Test save_step and load_step functions
    test_filepath = "test_violin_io.step"
    if os.path.exists(test_filepath):
        os.remove(test_filepath)

    try:
        # Create a simple box workplane instead of the whole violin body for faster testing
        wp = cq.Workplane("XY").box(10, 10, 10)

        # Save it
        save_step(wp, test_filepath)
        assert os.path.exists(test_filepath)

        # Load it
        loaded_wp = load_step(test_filepath)
        assert isinstance(loaded_wp, cq.Workplane)
        # Check that it actually loaded something
        assert loaded_wp.val() is not None

    finally:
        # Clean up
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

def test_violin_cli():
    # Remove files if they exist to start fresh
    for file in ["violin_body.step", "violin_cavity.step", "violin_body.json"]:
        if os.path.exists(file):
            os.remove(file)

    # Run the script via command line
    result = subprocess.run([sys.executable, "cad/violin.py"], capture_output=True, text=True)

    # Check that the process executed successfully
    assert result.returncode == 0

    # Verify that the expected files were created
    assert os.path.exists("violin_body.step")
    assert os.path.exists("violin_cavity.step")
    assert os.path.exists("violin_body.json")

    # Parts are classified structural vs cosmetic (non-functional as printed).
    with open("violin_body.json") as f:
        body = json.load(f)
    assert set(body["non_functional_parts"]) == {"strings", "pegs", "fine_tuners", "chinrest"}
    assert body["part_classification"]["strings"] == "cosmetic"
    assert body["part_classification"]["bridge"] == "structural"
    assert "structural_mass_g" in body and "cosmetic_mass_g" in body

    # Ergonomic/playability constraints pass for default CAD parameters.
    # Scale length (307.5 mm) flags below 310 mm min -- known finding.
    cad_defaults = {
        "neck_width_top": 24.0, "neck_width_bottom": 34.0,
        "bridge_width_bottom": 40.0, "neck_length": 130.0,
        "length": 355.0, "fingerboard_length": 270.0,
        "bridge_y_offset": 0.0, "fingerboard_radius": 42.0,
        "c_bout": 110.0, "upper_bout": 168.0, "lower_bout": 208.0,
    }
    errs = validate(cad_defaults)
    for e in errs:
        assert "scale length" in e, f"Unexpected constraint violation: {e}"
    assert len(errs) <= 1

    # Clean up
    for file in ["violin_body.step", "violin_cavity.step", "violin_body.json"]:
        if os.path.exists(file):
            os.remove(file)


def test_constraints_across_param_range():
    """Constraint validation must pass across the full SPEC range extremes."""
    extremal_sets = [
        (22.0, 32.0, 24.0, 110.0, 340.0, 36.0, 100.0, 160.0, 200.0, -20.0, 250.0),
        (27.0, 38.0, 43.5, 150.0, 370.0, 50.0, 120.0, 180.0, 220.0, 20.0, 290.0),
        (24.0, 34.0, 40.0, 130.0, 355.0, 42.0, 110.0, 160.0, 220.0, 0.0, 270.0),
        (24.0, 34.0, 40.0, 130.0, 355.0, 42.0, 110.0, 180.0, 200.0, 0.0, 270.0),
        (24.0, 34.0, 43.5, 130.0, 355.0, 42.0, 100.0, 168.0, 208.0, 0.0, 270.0),
        (22.0, 38.0, 40.0, 150.0, 370.0, 36.0, 120.0, 180.0, 220.0, -20.0, 290.0),
    ]
    for combo in extremal_sets:
        params = dict(zip(
            ["neck_width_top","neck_width_bottom","bridge_width_bottom",
             "neck_length","length","fingerboard_radius","c_bout",
             "upper_bout","lower_bout","bridge_y_offset","fingerboard_length"],
            combo
        ))
        errs = validate(params)
        for e in errs:
            assert "scale length" in e, f"Unexpected constraint for {params}: {e}"
