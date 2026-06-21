import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_tailpiece_width_bottom import sweep_tailpiece_width_bottom

@patch("subprocess.run")
def test_sweep_tailpiece_width_bottom(mock_run):
    mock_json_data = json.dumps({"tailpiece_mass_g": 6.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_tailpiece_width_bottom()

    assert len(results) == 5
    assert results[0] == (15.0, 6.0)
    assert results[1] == (20.0, 6.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--tailpiece_width_bottom", "15.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_bottom", "20.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_bottom", "25.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_bottom", "30.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--tailpiece_width_bottom", "35.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
