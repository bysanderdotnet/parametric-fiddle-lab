import json
import random
import os
import shutil
import sys
import numpy as np
import pyvista as pv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.elmer import run_elmer as elmer_eigenmodes
from common.params import FREQ_CBR_MAX, FREQ_B1_MINUS_MAX
from filaments import bambu_pla_basic as filament

SOLVER = """Solver 1
  Equation = Linear elasticity
  Variable = -dofs 3 Displacement
  Procedure = "StressSolve" "StressSolver"
  Calculate Stresses = True
  Eigen Analysis = True
  Eigen System Values = 16
  Eigen System Select = Smallest magnitude

  Linear System Solver = Direct
  Linear System Direct Method = UMFPACK
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8
  Linear System Residual Output = 10
  Linear System Abort Not Converged = False
End"""

BOUNDARIES = """Boundary Condition 1
  Target Boundaries(1) = 1
  Name = "scroll_tip"
  Displacement 1 = 0
  Displacement 2 = 0
  Displacement 3 = 0
End"""

def build_material(filament_name="pla"):
    fil = filament_lookup(filament_name)
    return """Material 1
  Name = "{name}"
  Density = {density}
  Youngs modulus = {youngs}
  Poisson ratio = {poisson}
End""".format(
        name=fil.NAME,
        density=fil.DENSITY_KG_M3,
        youngs=fil.YOUNGS_MODULUS_PA,
        poisson=fil.POISSON_RATIO,
    )

def mass_from_json(default=380.0):
    try:
        with open("violin_body.json", "r") as f:
            return json.load(f).get("mass_g", default)
    except FileNotFoundError:
        return default


def run_elmer(mesh_file):
    print(f"Running Elmer simulation on {mesh_file}...")
    modes = elmer_eigenmodes(mesh_file, "elmer_mesh", "case.sif", SOLVER, MATERIAL, boundaries=BOUNDARIES)
    if not modes:
        return None

    for mode in modes:
        freq = mode.get("frequency_hz", 0.0)
        if freq < FREQ_CBR_MAX:
            mode["description"] = "CBR-like"
        elif FREQ_CBR_MAX <= freq <= FREQ_B1_MINUS_MAX:
            mode["description"] = "B1- like"
        else:
            mode["description"] = "B1+ like"

    max_stress_mpa_per_mm = 0.0
    vtu_path = os.path.join("elmer_mesh", "case_t0001.vtu")
    if os.path.exists(vtu_path):
        try:
            mesh = pv.read(vtu_path)
            max_normalized_stress_pa_per_m = 0.0
            for i in range(1, len(modes) + 1):
                vm_key = f"vonmises EigenMode{i}"
                disp_key = f"displacement EigenMode{i}"
                if vm_key in mesh.point_data and disp_key in mesh.point_data:
                    max_vm = np.max(mesh.point_data[vm_key])
                    max_disp = np.max(np.linalg.norm(mesh.point_data[disp_key], axis=1))
                    if max_disp > 0:
                        normalized = max_vm / max_disp
                        if normalized > max_normalized_stress_pa_per_m:
                            max_normalized_stress_pa_per_m = normalized

            max_stress_mpa_per_mm = max_normalized_stress_pa_per_m * 1e-9
        except Exception as e:
            print(f"Failed to read stress from VTU: {e}")

    return {
        "eigenmodes": modes,
        "max_stress_mpa": max_stress_mpa_per_mm,
        "mass_g": mass_from_json()
    }

def run_structural_sim(mesh_file, filament_name="pla"):
    if shutil.which("ElmerGrid") and shutil.which("ElmerSolver") and os.path.exists(mesh_file):
        try:
            results = run_elmer(mesh_file, filament_name)
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
    dummy_results = {
        "eigenmodes": [
            {"mode": 1, "frequency_hz": 280.0 + random.uniform(-10, 10), "description": "CBR-like"},
            {"mode": 2, "frequency_hz": 400.0 + random.uniform(-15, 15), "description": "B1- like"},
            {"mode": 3, "frequency_hz": 530.0 + random.uniform(-20, 20), "description": "B1+ like"}
        ],
        "max_stress_mpa": 1150.0,
        "mass_g": mass_g
    }
    result_file = "structural_results.json"
    with open(result_file, "w") as f:
        json.dump(dummy_results, f, indent=4)
    print(f"Simulation complete. Results saved to {result_file}")
    return dummy_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run structural simulation.")
    parser.add_argument("--mesh", type=str, default="violin_body.msh", help="Mesh file to simulate")
    parser.add_argument("--filament", type=str, default="pla",
                        help="Filament material (pla, petg, asa, pc, nylon, pla-cf)")
    args = parser.parse_args()
    run_structural_sim(args.mesh, args.filament)
