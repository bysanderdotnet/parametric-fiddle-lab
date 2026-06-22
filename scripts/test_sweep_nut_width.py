import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_nut_width

@patch("subprocess.run")
def test_sweep_nut_width(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"top_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_nut_width.sweep_nut_width()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [22.00, 23.00, 24.00, 25.00, 26.00]
