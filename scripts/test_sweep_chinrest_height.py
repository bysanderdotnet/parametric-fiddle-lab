import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_chinrest_height

@patch("subprocess.run")
def test_sweep_chinrest_height(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"top_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_chinrest_height.sweep_chinrest_height()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [10.00, 13.75, 17.50, 21.25, 25.00]
