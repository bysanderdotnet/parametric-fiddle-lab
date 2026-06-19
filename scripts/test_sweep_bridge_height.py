import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_bridge_height

@patch("subprocess.run")
def test_sweep_bridge_height(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"bridge_mass_g": 6.0}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_bridge_height.sweep_bridge_height()

    # Check that subprocess.run was called the expected number of times (5 heights)
    assert mock_run.call_count == 5

    # Check the returned results
    assert len(results) == 5
    for height, mass in results:
        assert mass == 6.0
        assert height in [20.0, 25.0, 30.0, 35.0, 40.0]
