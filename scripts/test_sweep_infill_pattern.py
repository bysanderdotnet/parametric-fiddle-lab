import subprocess
import pytest
from unittest.mock import patch, MagicMock

import sweep_infill_pattern

@patch("sweep_infill_pattern.slice_model")
@patch("subprocess.run")
def test_sweep_infill_pattern(mock_run, mock_slice_model):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_slice_model.return_value = None

    results = sweep_infill_pattern.sweep_infill_pattern()

    assert mock_run.call_count == 1
    assert mock_slice_model.call_count == 4
    assert len(results) == 4

    for val, status in results:
        assert status == "Success"
        assert val in ["grid", "gyroid", "honeycomb", "rectilinear"]

    calls = mock_slice_model.call_args_list
    args_called = [call[1].get('extra_args', []) for call in calls]

    expected_args = [
        ["--sparse-infill-pattern", "grid"],
        ["--sparse-infill-pattern", "gyroid"],
        ["--sparse-infill-pattern", "honeycomb"],
        ["--sparse-infill-pattern", "rectilinear"]
    ]

    assert args_called == expected_args
