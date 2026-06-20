import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_f_hole_size

@patch("subprocess.run")
def test_sweep_f_hole_size(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"cavity_modes": [{"description": "A0-like (Helmholtz)", "frequency_hz": 295.0}]}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_f_hole_size.sweep_f_hole_size()

    # Check that subprocess.run was called the expected number of times (5 widths * 3 commands = 15)
    assert mock_run.call_count == 15

    # Check the returned results
    assert len(results) == 5
    for width, freq in results:
        assert freq == 295.0
        assert width in [6.0, 7.0, 8.0, 9.0, 10.0]
