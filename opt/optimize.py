import optuna
import subprocess
import json
import os

def objective(trial):
    # 1. Suggest parameters
    length = trial.suggest_float("length", 340.0, 370.0)
    lower_bout = trial.suggest_float("lower_bout", 200.0, 220.0)
    upper_bout = trial.suggest_float("upper_bout", 160.0, 180.0)
    c_bout = trial.suggest_float("c_bout", 100.0, 120.0)
    thickness = trial.suggest_float("thickness", 2.0, 6.0)

    print(f"\n--- Starting Trial {trial.number} ---")
    print(f"Params: length={length:.1f}, lower={lower_bout:.1f}, upper={upper_bout:.1f}, c={c_bout:.1f}, t={thickness:.1f}")

    # 2. Generate CAD (STEP)
    subprocess.run([
        "python3", "cad/violin.py",
        "--length", str(length),
        "--lower_bout", str(lower_bout),
        "--upper_bout", str(upper_bout),
        "--c_bout", str(c_bout),
        "--thickness", str(thickness)
    ], check=True)

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
    # We want to minimize some penalty. Let's say target A0 cavity mode is 290Hz and we want low mass.

    mass_g = 400.0 # Default if fail
    a0_freq = 300.0

    try:
        with open("structural_results.json", "r") as f:
            struct_res = json.load(f)
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

    # Simple fitness: squared error of A0 frequency from 290Hz, plus a small penalty for mass
    target_a0 = 290.0
    freq_error = (a0_freq - target_a0) ** 2
    mass_penalty = mass_g * 0.1

    score = freq_error + mass_penalty
    print(f"Result: A0={a0_freq:.1f}Hz, Mass={mass_g:.1f}g -> Score={score:.2f}")

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
