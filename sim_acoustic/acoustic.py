import json
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.cavity_fem import cavity_eigenmodes
from common.params import FREQ_A0_MAX, FREQ_A1_MAX

SOUND_SPEED = 343.0  # m/s, air at room temperature


def run_acoustic_sim(mesh_file):
    """Solve rigid-wall air-cavity modes via P1 FEM.

    Raises
    ------
    FileNotFoundError
        If the cavity mesh file does not exist.
    RuntimeError
        If the cavity-mode FEM solver fails or returns no modes.
    """
    if not os.path.exists(mesh_file):
        raise FileNotFoundError(f"Cavity mesh file not found: {mesh_file}")

    print(f"Running cavity-mode FEM on {mesh_file}...")
    try:
        modes = cavity_eigenmodes(mesh_file, sound_speed=SOUND_SPEED)
    except Exception as e:
        raise RuntimeError(f"Cavity-mode FEM failed: {e}") from e

    if not modes:
        raise RuntimeError("Cavity-mode FEM returned no modes.")

    for mode in modes:
        freq = mode.get("frequency_hz", 0.0)
        if freq < FREQ_A0_MAX:
            mode["description"] = "A0-like (Helmholtz)"
        elif FREQ_A0_MAX <= freq <= FREQ_A1_MAX:
            mode["description"] = "A1-like"
        else:
            mode["description"] = "Higher cavity mode"

    results = {"cavity_modes": modes, "radiation_efficiency": None}
    with open("acoustic_results.json", "w") as f:
        json.dump(results, f, indent=4)
    freqs = [round(m["frequency_hz"], 1) for m in modes]
    print(f"Acoustic FEM complete. Cavity modes (Hz): {freqs}")
    print("Results saved to acoustic_results.json")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run acoustic simulation.")
    parser.add_argument("--mesh", type=str, default="violin_cavity.msh", help="Cavity mesh file to simulate")
    args = parser.parse_args()

    run_acoustic_sim(args.mesh)
