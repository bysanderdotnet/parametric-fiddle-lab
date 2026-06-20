import os
import json
import pytest
from unittest.mock import patch
from sim_acoustic.acoustic import run_acoustic_sim

def test_run_acoustic_sim_dummy(tmpdir):
    # Change directory to tmpdir so output file is written there
    orig_dir = os.getcwd()
    os.chdir(tmpdir)

    try:
        # Pass a non-existent mesh file to force fallback to dummy results
        results = run_acoustic_sim("non_existent_mesh.msh")

        # Verify dummy results structure
        assert "cavity_modes" in results
        assert "radiation_efficiency" in results

        assert len(results["cavity_modes"]) == 2

        # Verify the output file was created
        assert os.path.exists("acoustic_results.json")

        with open("acoustic_results.json", "r") as f:
            data = json.load(f)
            assert len(data["cavity_modes"]) == 2

    finally:
        os.chdir(orig_dir)

def test_acoustic_cli(tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        script_path = os.path.abspath(os.path.join(orig_dir, "sim_acoustic", "acoustic.py"))
        import subprocess
        import sys

        env = os.environ.copy()
        env["PYTHONPATH"] = orig_dir

        result = subprocess.run([sys.executable, script_path, "--mesh", "non_existent_mesh.msh"], capture_output=True, text=True, env=env)
        assert result.returncode == 0
        assert os.path.exists("acoustic_results.json")
    finally:
        os.chdir(orig_dir)

@patch("sim_acoustic.acoustic.cavity_eigenmodes")
@patch("sim_acoustic.acoustic.os.path.exists")
def test_run_acoustic_sim_exception(mock_exists, mock_cavity_eigenmodes, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        mock_exists.return_value = True
        mock_cavity_eigenmodes.side_effect = Exception("Sim failed")

        results = run_acoustic_sim("dummy_mesh.msh")

        assert "cavity_modes" in results
        assert len(results["cavity_modes"]) == 2
    finally:
        os.chdir(orig_dir)

@patch("sim_acoustic.acoustic.cavity_eigenmodes")
@patch("sim_acoustic.acoustic.os.path.exists")
def test_run_acoustic_sim_fem(mock_exists, mock_cavity_eigenmodes, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)

    try:
        mock_exists.return_value = True

        mock_cavity_eigenmodes.return_value = [
            {"mode": 1, "frequency_hz": 300.0},
            {"mode": 2, "frequency_hz": 400.0},
            {"mode": 3, "frequency_hz": 600.0}
        ]

        results = run_acoustic_sim("dummy_mesh.msh")

        assert "cavity_modes" in results
        assert len(results["cavity_modes"]) == 3

        assert results["cavity_modes"][0]["description"] == "A0-like (Helmholtz)"
        assert results["cavity_modes"][1]["description"] == "A1-like"
        assert results["cavity_modes"][2]["description"] == "Higher cavity mode"

        assert os.path.exists("acoustic_results.json")

    finally:
        os.chdir(orig_dir)
