import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_tailpiece_width_top import sweep_tailpiece_width_top

@patch("subprocess.run")
def test_sweep_tailpiece_width_top(mock_run):
    mock_json_data = json.dumps({"tailpiece_mass_g": 8.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_tailpiece_width_top()

    assert len(results) == 5
    assert results[0] == (35.0, 8.0)
    assert results[1] == (40.0, 8.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--tailpiece_width_top", "35.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_top", "40.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_top", "45.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_top", "50.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_top", "55.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
