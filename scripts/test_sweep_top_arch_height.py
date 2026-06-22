import pytest
from unittest.mock import patch, mock_open, call
import json
from sweep_top_arch_height import sweep_top_arch_height

@patch("subprocess.run")
def test_sweep_top_arch_height(mock_run):
    mock_json_data = json.dumps({"mass_g": 350.0})

    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        results = sweep_top_arch_height()

    assert len(results) == 5
    assert results[0] == (10.0, 350.0)
    assert results[1] == (13.75, 350.0)

    # Check if subprocess.run was called with correct arguments
    calls = [
        call(["python3", "cad/violin.py", "--top_arch_height", "10.0"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--top_arch_height", "13.75"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--top_arch_height", "17.5"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--top_arch_height", "21.25"], check=True, capture_output=True),
        call(["python3", "cad/violin.py", "--top_arch_height", "25.0"], check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(calls, any_order=False)
