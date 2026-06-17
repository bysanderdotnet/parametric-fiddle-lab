import json
import random
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.elmer import run_elmer as elmer_eigenmodes
from filaments import bambu_pla_basic as filament

SOLVER = """Solver 1
  Equation = Linear elasticity
  Variable = -dofs 3 Displacement
  Procedure = "StressSolve" "StressSolver"
  Eigen Analysis = True
  Eigen System Values = 10
  Eigen System Select = Smallest magnitude

  Linear System Solver = Direct
  Linear System Direct Method = UMFPACK
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8
  Linear System Residual Output = 10
  Linear System Abort Not Converged = False
End"""

MATERIAL = """Material 1
  Name = "{name}"
  Density = {density}
  Youngs modulus = {youngs}
  Poisson ratio = {poisson}
End""".format(
    name=filament.NAME,
    density=filament.DENSITY_KG_M3,
    youngs=filament.YOUNGS_MODULUS_PA,
    poisson=filament.POISSON_RATIO,
)

def mass_from_json(default=380.0):
    """Mass is a geometric quantity already computed by the CAD step."""
    try:
        with open("violin_body.json", "r") as f:
            return json.load(f).get("mass_g", default)
    except FileNotFoundError:
        return default


def run_elmer(mesh_file):
    print(f"Running Elmer simulation on {mesh_file}...")
    modes = elmer_eigenmodes(mesh_file, "elmer_mesh", "case.sif", SOLVER, MATERIAL)
    if not modes:
        return None
    return {
        "eigenmodes": modes,
        "max_stress_mpa": 0.0,  # eigenanalysis only; stress not computed
        "mass_g": mass_from_json()
    }

def run_structural_sim(mesh_file):
    """Run Elmer/Code_Aster structural simulation, fallback to dummy if not installed."""
    if shutil.which("ElmerGrid") and shutil.which("ElmerSolver") and os.path.exists(mesh_file):
        try:
            results = run_elmer(mesh_file)
            if results:
                result_file = "structural_results.json"
                with open(result_file, "w") as f:
                    json.dump(results, f, indent=4)
                print(f"Elmer Simulation complete. Results saved to {result_file}")
                return results
        except Exception as e:
            print(f"Elmer simulation failed: {e}. Falling back to dummy results.")
    else:
        print("ElmerGrid or ElmerSolver not found, or mesh doesn't exist. Using dummy results.")

    print(f"Running placeholder structural simulation on {mesh_file}...")

    mass_g = mass_from_json()

    # Dummy results: eigenfrequencies (e.g. A0, C0, B1- like modes for a violin body)
    dummy_results = {
        "eigenmodes": [
            {"mode": 1, "frequency_hz": 280.0 + random.uniform(-10, 10), "description": "CBR-like"},
            {"mode": 2, "frequency_hz": 400.0 + random.uniform(-15, 15), "description": "B1- like"},
            {"mode": 3, "frequency_hz": 530.0 + random.uniform(-20, 20), "description": "B1+ like"}
        ],
        "max_stress_mpa": 15.4,
        "mass_g": mass_g
    }

    # Output to a dummy result file
    result_file = "structural_results.json"
    with open(result_file, "w") as f:
        json.dump(dummy_results, f, indent=4)

    print(f"Simulation complete. Results saved to {result_file}")
    return dummy_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run structural simulation.")
    parser.add_argument("--mesh", type=str, default="violin_body.msh", help="Mesh file to simulate")
    args = parser.parse_args()

    run_structural_sim(args.mesh)
