import os
import json
import pytest
import sys

# Ensure scripts directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.generate_stradivarius import generate_stradivarius_parameters

def test_generate_stradivarius_creates_file():
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'stradivarius.json'))

    if os.path.exists(output_path):
        os.remove(output_path)

    generate_stradivarius_parameters()

    assert os.path.exists(output_path), "stradivarius.json was not created"

    with open(output_path, 'r') as f:
        params = json.load(f)

    assert "length" in params
    assert params["length"] == 355.5
    assert params["upper_bout"] == 168.0
    assert params["c_bout"] == 111.0
    assert params["lower_bout"] == 208.0
    assert params["f_hole_profile"] == "classic"

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)
