import subprocess
import pytest
from unittest.mock import patch, MagicMock

import sweep_wall_loops

@patch("sweep_wall_loops.slice_model")
@patch("subprocess.run")
def test_sweep_wall_loops(mock_run, mock_slice_model):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_slice_model.return_value = None

    results = sweep_wall_loops.sweep_wall_loops()

    assert mock_run.call_count == 1
    assert mock_slice_model.call_count == 5
    assert len(results) == 5

    for val, status in results:
        assert status == "Success"
        assert val in [1, 2, 3, 4, 5]

    calls = mock_slice_model.call_args_list
    args_called = [call[1].get('extra_args', []) for call in calls]

    expected_args = [
        ["--wall-loops", "1"],
        ["--wall-loops", "2"],
        ["--wall-loops", "3"],
        ["--wall-loops", "4"],
        ["--wall-loops", "5"]
    ]

    assert args_called == expected_args
