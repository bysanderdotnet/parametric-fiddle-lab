import subprocess
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_bass_bar_height

@patch("subprocess.run")
def test_sweep_bass_bar_height(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"bass_bar_mass_g": 12.4}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_bass_bar_height.sweep_bass_bar_height()

    # Check that subprocess.run was called the expected number of times (5 heights)
    assert mock_run.call_count == 5

    # Check the returned results
    assert len(results) == 5
    for height, mass in results:
        assert mass == 12.4
        assert height in [5.0, 7.5, 10.0, 12.5, 15.0]
