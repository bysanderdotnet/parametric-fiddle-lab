import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_lower_bout import sweep_lower_bout

@patch("subprocess.run")
def test_sweep_lower_bout(mock_run):
    mock_json_data = json.dumps({"mass_g": 350.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_lower_bout()

    assert len(results) == 5
    assert results[0] == (180.0, 350.0)
    assert results[1] == (192.5, 350.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--lower_bout", "180.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--lower_bout", "192.5"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--lower_bout", "205.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--lower_bout", "217.5"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--lower_bout", "230.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
