import os
import json
import pytest
from unittest.mock import patch
from sim_struct.structural import run_structural_sim


def test_structural_boundary_conditions():
    from sim_struct.structural import BOUNDARIES
    assert "Boundary Condition 1" in BOUNDARIES
    assert "Target Boundaries(1) = 1" in BOUNDARIES
    assert "Displacement 1 = 0" in BOUNDARIES
    assert "Displacement 2 = 0" in BOUNDARIES
    assert "Displacement 3 = 0" in BOUNDARIES
    assert BOUNDARIES.count("Boundary Condition") == 1


def test_elmer_path_passes_boundaries():
    import inspect
    from sim_struct.structural import run_elmer as structural_run_elmer
    src = inspect.getsource(structural_run_elmer)
    assert "boundaries=BOUNDARIES" in src


def test_first_eigenfrequency_above_50hz():
    orig_dir = os.getcwd()
    os.chdir("/tmp")
    try:
        with patch("sim_struct.structural.shutil.which") as mock_which:
            with patch("sim_struct.structural.os.path.exists") as mock_exists:
                with patch("sim_struct.structural.elmer_eigenmodes") as mock_elmer:
                    mock_which.return_value = True
                    mock_exists.return_value = True
                    mock_elmer.return_value = [
                        {"mode": 1, "frequency_hz": 85.3},
                        {"mode": 2, "frequency_hz": 120.7},
                        {"mode": 3, "frequency_hz": 385.2},
                        {"mode": 4, "frequency_hz": 510.4},
                    ]
                    with patch("sim_struct.structural.pv.read") as mock_pv:
                        import numpy as np
                        class MockMesh:
                            @property
                            def point_data(self):
                                return {}
                        mock_pv.return_value = MockMesh()
                        results = run_structural_sim("dummy_mesh.msh")
                        assert results is not None
                        freqs = [m["frequency_hz"] for m in results["eigenmodes"]]
                        assert len(freqs) >= 1
                        assert freqs[0] > 50.0
    finally:
        os.chdir(orig_dir)


def test_run_structural_sim_dummy(tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        results = run_structural_sim("non_existent_mesh.msh")
        assert "eigenmodes" in results
        assert "max_stress_mpa" in results
        assert "mass_g" in results
        assert len(results["eigenmodes"]) == 3
        assert os.path.exists("structural_results.json")
        with open("structural_results.json", "r") as f:
            data = json.load(f)
            assert data["max_stress_mpa"] == 1150.0
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
        results = run_structural_sim("dummy_mesh.msh")
        assert "eigenmodes" in results
        assert len(results["eigenmodes"]) == 3
        assert results["max_stress_mpa"] == 1150.0
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
        results = run_structural_sim("dummy_mesh.msh")
        assert "eigenmodes" in results
        assert len(results["eigenmodes"]) == 3
        assert results["max_stress_mpa"] == 1150.0
    finally:
        os.chdir(orig_dir)


def test_structural_cli(tmpdir):
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        script_path = os.path.abspath(os.path.join(orig_dir, "sim_struct", "structural.py"))
        import subprocess
        import sys
        with open("violin_body.json", "w") as f:
            json.dump({"dummy": 1.0}, f)
        env = os.environ.copy()
        env["PYTHONPATH"] = orig_dir
        result = subprocess.run([sys.executable, script_path, "--mesh", "non_existent_mesh.msh"], capture_output=True, text=True, env=env)
        assert result.returncode == 0
        assert os.path.exists("structural_results.json")
        with open("structural_results.json", "r") as f:
            res = json.load(f)
            assert res["mass_g"] == 380.0
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
