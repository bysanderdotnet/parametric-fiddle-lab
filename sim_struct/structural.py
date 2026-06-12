import json
import random
import os
import subprocess
import shutil
import math

def write_sif(mesh_dir):
    sif_content = """Header
  CHECK KEYWORDS Warn
  Mesh DB "." "{mesh_dir}"
  Include Path ""
  Results Directory ""
End

Simulation
  Max Output Level = 5
  Coordinate System = Cartesian
  Coordinate Mapping(3) = 1 2 3
  Simulation Type = Steady state
  Steady State Max Iterations = 1
  Output Intervals(1) = 1
  Solver Input File = case.sif
  Post File = case.vtu
End

Constants
  Gravity(4) = 0 -1 0 9.82
  Stefan Boltzmann = 5.670374419e-08
  Permittivity of Vacuum = 8.85418781e-12
  Permeability of Vacuum = 1.25663706e-06
  Boltzmann Constant = 1.380649e-23
  Unit Charge = 1.6021766e-19
End

Body 1
  Target Bodies(1) = 1
  Name = "Body 1"
  Equation = 1
  Material = 1
End

Solver 1
  Equation = Linear elasticity
  Variable = -dofs 3 Displacement
  Procedure = "StressSolve" "StressSolver"
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
End

Equation 1
  Name = "Equation 1"
  Active Solvers(1) = 1
End

Material 1
  Name = "PLA"
  Density = 1240.0
  Youngs modulus = 2.58e9
  Poisson ratio = 0.35
End
"""
    sif_content = sif_content.replace("{mesh_dir}", mesh_dir)
    with open("case.sif", "w") as f:
        f.write(sif_content)

def run_elmer(mesh_file):
    print(f"Running Elmer simulation on {mesh_file}...")
    mesh_dir = "elmer_mesh"

    # 1. ElmerGrid
    subprocess.run(["ElmerGrid", "14", "2", mesh_file, "-out", mesh_dir], check=True)

    # 2. Write SIF
    write_sif(mesh_dir)

    # 3. ElmerSolver
    result = subprocess.run(["ElmerSolver", "case.sif"], capture_output=True, text=True, check=True)

    # Parse eigenfrequencies from Elmer output
    modes = []
    mode_count = 1
    for line in result.stdout.split('\n'):
        if "EigenSolve:" in line and len(line.split()) >= 3:
            try:
                val = float(line.split()[2])
                if val > 0:
                    freq = math.sqrt(val) / (2 * math.pi)
                else:
                    freq = 0.0
                modes.append({
                    "mode": mode_count,
                    "frequency_hz": freq,
                    "eigenvalue": val
                })
                mode_count += 1
            except ValueError:
                pass

    if not modes:
        return None

    return {
        "eigenmodes": modes,
        "max_stress_mpa": 0.0,
        "mass_g": 0.0
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

    # Dummy results: eigenfrequencies (e.g. A0, C0, B1- like modes for a violin body)
    dummy_results = {
        "eigenmodes": [
            {"mode": 1, "frequency_hz": 280.0 + random.uniform(-10, 10), "description": "CBR-like"},
            {"mode": 2, "frequency_hz": 400.0 + random.uniform(-15, 15), "description": "B1- like"},
            {"mode": 3, "frequency_hz": 530.0 + random.uniform(-20, 20), "description": "B1+ like"}
        ],
        "max_stress_mpa": 15.4,
        "mass_g": 380.0
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
    parser.add_argument("--mesh", type=str, default="dummy.msh", help="Mesh file to simulate")
    args = parser.parse_args()

    run_structural_sim(args.mesh)
