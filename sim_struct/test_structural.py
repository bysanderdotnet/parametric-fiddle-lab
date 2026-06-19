import os
import json
import pytest
from sim_struct.structural import run_structural_sim

def test_run_structural_sim_dummy(tmpdir):
    # Change directory to tmpdir so output file is written there
    orig_dir = os.getcwd()
    os.chdir(tmpdir)

    try:
        # Pass a non-existent mesh file to force fallback to dummy results
        results = run_structural_sim("non_existent_mesh.msh")

        # Verify dummy results structure
        assert "eigenmodes" in results
        assert "max_stress_mpa" in results
        assert "mass_g" in results

        assert len(results["eigenmodes"]) == 3

        # Verify the output file was created
        assert os.path.exists("structural_results.json")

        with open("structural_results.json", "r") as f:
            data = json.load(f)
            assert data["max_stress_mpa"] == 15.4

    finally:
        os.chdir(orig_dir)
