import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_soundpost_mass

@patch("subprocess.run")
def test_sweep_soundpost_mass(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"soundpost_mass_g": 3.2}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_soundpost_mass.sweep_soundpost_mass()

    # Check that subprocess.run was called the expected number of times (7 thicknesses)
    assert mock_run.call_count == 7

    # Check the returned results
    assert len(results) == 7
    for thickness, mass in results:
        assert mass == 3.2
        assert thickness in [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
