import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_fingerboard_end_shape

@patch("subprocess.run")
def test_sweep_fingerboard_end_shape(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"top_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_fingerboard_end_shape.sweep_fingerboard_end_shape()

    assert mock_run.call_count == 2
    assert len(results) == 2

    for val, mass in results:
        assert mass == 2.5
        assert val in ['flat', 'curve']
