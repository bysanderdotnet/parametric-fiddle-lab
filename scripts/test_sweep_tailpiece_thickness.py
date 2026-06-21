import subprocess
import pytest
from unittest.mock import patch, mock_open

# Import the module to test
import sweep_tailpiece_thickness

@patch("subprocess.run")
def test_sweep_tailpiece_thickness(mock_run):
    # Mock subprocess.run to just return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Mock the JSON file reading
    mock_json_content = '{"tailpiece_mass_g": 20.46}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_tailpiece_thickness.sweep_tailpiece_thickness()

    # Check that subprocess.run was called the expected number of times (6 thicknesses)
    assert mock_run.call_count == 6

    # Check the returned results
    assert len(results) == 6
    for thickness, mass in results:
        assert mass == 20.46
        assert thickness in [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
