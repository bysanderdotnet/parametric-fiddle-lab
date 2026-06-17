import optuna
import subprocess
import json
import os
import sys

# Ensure the root directory is in sys.path so we can import from slice/common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model
from common.params import suggest, cli_args
from opt.objective import evaluate_objective

def objective(trial):
    # 1. Suggest parameters from the shared search space
    params = suggest(trial)

    print(f"\n--- Starting Trial {trial.number} ---")
    print("Params: " + ", ".join(f"{k}={v}" for k, v in params.items()))

    # 2. Generate CAD (STEP)
    subprocess.run(["python3", "cad/violin.py", *cli_args(params)], check=True)

    # 3. Generate Mesh
    mesh_file = "violin_body.msh"
    cavity_mesh = "violin_cavity.msh"
    # mesher meshes both violin_body.step and violin_cavity.step when run directly
    subprocess.run(["python3", "mesh/mesher.py"], check=True)

    # 4. Run Structural Sim (solid body mesh)
    subprocess.run(["python3", "sim_struct/structural.py", "--mesh", mesh_file], check=True)

    # 5. Run Acoustic Sim (air cavity mesh)
    subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", cavity_mesh], check=True)

    # 6. Evaluate Objective
    score, result_str = evaluate_objective()
    print(result_str)

    return score

if __name__ == "__main__":
    # Create study and run optimization
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=3)

    print("\nOptimization finished.")
    print("Best trial:")
    trial = study.best_trial
    print(f"  Value: {trial.value}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")

    print("\nGenerating final geometry and sliced file for best trial...")
    # Generate final CAD
    subprocess.run(["python3", "cad/violin.py", *cli_args(trial.params)], check=True)

    # Slice Model
    try:
        slice_model("violin_body.step", "dummy_profile.json", "violin_body.gcode")
        print("Final slice generated.")
    except Exception as e:
        print(f"Warning: Slicing final model failed or orca-slicer not installed: {e}")

    # Final Meshing and Simulation
    print("\nRunning final meshing and simulation...")
    mesh_file = "violin_body.msh"
    cavity_mesh = "violin_cavity.msh"
    subprocess.run(["python3", "mesh/mesher.py"], check=True)
    subprocess.run(["python3", "sim_struct/structural.py", "--mesh", mesh_file], check=True)
    subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", cavity_mesh], check=True)
    print("End-to-End Pipeline Completed Successfully.")
