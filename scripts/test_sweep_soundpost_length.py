import subprocess
import os
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_soundpost_length

@patch("subprocess.run")
def test_sweep_soundpost_length(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"soundpost_mass_g": 6.0}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_soundpost_length.sweep_soundpost_length()

    # Check that subprocess.run was called the expected number of times (5 lengths)
    assert mock_run.call_count == 5

    # Check the returned results
    assert len(results) == 5
    for length, mass in results:
        assert mass == 6.0
        assert length in [45.0, 47.5, 50.0, 52.5, 55.0]
