import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_saddle_width

@patch("subprocess.run")
def test_sweep_saddle_width(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{"top_mass_g": 2.5}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_saddle_width.sweep_saddle_width()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [25.00, 27.50, 30.00, 32.50, 35.00]
