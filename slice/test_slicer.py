import pytest
import os
import zipfile
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

from slicer import slice_model

def test_slice_model_file_not_found():
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        slice_model("nonexistent_file.stl", "out.gcode", {})

@patch("subprocess.run")
def test_slice_model_dict_profile(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()

    machine_file = tmp_path / "machine.json"
    machine_file.touch()
    process_file = tmp_path / "process.json"
    process_file.touch()
    filament_file = tmp_path / "filament.json"
    filament_file.touch()

    output_gcode = tmp_path / "output.gcode"

    profile = {
        'machine': str(machine_file),
        'process': str(process_file),
        'filament': str(filament_file)
    }

    # Mock return value
    mock_run.return_value = MagicMock(stdout="Success", returncode=0)

    # Also mock the zip extraction part so it doesn't try to open output.gcode.3mf
    with patch("zipfile.ZipFile") as mock_zip:
        slice_model(str(stl_file), str(output_gcode), profile)

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]

    assert "orca-slicer" in cmd
    assert "--load-settings" in cmd

    # Check that settings are correctly loaded
    settings_arg_idx = cmd.index("--load-settings") + 1
    settings_val = cmd[settings_arg_idx]
    assert str(machine_file.absolute()) in settings_val
    assert str(process_file.absolute()) in settings_val

    assert "--load-filaments" in cmd
    filament_arg_idx = cmd.index("--load-filaments") + 1
    assert cmd[filament_arg_idx] == str(filament_file.absolute())

