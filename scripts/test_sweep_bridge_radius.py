import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_bridge_radius

@patch("subprocess.run")
def test_sweep_bridge_radius(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"bridge_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_bridge_radius.sweep_bridge_radius()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [15.0, 21.25, 27.5, 33.75, 40.0]
