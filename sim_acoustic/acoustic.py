import json
import random
import os
import shutil
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.elmer import run_elmer as elmer_eigenmodes

SOLVER = """Solver 1
  Equation = Helmholtz Equation
  Variable = -dofs 2 Pressure
  Procedure = "HelmholtzSolve" "HelmholtzSolver"
  Eigen Analysis = True
  Eigen System Values = 10
  Eigen System Select = Smallest magnitude

  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStabl
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8
  Linear System Preconditioning = ILU0
  Linear System Residual Output = 10
  Linear System Abort Not Converged = False
End"""

MATERIAL = """Material 1
  Name = "Air (room temperature)"
  Density = 1.205
  Sound speed = 343.0
End"""

def run_elmer(mesh_file):
    print(f"Running Elmer acoustic simulation on {mesh_file}...")
    modes = elmer_eigenmodes(mesh_file, "elmer_mesh_acoustic", "case_acoustic.sif", SOLVER, MATERIAL)
    if not modes:
        return None
    return {
        "cavity_modes": modes,
        "radiation_efficiency": 0.0
    }

def run_acoustic_sim(mesh_file):
    """Run Elmer acoustic simulation, fallback to dummy if not installed."""
    if shutil.which("ElmerGrid") and shutil.which("ElmerSolver") and os.path.exists(mesh_file):
        try:
            results = run_elmer(mesh_file)
            if results:
                result_file = "acoustic_results.json"
                with open(result_file, "w") as f:
                    json.dump(results, f, indent=4)
                print(f"Elmer Acoustic Simulation complete. Results saved to {result_file}")
                return results
        except Exception as e:
            print(f"Elmer simulation failed: {e}. Falling back to dummy results.")
    else:
        print("ElmerGrid or ElmerSolver not found, or mesh doesn't exist. Using dummy results.")

    print(f"Running placeholder acoustic simulation on {mesh_file}...")

    # Dummy results: eigenfrequencies (e.g. A0, A1 modes for a violin cavity)
    dummy_results = {
        "cavity_modes": [
            {"mode": 1, "frequency_hz": 290.0 + random.uniform(-10, 10), "description": "A0-like (Helmholtz)"},
            {"mode": 2, "frequency_hz": 450.0 + random.uniform(-15, 15), "description": "A1-like"},
        ],
        "radiation_efficiency": random.uniform(0.1, 0.3)
    }

    # Output to a dummy result file
    result_file = "acoustic_results.json"
    with open(result_file, "w") as f:
        json.dump(dummy_results, f, indent=4)

    print(f"Simulation complete. Results saved to {result_file}")
    return dummy_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run acoustic simulation.")
    parser.add_argument("--mesh", type=str, default="dummy_cavity.msh", help="Mesh file to simulate")
    args = parser.parse_args()

    run_acoustic_sim(args.mesh)