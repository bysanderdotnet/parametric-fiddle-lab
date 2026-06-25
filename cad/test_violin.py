import os
import sys
import json
import subprocess
import pytest
import cadquery as cq
from violin import create_violin_body, load_step, save_step

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

    # Clean up
    for file in ["violin_body.step", "violin_cavity.step", "violin_body.json"]:
        if os.path.exists(file):
            os.remove(file)
