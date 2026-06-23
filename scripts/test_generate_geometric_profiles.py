import os
import json
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.generate_geometric_profiles import generate_profiles

def test_generate_geometric_profiles_creates_files():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    files_to_check = {
        'stradivarius.json': {
            'length': 355.5,
            'upper_bout': 168.0,
            'f_hole_profile': 'classic'
        },
        'guarneri.json': {
            'length': 354.0,
            'c_bout': 112.0,
            'rib_height': 31.0
        },
        'amati.json': {
            'length': 352.0,
            'lower_bout': 202.0,
            'top_arch_height': 18.0
        }
    }

    # Clean up before testing
    for filename in files_to_check:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            os.remove(path)

    generate_profiles()

    for filename, expected_values in files_to_check.items():
        path = os.path.join(base_dir, filename)
        assert os.path.exists(path), f"{filename} was not created"

        with open(path, 'r') as f:
            params = json.load(f)

        for key, expected_value in expected_values.items():
            assert key in params
            assert params[key] == expected_value, f"Expected {key} to be {expected_value} in {filename}, got {params[key]}"

        # Clean up after testing
        if os.path.exists(path):
            os.remove(path)
