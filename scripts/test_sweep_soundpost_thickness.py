import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_soundpost_thickness

@patch("subprocess.run")
def test_sweep_soundpost_thickness(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"soundpost_mass_g": 1.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_soundpost_thickness.sweep_soundpost_thickness()

    # Check that subprocess.run was called the expected number of times (5 thicknesses)
    assert mock_run.call_count == 5

    # Check the returned results
    assert len(results) == 5
    for thickness, mass in results:
        assert mass == 1.5
        assert thickness in [4.0, 5.0, 6.0, 7.0, 8.0]
