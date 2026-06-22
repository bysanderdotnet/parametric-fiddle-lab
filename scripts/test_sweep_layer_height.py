import subprocess
import pytest
from unittest.mock import patch, MagicMock

import sweep_layer_height

@patch("sweep_layer_height.slice_model")
@patch("subprocess.run")
def test_sweep_layer_height(mock_run, mock_slice_model):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_slice_model.return_value = None

    results = sweep_layer_height.sweep_layer_height()

    assert mock_run.call_count == 1
    assert mock_slice_model.call_count == 5
    assert len(results) == 5

    for val, status in results:
        assert status == "Success"
        assert val in [0.08, 0.13, 0.18, 0.23, 0.28]

    # Verify slice_model was called with the correct extra_args
    calls = mock_slice_model.call_args_list
    args_called = [call[1].get('extra_args', []) for call in calls]

    expected_args = [
        ["--layer-height", "0.08"],
        ["--layer-height", "0.13"],
        ["--layer-height", "0.18"],
        ["--layer-height", "0.23"],
        ["--layer-height", "0.28"]
    ]

    assert args_called == expected_args
