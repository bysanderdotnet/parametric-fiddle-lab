import os
import json
import pytest
import sys

# Ensure scripts directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.generate_historical_profiles import generate_historical_profiles

def test_generate_historical_profiles_creates_files():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    expected_files = [
        "stradivarius.json",
        "guarneri.json",
        "amati.json",
        "historical_comparison.md"
    ]

    # Ensure starting clean
    for file in expected_files:
        filepath = os.path.join(base_dir, file)
        if os.path.exists(filepath):
            os.remove(filepath)

    generate_historical_profiles()

    for file in expected_files:
        filepath = os.path.join(base_dir, file)
        assert os.path.exists(filepath), f"{file} was not created"

    # Check specific fields in one of the jsons
    with open(os.path.join(base_dir, "stradivarius.json"), 'r') as f:
        params = json.load(f)

    assert "length" in params
    assert params["length"] == 355.5
    assert params["upper_bout"] == 168.0
    assert params["c_bout"] == 111.0
    assert params["lower_bout"] == 208.0
    assert params["f_hole_profile"] == "classic"

    # Check that comparison report contains the right text
    with open(os.path.join(base_dir, "historical_comparison.md"), 'r') as f:
        md = f.read()

    assert "Historical Violin Profiles Comparison" in md
    assert "Stradivarius" in md
    assert "Guarneri" in md
    assert "Amati" in md
    assert "back_arch_height" in md

    # Clean up
    for file in expected_files:
        filepath = os.path.join(base_dir, file)
        if os.path.exists(filepath):
            os.remove(filepath)
