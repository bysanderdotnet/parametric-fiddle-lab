import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_upper_bout import sweep_upper_bout

@patch("subprocess.run")
def test_sweep_upper_bout(mock_run):
    mock_json_data = json.dumps({"mass_g": 350.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_upper_bout()

    assert len(results) == 5
    assert results[0] == (140.0, 350.0)
    assert results[1] == (152.5, 350.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--upper_bout", "140.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--upper_bout", "152.5"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--upper_bout", "165.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--upper_bout", "177.5"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--upper_bout", "190.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
