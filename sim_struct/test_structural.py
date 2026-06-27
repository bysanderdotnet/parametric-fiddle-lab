import os
import json
import pytest
from unittest.mock import patch
from sim_struct.structural import run_structural_sim


def test_run_structural_sim_missing_mesh(tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        with pytest.raises(FileNotFoundError, match="Mesh file not found"):
            run_structural_sim("non_existent_mesh.msh")
    finally:
        os.chdir(orig_dir)


@patch("sim_struct.structural.shutil.which")
def test_run_structural_sim_no_elmergrid(mock_which, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        def side_effect(name):
            if name == "ElmerGrid":
                return None
            if name == "ElmerSolver":
                return "/usr/bin/ElmerSolver"
            return None
        mock_which.side_effect = side_effect

        with open("dummy_mesh.msh", "w") as f:
            f.write("")

        with pytest.raises(RuntimeError, match="ElmerGrid not found"):
            run_structural_sim("dummy_mesh.msh")
    finally:
        os.chdir(orig_dir)


@patch("sim_struct.structural.shutil.which")
def test_run_structural_sim_no_elmersolver(mock_which, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        def side_effect(name):
            if name == "ElmerGrid":
                return "/usr/bin/ElmerGrid"
            if name == "ElmerSolver":
                return None
            return None
        mock_which.side_effect = side_effect

        with open("dummy_mesh.msh", "w") as f:
            f.write("")

        with pytest.raises(RuntimeError, match="ElmerSolver not found"):
            run_structural_sim("dummy_mesh.msh")
    finally:
        os.chdir(orig_dir)


@patch("sim_struct.structural.run_elmer")
@patch("sim_struct.structural.shutil.which")
@patch("sim_struct.structural.os.path.exists")
def test_run_structural_sim_elmer_exception(mock_exists, mock_which, mock_run_elmer, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        mock_exists.return_value = True
        mock_which.return_value = True

        mock_run_elmer.side_effect = Exception("Sim failed")

        with pytest.raises(RuntimeError, match="Elmer simulation failed"):
            run_structural_sim("dummy_mesh.msh")
    finally:
        os.chdir(orig_dir)


@patch("sim_struct.structural.elmer_eigenmodes")
@patch("sim_struct.structural.shutil.which")
@patch("sim_struct.structural.os.path.exists")
def test_run_structural_sim_elmer_none(mock_exists, mock_which, mock_elmer_eigenmodes, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        mock_exists.return_value = True
        mock_which.return_value = True

        mock_elmer_eigenmodes.return_value = []

        with pytest.raises(RuntimeError, match="returned no results"):
            run_structural_sim("dummy_mesh.msh")
    finally:
        os.chdir(orig_dir)


@patch("sim_struct.structural.shutil.which")
def test_structural_cli(mock_which, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        script_path = os.path.abspath(os.path.join(orig_dir, "sim_struct", "structural.py"))
        import subprocess
        import sys

        import json
        with open("violin_body.json", "w") as f:
            json.dump({"dummy": 1.0}, f)

        env = os.environ.copy()
        env["PYTHONPATH"] = orig_dir

        result = subprocess.run(
            [sys.executable, script_path, "--mesh", "non_existent_mesh.msh"],
            capture_output=True, text=True, env=env
        )

        # CLI should fail hard when mesh is missing
        assert result.returncode != 0
    finally:
        os.chdir(orig_dir)


@patch("sim_struct.structural.pv.read")
@patch("sim_struct.structural.elmer_eigenmodes")
@patch("sim_struct.structural.shutil.which")
@patch("sim_struct.structural.os.path.exists")
def test_run_structural_sim_elmer(mock_exists, mock_which, mock_elmer_eigenmodes, mock_pv_read, tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)

    try:
        def side_effect_exists(path):
            if path == "dummy_mesh.msh": return True
            if path == os.path.join("elmer_mesh", "case_t0001.vtu"): return True
            if path == "structural_results.json": return True
            return False
        mock_exists.side_effect = side_effect_exists

        mock_which.return_value = True

        mock_elmer_eigenmodes.return_value = [
            {"mode": 1, "frequency_hz": 300.0},
            {"mode": 2, "frequency_hz": 400.0},
            {"mode": 3, "frequency_hz": 500.0}
        ]

        class MockMesh:
            @property
            def point_data(self):
                import numpy as np
                return {
                    "vonmises EigenMode1": np.array([1000000.0, 2500000.0]),
                    "displacement EigenMode1": np.array([[0.001, 0.0, 0.0], [0.002, 0.0, 0.0]]),
                    "vonmises EigenMode2": np.array([1000000.0, 3000000.0]),
                    "displacement EigenMode2": np.array([[0.001, 0.0, 0.0], [0.002, 0.0, 0.0]]),
                    "vonmises EigenMode3": np.array([1000000.0, 2500000.0]),
                    "displacement EigenMode3": np.array([[0.001, 0.0, 0.0], [0.002, 0.0, 0.0]]),
                }

        mock_pv_read.return_value = MockMesh()

        results = run_structural_sim("dummy_mesh.msh")

        assert "eigenmodes" in results
        assert len(results["eigenmodes"]) == 3

        assert results["eigenmodes"][0]["description"] == "CBR-like"
        assert results["eigenmodes"][1]["description"] == "B1- like"
        assert results["eigenmodes"][2]["description"] == "B1+ like"

        assert results["max_stress_mpa"] == 1.5
        assert os.path.exists("structural_results.json")

    finally:
        os.chdir(orig_dir)
