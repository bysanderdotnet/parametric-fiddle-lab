import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_length import sweep_length

@patch("subprocess.run")
def test_sweep_length(mock_run):
    mock_json_data = json.dumps({"mass_g": 350.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_length()

    assert len(results) == 5
    assert results[0] == (300.0, 350.0)
    assert results[1] == (325.0, 350.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--length", "300.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--length", "325.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--length", "350.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--length", "375.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--length", "400.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
