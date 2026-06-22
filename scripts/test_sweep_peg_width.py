import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_peg_width

@patch("subprocess.run")
def test_sweep_peg_width(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"top_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_peg_width.sweep_peg_width()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [15.00, 17.50, 20.00, 22.50, 25.00]
