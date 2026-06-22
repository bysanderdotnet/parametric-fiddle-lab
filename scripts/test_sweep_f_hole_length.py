import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_f_hole_length

@patch("subprocess.run")
def test_sweep_f_hole_length(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"cavity_modes": [{"description": "A0-like (Helmholtz)", "frequency_hz": 295.0}]}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_f_hole_length.sweep_f_hole_length()

    # Check that subprocess.run was called the expected number of times
    assert mock_run.call_count == 12

    # Check the returned results
    assert len(results) == 4
    for val, freq in results:
        assert freq == 295.0
        assert val in [60.0, 70.0, 80.0, 90.0]
