import json
import os
import tempfile
from unittest.mock import patch
from objective import evaluate_objective

@patch('builtins.open', side_effect=FileNotFoundError)
def test_evaluate_objective_default_fallback(mock_open):
    score, result_str = evaluate_objective()

    # All three result files missing -> neutral default frequencies, but the
    # trial is charged the missing-data penalty.
    # targets are now: A0=285, B1-=410, B1+=540
    # freq_error = |300-285| + |400-410| + |500-540| = 15 + 10 + 40 = 65
    # mass_penalty = 0.05 * 400 = 20
    # data_penalty = 1000 * 3 = 3000
    expected_score = 3085.0

    assert abs(score - expected_score) < 1e-6
    assert "A0=300.0Hz" in result_str
    assert "B1-=400.0Hz" in result_str
    assert "Score=3085.00" in result_str

@patch('builtins.open')
def test_evaluate_objective_with_mock_files(mock_open):
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

    # targets: A0=285, B1-=410, B1+=540
    # freq_error = |285-285| + |420-410| + |520-540| = 0 + 10 + 20 = 30
    # mass_penalty = 0.05 * 350 = 17.5
    # data_penalty = 0
    expected_score = 47.5

    assert abs(score - expected_score) < 1e-6
    assert "A0=285.0Hz" in result_str
    assert "A1=460.0Hz" in result_str
    assert "CBR=310.0Hz" in result_str
    assert "B1-=420.0Hz" in result_str
    assert "B1+=520.0Hz" in result_str
    assert "Mass=350.0g" in result_str
    assert "SliceFilament=0.0g" in result_str
    assert "Top=3.0mm" in result_str
    assert "Score=47.50" in result_str


@patch('builtins.open')
def test_evaluate_objective_fallback_modes(mock_open):
    struct_data = {
        "eigenmodes": [
            {"frequency_hz": 90.0, "description": ""},
            {"frequency_hz": 415.0, "description": ""},
            {"frequency_hz": 500.0, "description": ""}
        ]
    }

    acoustic_data = {
        "cavity_modes": [
            {"frequency_hz": 295.0, "description": ""},
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
    assert "B1-=500.0Hz" in result_str


@patch('builtins.open')
def test_evaluate_objective_single_fallback_mode(mock_open):
    struct_data = {
        "eigenmodes": [
            {"frequency_hz": 90.0, "description": ""},
            {"frequency_hz": 415.0, "description": ""}
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
    assert "B1-=415.0Hz" in result_str


@patch('builtins.open')
def test_evaluate_objective_no_fallback_modes(mock_open):
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
    assert "B1-=400.0Hz" in result_str


@patch('builtins.open')
def test_evaluate_objective_empty_modes_penalty(mock_open):
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

    assert "DataPen=2000.0" in result_str


def test_calibrate_and_evaluate_uses_ref_targets():
    from objective import calibrate_and_evaluate
    score, result_str, raw = calibrate_and_evaluate()
    # In the all-defaults-fallback path: A0=300.0, B1-=400.0, B1+=500.0
    # targets: A0=285, B1-=410, B1+=540
    # freq_error = |300-285| + |400-410| + |500-540| = 15+10+35 = 60
    assert raw["freq_error"] == 60.0


def test_evaluate_objective_return_raw():
    score, result_str, raw = evaluate_objective(return_raw=True)
    assert "a0_hz" in raw
    assert "b1_minus_hz" in raw
    assert "b1_plus_hz" in raw
    assert "freq_error" in raw
