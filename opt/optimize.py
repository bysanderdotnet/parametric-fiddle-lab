import optuna
import subprocess
import json
import os
import sys

# Ensure the root directory is in sys.path so we can import from slice
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model

def objective(trial):
    # 1. Suggest parameters
    length = trial.suggest_float("length", 340.0, 370.0)
    lower_bout = trial.suggest_float("lower_bout", 200.0, 220.0)
    upper_bout = trial.suggest_float("upper_bout", 160.0, 180.0)
    c_bout = trial.suggest_float("c_bout", 100.0, 120.0)
    top_thickness = trial.suggest_float("top_thickness", 2.0, 6.0)
    back_thickness = trial.suggest_float("back_thickness", 2.0, 6.0)
    rib_thickness = trial.suggest_float("rib_thickness", 2.0, 6.0)
    top_arch_height = trial.suggest_float("top_arch_height", 10.0, 25.0)
    back_arch_height = trial.suggest_float("back_arch_height", 10.0, 25.0)
    rib_height = trial.suggest_float("rib_height", 25.0, 40.0)
    f_hole_length = trial.suggest_float("f_hole_length", 60.0, 90.0)
    f_hole_spacing = trial.suggest_float("f_hole_spacing", 60.0, 100.0)
    neck_length = trial.suggest_float("neck_length", 110.0, 150.0)
    neck_width = trial.suggest_float("neck_width", 25.0, 40.0)
    neck_height = trial.suggest_float("neck_height", 15.0, 30.0)
    bridge_width = trial.suggest_float("bridge_width", 30.0, 50.0)
    bridge_height = trial.suggest_float("bridge_height", 20.0, 40.0)
    bridge_thickness = trial.suggest_float("bridge_thickness", 3.0, 8.0)
    soundpost_radius = trial.suggest_float("soundpost_radius", 2.0, 5.0)
    soundpost_x_offset = trial.suggest_float("soundpost_x_offset", 5.0, 25.0)
    soundpost_y_offset = trial.suggest_float("soundpost_y_offset", -25.0, -5.0)
    bass_bar_length = trial.suggest_float("bass_bar_length", 150.0, 250.0)
    bass_bar_width = trial.suggest_float("bass_bar_width", 3.0, 8.0)
    bass_bar_height = trial.suggest_float("bass_bar_height", 5.0, 15.0)
    bass_bar_x_offset = trial.suggest_float("bass_bar_x_offset", -25.0, -5.0)
    bass_bar_y_offset = trial.suggest_float("bass_bar_y_offset", -20.0, 20.0)

    print(f"\n--- Starting Trial {trial.number} ---")
    print(f"Params: length={length:.1f}, lower={lower_bout:.1f}, upper={upper_bout:.1f}, c={c_bout:.1f}, t_top={top_thickness:.1f}, t_back={back_thickness:.1f}, t_rib={rib_thickness:.1f}, arch_t={top_arch_height:.1f}, arch_b={back_arch_height:.1f}, h_rib={rib_height:.1f}, f_len={f_hole_length:.1f}, f_spc={f_hole_spacing:.1f}")
    print(f"        neck_l={neck_length:.1f}, neck_w={neck_width:.1f}, neck_h={neck_height:.1f}")
    print(f"        br_w={bridge_width:.1f}, br_h={bridge_height:.1f}, br_t={bridge_thickness:.1f}")
    print(f"        sp_r={soundpost_radius:.1f}, sp_x={soundpost_x_offset:.1f}, sp_y={soundpost_y_offset:.1f}")
    print(f"        bb_l={bass_bar_length:.1f}, bb_w={bass_bar_width:.1f}, bb_h={bass_bar_height:.1f}, bb_x={bass_bar_x_offset:.1f}, bb_y={bass_bar_y_offset:.1f}")

    # 2. Generate CAD (STEP)
    subprocess.run([
        "python3", "cad/violin.py",
        "--length", str(length),
        "--lower_bout", str(lower_bout),
        "--upper_bout", str(upper_bout),
        "--c_bout", str(c_bout),
        "--top_thickness", str(top_thickness),
        "--back_thickness", str(back_thickness),
        "--rib_thickness", str(rib_thickness),
        "--top_arch_height", str(top_arch_height),
        "--back_arch_height", str(back_arch_height),
        "--rib_height", str(rib_height),
        "--f_hole_length", str(f_hole_length),
        "--f_hole_spacing", str(f_hole_spacing),
        "--neck_length", str(neck_length),
        "--neck_width", str(neck_width),
        "--neck_height", str(neck_height),
        "--bridge_width", str(bridge_width),
        "--bridge_height", str(bridge_height),
        "--bridge_thickness", str(bridge_thickness),
        "--soundpost_radius", str(soundpost_radius),
        "--soundpost_x_offset", str(soundpost_x_offset),
        "--soundpost_y_offset", str(soundpost_y_offset),
        "--bass_bar_length", str(bass_bar_length),
        "--bass_bar_width", str(bass_bar_width),
        "--bass_bar_height", str(bass_bar_height),
        "--bass_bar_x_offset", str(bass_bar_x_offset),
        "--bass_bar_y_offset", str(bass_bar_y_offset)
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

    print("\nGenerating final geometry and sliced file for best trial...")
    # Generate final CAD
    subprocess.run([
        "python3", "cad/violin.py",
        "--length", str(trial.params["length"]),
        "--lower_bout", str(trial.params["lower_bout"]),
        "--upper_bout", str(trial.params["upper_bout"]),
        "--c_bout", str(trial.params["c_bout"]),
        "--top_thickness", str(trial.params["top_thickness"]),
        "--back_thickness", str(trial.params["back_thickness"]),
        "--rib_thickness", str(trial.params["rib_thickness"]),
        "--top_arch_height", str(trial.params["top_arch_height"]),
        "--back_arch_height", str(trial.params["back_arch_height"]),
        "--rib_height", str(trial.params["rib_height"]),
        "--f_hole_length", str(trial.params["f_hole_length"]),
        "--f_hole_spacing", str(trial.params["f_hole_spacing"]),
        "--neck_length", str(trial.params["neck_length"]),
        "--neck_width", str(trial.params["neck_width"]),
        "--neck_height", str(trial.params["neck_height"]),
        "--bridge_width", str(trial.params["bridge_width"]),
        "--bridge_height", str(trial.params["bridge_height"]),
        "--bridge_thickness", str(trial.params["bridge_thickness"]),
        "--soundpost_radius", str(trial.params["soundpost_radius"]),
        "--soundpost_x_offset", str(trial.params["soundpost_x_offset"]),
        "--soundpost_y_offset", str(trial.params["soundpost_y_offset"]),
        "--bass_bar_length", str(trial.params["bass_bar_length"]),
        "--bass_bar_width", str(trial.params["bass_bar_width"]),
        "--bass_bar_height", str(trial.params["bass_bar_height"]),
        "--bass_bar_x_offset", str(trial.params["bass_bar_x_offset"]),
        "--bass_bar_y_offset", str(trial.params["bass_bar_y_offset"])
    ], check=True)

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
