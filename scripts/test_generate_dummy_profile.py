import os
import shutil
import pytest
from generate_dummy_profile import generate_dummy_profiles

def test_generate_dummy_profiles(tmp_path):
    output_dir = tmp_path / "profiles"
    generate_dummy_profiles(output_dir=str(output_dir))

    assert os.path.exists(output_dir / "machine.json")
    assert os.path.exists(output_dir / "process.json")
    assert os.path.exists(output_dir / "filament.json")
