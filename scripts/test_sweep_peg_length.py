import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_peg_length

@patch("subprocess.run")
def test_sweep_peg_length(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"top_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_peg_length.sweep_peg_length()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [35.00, 40.00, 45.00, 50.00, 55.00]
