import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_back_thickness

@patch("subprocess.run")
def test_sweep_back_thickness(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"cavity_modes": [{"description": "A0-like (Helmholtz)", "frequency_hz": 295.0}, {"description": "A1-like", "frequency_hz": 460.0}]}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_back_thickness.sweep_back_thickness()

    # Check that subprocess.run was called the expected number of times (5 thicknesses * 3 commands = 15)
    assert mock_run.call_count == 15

    # Check the returned results
    assert len(results) == 5
    for thickness, freq in results:
        assert freq == 295.0
        assert thickness in [2.0, 3.0, 4.0, 5.0, 6.0]
