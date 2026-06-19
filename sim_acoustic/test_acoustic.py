import os
import json
import pytest
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
