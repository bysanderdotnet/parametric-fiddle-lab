import json
import os
import tempfile
from unittest.mock import patch
from objective import evaluate_objective

@patch('builtins.open', side_effect=FileNotFoundError)
def test_evaluate_objective_default_fallback(mock_open):
    # Test fallback to defaults when no files exist
    score, result_str = evaluate_objective()

    # All three result files missing -> neutral default frequencies, but the
    # trial is charged the missing-data penalty so a total failure cannot score
    # well by hiding behind rosy defaults.
    # freq_error = |300-290| + |400-400| + |500-540| = 10 + 0 + 40 = 50
    # mass_penalty = 0.05 * 400 = 20
    # data_penalty = 1000 * 3 (body + struct + acoustic all missing) = 3000
    expected_score = 3070.0

    assert abs(score - expected_score) < 1e-6
    assert "A0=300.0Hz" in result_str
    assert "B1-=400.0Hz" in result_str
    assert "Score=3070.00" in result_str

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

    # Calculate expected score (frequency matching dominates; mass is a mild
    # regularizer; all three result sources present so no data penalty):
    # freq_error = |285-290| + |420-400| + |520-540| = 5 + 20 + 20 = 45
    # mass_penalty = 0.05 * 350 = 17.5
    # data_penalty = 0
    expected_score = 62.5

    assert abs(score - expected_score) < 1e-6
    assert "A0=285.0Hz" in result_str
    assert "A1=460.0Hz" in result_str
    assert "CBR=310.0Hz" in result_str
    assert "B1-=420.0Hz" in result_str
    assert "B1+=520.0Hz" in result_str
    assert "Mass=350.0g" in result_str
    assert "Top=3.0mm" in result_str
    assert "Score=62.50" in result_str


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


@patch('builtins.open')
def test_evaluate_objective_single_fallback_mode(mock_open):
    # Test fallback when modes do not have proper descriptions and only 1 valid mode exists
    struct_data = {
        "eigenmodes": [
            {"frequency_hz": 90.0, "description": ""},
            {"frequency_hz": 415.0, "description": ""} # Should be picked as B1- (only real > 100)
        ]
    }

    acoustic_data = {
        "cavity_modes": [
            {"frequency_hz": 295.0, "description": "A0"}
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
        if filename == "violin_body.json":
            return MockFile(json.dumps({}))
        raise FileNotFoundError(filename)

    mock_open.side_effect = side_effect

    score, result_str = evaluate_objective()
    assert "B1-=415.0Hz" in result_str # Fallback takes the only mode > 100Hz

@patch('builtins.open')
def test_evaluate_objective_no_fallback_modes(mock_open):
    # Test fallback when modes do not have proper descriptions and no modes > 100Hz
    struct_data = {
        "eigenmodes": [
            {"frequency_hz": 90.0, "description": ""},
            {"frequency_hz": 95.0, "description": ""}
        ]
    }

    acoustic_data = {
        "cavity_modes": [
            {"frequency_hz": 295.0, "description": "A0"}
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
        if filename == "violin_body.json":
            return MockFile(json.dumps({}))
        raise FileNotFoundError(filename)

    mock_open.side_effect = side_effect

    score, result_str = evaluate_objective()
    assert "B1-=400.0Hz" in result_str # Fallback leaves it at default 400.0


@patch('builtins.open')
def test_evaluate_objective_empty_modes_penalty(mock_open):
    # Test that empty eigenmodes or cavity_modes results in MISSING_DATA_PENALTY
    struct_data = {
        "eigenmodes": []
    }

    acoustic_data = {
        "cavity_modes": []
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
        if filename == "violin_body.json":
            return MockFile(json.dumps({}))
        raise FileNotFoundError(filename)

    mock_open.side_effect = side_effect

    score, result_str = evaluate_objective()

    # 2 sources missing data (struct and acoustic have empty modes)
    assert "DataPen=2000.0" in result_str
