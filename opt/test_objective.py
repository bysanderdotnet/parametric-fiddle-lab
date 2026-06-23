import json
import os
import tempfile
from unittest.mock import patch
from objective import evaluate_objective

@patch('builtins.open', side_effect=FileNotFoundError)
def test_evaluate_objective_default_fallback(mock_open):
    # Test fallback to defaults when no files exist
    score, result_str = evaluate_objective()

    # Verify score with defaults
    # a0_freq=300, target_a0=280 -> diff 20
    # b1_minus_freq=400, target_struct=450 -> diff 50
    # b1_plus_freq=500, target_b1_plus=540 -> diff 40
    # mass_g=400 -> 40
    # vol=300000 -> 30
    # components (21) = top+back+bridge+soundpost+bassbar+tailpiece+chinrest+finetuners+saddle+strings+nut+pegs+fingerboard+endpin+neck+scroll+topblock+bottomblock+cornerblocks
    # component values: 4, 4, 2, 1, 5, 10, 15, 0.5, 1, 1.5, 2, 5, 10, 2, 15, 5, 10, 10, 10 = 113.0
    # 113 * 5 = 565
    # total expected = 20 + 50 + 40 + 40 + 30 + 565 = 745
    expected_score = 745.0

    assert abs(score - expected_score) < 1e-6
    assert "A0=300.0Hz" in result_str
    assert "B1-=400.0Hz" in result_str
    assert "Score=745.00" in result_str

@patch('builtins.open')
def test_evaluate_objective_with_mock_files(mock_open):
    # Set up mock file data
    body_data = {
        "mass_g": 350.0,
        "volume_mm3": 250000.0,
        "top_thickness": 3.0,
        "back_thickness": 3.5,
        "bridge_mass_g": 2.5,
        "soundpost_mass_g": 1.2,
        "bass_bar_mass_g": 4.5,
        "tailpiece_mass_g": 9.0,
        "chinrest_mass_g": 14.0,
        "fine_tuners_mass_g": 0.0,
        "saddle_mass_g": 0.8,
        "strings_mass_g": 1.2,
        "nut_mass_g": 1.8,
        "pegs_mass_g": 4.0,
        "fingerboard_mass_g": 9.5,
        "endpin_mass_g": 1.5,
        "neck_mass_g": 12.0,
        "scroll_mass_g": 4.5,
        "top_block_mass_g": 8.0,
        "bottom_block_mass_g": 8.0,
        "corner_blocks_mass_g": 8.0
    }

    struct_data = {
        "eigenmodes": [
            {"frequency_hz": 310.0, "description": "CBR mode"},
            {"frequency_hz": 420.0, "description": "B1- mode"},
            {"frequency_hz": 520.0, "description": "B1+ mode"}
        ]
    }

    acoustic_data = {
        "cavity_modes": [
            {"frequency_hz": 285.0, "description": "A0 mode"},
            {"frequency_hz": 460.0, "description": "A1 mode"}
        ]
    }

    def mock_open_impl(filename, *args, **kwargs):
        if filename == "violin_body.json":
            return json.dumps(body_data)
        elif filename == "structural_results.json":
            return json.dumps(struct_data)
        elif filename == "acoustic_results.json":
            return json.dumps(acoustic_data)
        raise FileNotFoundError(filename)

    # Use a custom side effect to return a mock file object with the correct read() content
    class MockFile:
        def __init__(self, content):
            self.content = content
        def read(self):
            return self.content
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def side_effect(filename, *args, **kwargs):
        try:
            return MockFile(mock_open_impl(filename))
        except FileNotFoundError:
            raise

    mock_open.side_effect = side_effect

    score, result_str = evaluate_objective()

    # Calculate expected score:
    # a0_freq=285, target_a0=280 -> diff 5
    # b1_minus_freq=420, target_struct=450 -> diff 30
    # b1_plus_freq=520, target_b1_plus=540 -> diff 20
    # mass_g=350 -> 35
    # vol=250000 -> 25
    # comp sums = 3 + 3.5 + 2.5 + 1.2 + 4.5 + 9.0 + 14.0 + 0 + 0.8 + 1.2 + 1.8 + 4.0 + 9.5 + 1.5 + 12.0 + 4.5 + 8.0 + 8.0 + 8.0 = 97.0
    # 97 * 5 = 485
    # total expected = 5 + 30 + 20 + 35 + 25 + 485 = 600
    expected_score = 600.0

    assert abs(score - expected_score) < 1e-6
    assert "A0=285.0Hz" in result_str
    assert "A1=460.0Hz" in result_str
    assert "CBR=310.0Hz" in result_str
    assert "B1-=420.0Hz" in result_str
    assert "B1+=520.0Hz" in result_str
    assert "Mass=350.0g" in result_str
    assert "Top=3.0mm" in result_str
    assert "Score=600.00" in result_str


@patch('builtins.open')
def test_evaluate_objective_fallback_modes(mock_open):
    # Test fallback when modes do not have proper descriptions
    struct_data = {
        "eigenmodes": [
            {"frequency_hz": 90.0, "description": ""},
            {"frequency_hz": 415.0, "description": ""}, # Should be picked as B1- (first real > 100)
            {"frequency_hz": 500.0, "description": ""}
        ]
    }

    acoustic_data = {
        "cavity_modes": [
            {"frequency_hz": 295.0, "description": ""}, # Should be picked as A0 (first one)
            {"frequency_hz": 460.0, "description": ""}
        ]
    }

    class MockFile:
        def __init__(self, content):
            self.content = content
        def read(self):
            return self.content
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def side_effect(filename, *args, **kwargs):
        if filename == "structural_results.json":
            return MockFile(json.dumps(struct_data))
        elif filename == "acoustic_results.json":
            return MockFile(json.dumps(acoustic_data))
        raise FileNotFoundError(filename)

    mock_open.side_effect = side_effect

    score, result_str = evaluate_objective()

    assert "A0=295.0Hz" in result_str
    assert "B1-=500.0Hz" in result_str # Fallback takes 2nd mode > 100Hz
