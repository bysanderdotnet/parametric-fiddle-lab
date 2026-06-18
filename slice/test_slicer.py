import pytest
import os
import zipfile
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

from slicer import slice_model

def test_slice_model_file_not_found():
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        slice_model("nonexistent_file.stl", {}, "out.gcode")

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
        slice_model(str(stl_file), profile, str(output_gcode))

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
        return MagicMock(stdout="Slice success", returncode=0)

    mock_run.side_effect = mock_run_side_effect

    slice_model(str(stl_file), {}, str(output_gcode))

    mock_run.assert_called_once()

    assert output_gcode.exists()
    with open(output_gcode, "r") as f:
        content = f.read()
    assert "G1 X10 Y10 Z10" in content

@patch("subprocess.run")
def test_slice_model_subprocess_error(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["orca-slicer"], stderr="Some slice error")

    with pytest.raises(RuntimeError, match="Orca Slicer CLI error: Some slice error"):
        slice_model(str(stl_file), {}, str(output_gcode))

@patch("subprocess.run")
def test_slice_model_no_executable(mock_run, tmp_path):
    stl_file = tmp_path / "test.stl"
    stl_file.touch()
    output_gcode = tmp_path / "output.gcode"

    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(RuntimeError, match="orca-slicer executable not found"):
        slice_model(str(stl_file), {}, str(output_gcode))
