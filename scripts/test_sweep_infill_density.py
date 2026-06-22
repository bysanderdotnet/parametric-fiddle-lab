import subprocess
import pytest
from unittest.mock import patch, MagicMock

import sweep_infill_density

@patch("sweep_infill_density.slice_model")
@patch("subprocess.run")
def test_sweep_infill_density(mock_run, mock_slice_model):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_slice_model.return_value = None

    results = sweep_infill_density.sweep_infill_density()

    assert mock_run.call_count == 1
    assert mock_slice_model.call_count == 5
    assert len(results) == 5

    for val, status in results:
        assert status == "Success"
        assert val in [5.0, 28.75, 52.5, 76.25, 100.0]

    # Verify slice_model was called with the correct extra_args
    calls = mock_slice_model.call_args_list
    args_called = [call[1].get('extra_args', []) for call in calls]

    expected_args = [
        ["--sparse-infill-density", "5.0%"],
        ["--sparse-infill-density", "28.75%"],
        ["--sparse-infill-density", "52.5%"],
        ["--sparse-infill-density", "76.25%"],
        ["--sparse-infill-density", "100.0%"]
    ]

    assert args_called == expected_args
