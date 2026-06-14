import optuna
import subprocess
import json
import os
import sys

# Ensure the root directory is in sys.path so we can import from slice/common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model
from common.params import suggest, cli_args

def objective(trial):
    # 1. Suggest parameters from the shared search space
    params = suggest(trial)

    print(f"\n--- Starting Trial {trial.number} ---")
    print("Params: " + ", ".join(f"{k}={v}" for k, v in params.items()))

    # 2. Generate CAD (STEP)
    subprocess.run(["python3", "cad/violin.py", *cli_args(params)], check=True)

    # 3. Generate Mesh
    step_file = "violin_body.step"
    mesh_file = "violin_body.msh"
    # the mesher script uses hardcoded input/output when run directly so we will rename if needed or just let it use violin_body.step
    subprocess.run(["python3", "mesh/mesher.py"], check=True)

    # 4. Run Structural Sim
    subprocess.run(["python3", "sim_struct/structural.py", "--mesh", mesh_file], check=True)

    # 5. Run Acoustic Sim
    subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", mesh_file], check=True)

    # 6. Evaluate Objective
    # We want to minimize some penalty. Let's say target A0 cavity mode is 290Hz and we want low mass and volume.

    mass_g = 400.0 # Default if fail
    volume_mm3 = 300000.0 # Default if fail
    a0_freq = 300.0
    top_thickness_val = 4.0 # Default if fail
    back_thickness_val = 4.0 # Default if fail
    bridge_mass_g = 2.0 # Default if fail

    try:
        with open("violin_body.json", "r") as f:
            body_res = json.load(f)
            mass_g = body_res.get("mass_g", mass_g)
            volume_mm3 = body_res.get("volume_mm3", volume_mm3)
            top_thickness_val = body_res.get("top_thickness", top_thickness_val)
            back_thickness_val = body_res.get("back_thickness", back_thickness_val)
            bridge_mass_g = body_res.get("bridge_mass_g", bridge_mass_g)
    except FileNotFoundError:
        print("Warning: violin_body.json not found")

    try:
        with open("structural_results.json", "r") as f:
            struct_res = json.load(f)
            # fallback in case structural_results has updated mass
            mass_g = struct_res.get("mass_g", mass_g)
    except FileNotFoundError:
        print("Warning: structural_results.json not found")

    try:
        with open("acoustic_results.json", "r") as f:
            ac_res = json.load(f)
            # Find first mode
            modes = ac_res.get("cavity_modes", [])
            if modes:
                a0_freq = modes[0].get("frequency_hz", a0_freq)
    except FileNotFoundError:
        print("Warning: acoustic_results.json not found")

    # Simple fitness: squared error of A0 frequency from 290Hz, plus a small penalty for mass and volume
    target_a0 = 290.0

    score = abs(a0_freq - target_a0) + (mass_g * 0.1) + (volume_mm3 * 1e-4) + (top_thickness_val * 5.0) + (back_thickness_val * 5.0) + (bridge_mass_g * 5.0)
    print(f"Result: A0={a0_freq:.1f}Hz, Mass={mass_g:.1f}g, BridgeMass={bridge_mass_g:.2f}g, Volume={volume_mm3:.1f}mm3, Top={top_thickness_val:.1f}mm, Back={back_thickness_val:.1f}mm -> Score={score:.2f}")

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
        print(f"Warning: Slicing final model failed or bambu-studio not installed: {e}")

    # Final Meshing and Simulation
    print("\nRunning final meshing and simulation...")
    mesh_file = "violin_body.msh"
    subprocess.run(["python3", "mesh/mesher.py"], check=True)
    subprocess.run(["python3", "sim_struct/structural.py", "--mesh", mesh_file], check=True)
    subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", mesh_file], check=True)
    print("End-to-End Pipeline Completed Successfully.")
