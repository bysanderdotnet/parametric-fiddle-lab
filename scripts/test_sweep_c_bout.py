import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_c_bout import sweep_c_bout

@patch("subprocess.run")
def test_sweep_c_bout(mock_run):
    mock_json_data = json.dumps({"mass_g": 350.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_c_bout()

    assert len(results) == 5
    assert results[0] == (90.0, 350.0)
    assert results[1] == (100.0, 350.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--c_bout", "90.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--c_bout", "100.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--c_bout", "110.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--c_bout", "120.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--c_bout", "130.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
