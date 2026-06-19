import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_bridge_mass

@patch("subprocess.run")
def test_sweep_bridge_mass(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"bridge_mass_g": 5.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_bridge_mass.sweep_bridge_mass()

    # Check that subprocess.run was called the expected number of times (6 thicknesses)
    assert mock_run.call_count == 6

    # Check the returned results
    assert len(results) == 6
    for thickness, mass in results:
        assert mass == 5.5
        assert thickness in [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