@patch("subprocess.run")
def test_slice_model_successful_extraction(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    # Mock subprocess run to actually create a dummy zip file named output.gcode.3mf
    # inside the working directory (which is created inside tmpdir).
    # Since tmpdir is created by tempfile.mkdtemp(), we can't easily intercept it.
    # Instead, we mock subprocess.run and inside the side_effect, we can inspect kwargs['cwd']
    # and create the file there.
    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("plate_1.gcode", "G1 X10 Y10 Z10\nM104 S200\n")
                z.writestr("Metadata/slice_info.config", '{"weight": 10.5, "volume": 12000}')
        return MagicMock(stdout="Slice success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), str(output_gcode), {})

    mock_run.assert_called_once()

    assert output_gcode.exists()
    with open(output_gcode, "r") as f:
        content = f.read()
    assert "G1 X10 Y10 Z10" in content

    slice_info_file = tmp_path / "slice_info.config"
    assert slice_info_file.exists()
    with open(slice_info_file, "r") as f:
        info_content = f.read()
    assert '"weight": 10.5' in info_content

@patch("subprocess.run")
def test_slice_model_subprocess_error(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["orca-slicer"], stderr="Some slice error")

    with pytest.raises(RuntimeError, match="Orca Slicer CLI error: Some slice error"):
        slice_model(str(stl_file), str(output_gcode), {})

@patch("subprocess.run")
def test_slice_model_no_executable(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(RuntimeError, match="orca-slicer executable not found"):
        slice_model(str(stl_file), str(output_gcode), {})

@patch("subprocess.run")
@patch("slicer.logger.info")
def test_slice_model_pipe_progress(mock_logger_info, mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    # We need to simulate subprocess.run writing to the pipe.
    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            pipe_path = os.path.join(cwd, "progress.pipe")
            # Write some JSON to the pipe
            if os.path.exists(pipe_path):
                # The pipe thread might not have opened it for reading yet,
                # but usually it has. We can just open and write.
                # Use non-blocking write if possible or just normal write.
                try:
                    with open(pipe_path, 'w') as f:
                        f.write('{"total_percent": 10.5, "message": "Slicing layer 1"}\n')
                        f.write('{"total_percent": 100.0, "message": "Done"}\n')
                except OSError:
                    pass

            # Create dummy output files so extraction doesn't warn
            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("plate_1.gcode", "G1 X10")
        return MagicMock(stdout="Success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), str(output_gcode), {})

    # Check that logger.info was called with the progress messages
    # mock_logger_info is called for other things too, so we search the calls.
    calls = [call[0][0] for call in mock_logger_info.call_args_list]

    assert any("Orca progress: 10.5% - Slicing layer 1" in msg for msg in calls)
    assert any("Orca progress: 100.0% - Done" in msg for msg in calls)

@patch("subprocess.run")
@patch("slicer.logger.info")
def test_slice_model_pipe_progress_invalid_json(mock_logger_info, mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            pipe_path = os.path.join(cwd, "progress.pipe")
            if os.path.exists(pipe_path):
                try:
                    with open(pipe_path, 'w') as f:
                        f.write('{"total_percent": 10.5, "message": "Slicing layer 1"}\n')
                        f.write('invalid json data\n')
                        f.write('{"total_percent": 100.0, "message": "Done"}\n')
                except OSError:
                    pass
            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("plate_1.gcode", "G1 X10")
        return MagicMock(stdout="Success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), str(output_gcode), {})

    calls = [call[0][0] for call in mock_logger_info.call_args_list]

    assert any("Orca progress: 10.5% - Slicing layer 1" in msg for msg in calls)
    assert any("Orca progress: 100.0% - Done" in msg for msg in calls)

@patch("subprocess.run")
@patch("slicer.logger.warning")
def test_slice_model_string_profile(mock_logger_warning, mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("plate_1.gcode", "G1 X10")
        return MagicMock(stdout="Success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), str(output_gcode), "dummy_profile")

    calls = [call[0][0] for call in mock_logger_warning.call_args_list]
    assert any("Profile (dummy_profile) is a string" in msg for msg in calls)

@patch("subprocess.run")
@patch("slicer.logger.warning")
def test_slice_model_no_gcode_in_3mf(mock_logger_warning, mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("Metadata/slice_info.config", "{}")
        return MagicMock(stdout="Success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), str(output_gcode), {})

    calls = [call[0][0] for call in mock_logger_warning.call_args_list]
    assert any("No .gcode file found" in msg for msg in calls)

@patch("subprocess.run")
def test_slice_model_default_profile(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    mock_run.return_value = MagicMock(stdout="Success", returncode=0)

    with patch("zipfile.ZipFile") as mock_zip:
        slice_model(str(stl_file), str(output_gcode), None)

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]

    assert "orca-slicer" in cmd
    assert "--load-settings" in cmd
    settings_arg_idx = cmd.index("--load-settings") + 1
    settings_val = cmd[settings_arg_idx]
    assert "machine.json" in settings_val
    assert "process.json" in settings_val

    assert "--load-filaments" in cmd
    filament_arg_idx = cmd.index("--load-filaments") + 1
    assert "filament.json" in cmd[filament_arg_idx]

@patch("subprocess.run")
@patch("slicer.logger.info")
def test_slice_model_debug_mode(mock_logger_info, mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("plate_1.gcode", "G1 X10")
        return MagicMock(stdout="Success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), str(output_gcode), {}, debug=True)

    calls = [call[0][0] for call in mock_logger_info.call_args_list]
    assert any("Debug mode enabled. Temporary directory left at:" in msg for msg in calls)

@patch("subprocess.run")
@patch("slicer.logger.info")
def test_slice_model_pipe_progress_oserror(mock_logger_info, mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    def mock_run_side_effect(*args, **kwargs):
        cwd = kwargs.get('cwd')
        if cwd:
            pipe_path = os.path.join(cwd, "progress.pipe")
            # Force OSError on writing pipe
            import builtins
            original_open = builtins.open

            def mock_open(path, *oargs, **okwargs):
                if path == pipe_path and 'w' in oargs:
                    raise OSError("Mocked OSError")
                return original_open(path, *oargs, **okwargs)

            with patch('builtins.open', mock_open):
                if os.path.exists(pipe_path):
                    try:
                        with builtins.open(pipe_path, 'w') as f:
                            f.write('{"total_percent": 10.5, "message": "Slicing layer 1"}\n')
                    except OSError:
                        pass

            out_3mf = os.path.join(cwd, "output.gcode.3mf")
            with zipfile.ZipFile(out_3mf, 'w') as z:
                z.writestr("plate_1.gcode", "G1 X10")
        return MagicMock(stdout="Success", returncode=0)

    mock_run.side_effect = mock_run_side_effect
    slice_model(str(stl_file), str(output_gcode), {})
