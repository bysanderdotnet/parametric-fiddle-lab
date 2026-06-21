import subprocess
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_tailpiece_length

@patch("subprocess.run")
def test_sweep_tailpiece_length(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"tailpiece_mass_g": 20.46}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_tailpiece_length.sweep_tailpiece_length()

    # Check that subprocess.run was called the expected number of times (5 lengths)
    assert mock_run.call_count == 5

    # Check the returned results
    assert len(results) == 5
    for length, mass in results:
        assert mass == 20.46
        assert length in [100.0, 105.0, 110.0, 115.0, 120.0]