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
    f_hole_width = trial.suggest_float("f_hole_width", 5.0, 12.0)
    f_hole_profile = trial.suggest_categorical("f_hole_profile", ["slot", "classic"])
    f_hole_top_radius = trial.suggest_float("f_hole_top_radius", 3.0, 6.0)
    f_hole_bottom_radius = trial.suggest_float("f_hole_bottom_radius", 3.0, 6.0)
    f_hole_y_offset = trial.suggest_float("f_hole_y_offset", -20.0, 20.0)
    f_hole_angle = trial.suggest_float("f_hole_angle", 75.0, 105.0)
    neck_length = trial.suggest_float("neck_length", 110.0, 150.0)
    neck_width = trial.suggest_float("neck_width", 25.0, 40.0)
    neck_height = trial.suggest_float("neck_height", 15.0, 30.0)
    bridge_width = trial.suggest_float("bridge_width", 30.0, 50.0)
    bridge_height = trial.suggest_float("bridge_height", 20.0, 40.0)
    bridge_thickness = trial.suggest_float("bridge_thickness", 3.0, 8.0)
    bridge_radius = trial.suggest_float("bridge_radius", 15.0, 40.0)
    bridge_inner_curve_radius = trial.suggest_float("bridge_inner_curve_radius", 5.0, 15.0)
    bridge_side_cutout_radius = trial.suggest_float("bridge_side_cutout_radius", 3.0, 10.0)
    bridge_cutout_radius = trial.suggest_float("bridge_cutout_radius", 2.0, 8.0)
    bridge_cutout_y_offset = trial.suggest_float("bridge_cutout_y_offset", 5.0, 20.0)
    bridge_foot_length = trial.suggest_float("bridge_foot_length", 5.0, 15.0)
    bridge_foot_height = trial.suggest_float("bridge_foot_height", 2.0, 10.0)
    soundpost_radius = trial.suggest_float("soundpost_radius", 2.0, 5.0)
    soundpost_x_offset = trial.suggest_float("soundpost_x_offset", 5.0, 25.0)
    soundpost_y_offset = trial.suggest_float("soundpost_y_offset", -25.0, -5.0)
    bass_bar_length = trial.suggest_float("bass_bar_length", 150.0, 250.0)
    bass_bar_width = trial.suggest_float("bass_bar_width", 3.0, 8.0)
    bass_bar_height = trial.suggest_float("bass_bar_height", 5.0, 15.0)
    bass_bar_x_offset = trial.suggest_float("bass_bar_x_offset", -25.0, -5.0)
    bass_bar_y_offset = trial.suggest_float("bass_bar_y_offset", -20.0, 20.0)
    tailpiece_length = trial.suggest_float("tailpiece_length", 100.0, 120.0)
    tailpiece_width_top = trial.suggest_float("tailpiece_width_top", 30.0, 45.0)
    tailpiece_width_bottom = trial.suggest_float("tailpiece_width_bottom", 15.0, 25.0)
    tailpiece_thickness = trial.suggest_float("tailpiece_thickness", 3.0, 8.0)
    purfling_groove_depth = trial.suggest_float("purfling_groove_depth", 0.5, 2.0)
    fingerboard_length = trial.suggest_float("fingerboard_length", 250.0, 290.0)
    fingerboard_width_top = trial.suggest_float("fingerboard_width_top", 22.0, 26.0)
    fingerboard_width_bottom = trial.suggest_float("fingerboard_width_bottom", 40.0, 44.0)
    fingerboard_thickness = trial.suggest_float("fingerboard_thickness", 4.0, 7.0)
    fingerboard_radius = trial.suggest_float("fingerboard_radius", 30.0, 60.0)
    pegbox_length = trial.suggest_float("pegbox_length", 65.0, 75.0)
    pegbox_width = trial.suggest_float("pegbox_width", 22.0, 26.0)
    pegbox_depth = trial.suggest_float("pegbox_depth", 18.0, 22.0)
    pegbox_thickness = trial.suggest_float("pegbox_thickness", 4.0, 6.0)
    peg_hole_radius = trial.suggest_float("peg_hole_radius", 2.5, 3.5)
    peg_spacing = trial.suggest_float("peg_spacing", 14.0, 16.0)
    peg_length = trial.suggest_float("peg_length", 35.0, 55.0)
    endpin_length = trial.suggest_float("endpin_length", 15.0, 25.0)
    endpin_radius = trial.suggest_float("endpin_radius", 3.0, 6.0)
    nut_length = trial.suggest_float("nut_length", 3.0, 8.0)
    nut_width = trial.suggest_float("nut_width", 22.0, 26.0)
    nut_height = trial.suggest_float("nut_height", 5.0, 10.0)
    saddle_length = trial.suggest_float("saddle_length", 3.0, 8.0)
    saddle_width = trial.suggest_float("saddle_width", 25.0, 35.0)
    saddle_height = trial.suggest_float("saddle_height", 4.0, 8.0)
    scroll_radius = trial.suggest_float("scroll_radius", 8.0, 12.0)
    scroll_width = trial.suggest_float("scroll_width", 18.0, 22.0)
    chinrest_x_offset = trial.suggest_float("chinrest_x_offset", -60.0, -20.0)
    chinrest_y_offset = trial.suggest_float("chinrest_y_offset", -160.0, -120.0)
    chinrest_width = trial.suggest_float("chinrest_width", 60.0, 100.0)
    chinrest_length = trial.suggest_float("chinrest_length", 40.0, 70.0)
    chinrest_height = trial.suggest_float("chinrest_height", 10.0, 25.0)
    chinrest_cutout_radius = trial.suggest_float("chinrest_cutout_radius", 40.0, 80.0)
    chinrest_cutout_depth = trial.suggest_float("chinrest_cutout_depth", 2.0, 10.0)
    c_bout_cutout_radius = trial.suggest_float("c_bout_cutout_radius", 30.0, 60.0)

    print(f"\n--- Starting Trial {trial.number} ---")
    print(f"Params: length={length:.1f}, lower={lower_bout:.1f}, upper={upper_bout:.1f}, c={c_bout:.1f}, t_top={top_thickness:.1f}, t_back={back_thickness:.1f}, t_rib={rib_thickness:.1f}, arch_t={top_arch_height:.1f}, arch_b={back_arch_height:.1f}, h_rib={rib_height:.1f}, f_len={f_hole_length:.1f}, f_spc={f_hole_spacing:.1f}, f_wid={f_hole_width:.1f}, f_y_off={f_hole_y_offset:.1f}, f_ang={f_hole_angle:.1f}")
    print(f"        neck_l={neck_length:.1f}, neck_w={neck_width:.1f}, neck_h={neck_height:.1f}")
    print(f"        br_w={bridge_width:.1f}, br_h={bridge_height:.1f}, br_t={bridge_thickness:.1f}, br_r={bridge_radius:.1f}, br_inner_r={bridge_inner_curve_radius:.1f}, br_side_cut={bridge_side_cutout_radius:.1f}")
    print(f"        sp_r={soundpost_radius:.1f}, sp_x={soundpost_x_offset:.1f}, sp_y={soundpost_y_offset:.1f}")
    print(f"        bb_l={bass_bar_length:.1f}, bb_w={bass_bar_width:.1f}, bb_h={bass_bar_height:.1f}, bb_x={bass_bar_x_offset:.1f}, bb_y={bass_bar_y_offset:.1f}")
    print(f"        tp_l={tailpiece_length:.1f}, tp_wt={tailpiece_width_top:.1f}, tp_wb={tailpiece_width_bottom:.1f}, tp_th={tailpiece_thickness:.1f}")
    print(f"        purfling_d={purfling_groove_depth:.1f}")
    print(f"        fb_l={fingerboard_length:.1f}, fb_wt={fingerboard_width_top:.1f}, fb_wb={fingerboard_width_bottom:.1f}, fb_th={fingerboard_thickness:.1f}, fb_r={fingerboard_radius:.1f}")
    print(f"        nut_l={nut_length:.1f}, nut_w={nut_width:.1f}, nut_h={nut_height:.1f}")
    print(f"        saddle_l={saddle_length:.1f}, saddle_w={saddle_width:.1f}, saddle_h={saddle_height:.1f}")
    print(f"        scroll_r={scroll_radius:.1f}, scroll_w={scroll_width:.1f}")
    print(f"        chinrest_x={chinrest_x_offset:.1f}, chinrest_y={chinrest_y_offset:.1f}, chinrest_w={chinrest_width:.1f}, chinrest_l={chinrest_length:.1f}, chinrest_h={chinrest_height:.1f}")
    print(f"        c_bout_cutout_r={c_bout_cutout_radius:.1f}")

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
        "--f_hole_width", str(f_hole_width),
        "--f_hole_profile", str(f_hole_profile),
        "--f_hole_top_radius", str(f_hole_top_radius),
        "--f_hole_bottom_radius", str(f_hole_bottom_radius),
        "--f_hole_y_offset", str(f_hole_y_offset),
        "--f_hole_angle", str(f_hole_angle),
        "--neck_length", str(neck_length),
        "--neck_width", str(neck_width),
        "--neck_height", str(neck_height),
        "--bridge_width", str(bridge_width),
        "--bridge_height", str(bridge_height),
        "--bridge_thickness", str(bridge_thickness),
        "--bridge_radius", str(bridge_radius),
        "--bridge_inner_curve_radius", str(bridge_inner_curve_radius),
        "--bridge_side_cutout_radius", str(bridge_side_cutout_radius),
        "--bridge_cutout_radius", str(bridge_cutout_radius),
        "--bridge_cutout_y_offset", str(bridge_cutout_y_offset),
        "--bridge_foot_length", str(bridge_foot_length),
        "--bridge_foot_height", str(bridge_foot_height),
        "--soundpost_radius", str(soundpost_radius),
        "--soundpost_x_offset", str(soundpost_x_offset),
        "--soundpost_y_offset", str(soundpost_y_offset),
        "--bass_bar_length", str(bass_bar_length),
        "--bass_bar_width", str(bass_bar_width),
        "--bass_bar_height", str(bass_bar_height),
        "--bass_bar_x_offset", str(bass_bar_x_offset),
        "--bass_bar_y_offset", str(bass_bar_y_offset),
        "--tailpiece_length", str(tailpiece_length),
        "--tailpiece_width_top", str(tailpiece_width_top),
        "--tailpiece_width_bottom", str(tailpiece_width_bottom),
        "--tailpiece_thickness", str(tailpiece_thickness),
        "--purfling_groove_depth", str(purfling_groove_depth),
        "--fingerboard_length", str(fingerboard_length),
        "--fingerboard_width_top", str(fingerboard_width_top),
        "--fingerboard_width_bottom", str(fingerboard_width_bottom),
        "--fingerboard_thickness", str(fingerboard_thickness),
        "--fingerboard_radius", str(fingerboard_radius),
        "--pegbox_length", str(pegbox_length),
        "--pegbox_width", str(pegbox_width),
        "--pegbox_depth", str(pegbox_depth),
        "--pegbox_thickness", str(pegbox_thickness),
        "--peg_hole_radius", str(peg_hole_radius),
        "--peg_spacing", str(peg_spacing),
        "--peg_length", str(peg_length),
        "--endpin_length", str(endpin_length),
        "--endpin_radius", str(endpin_radius),
        "--nut_length", str(nut_length),
        "--nut_width", str(nut_width),
        "--nut_height", str(nut_height),
        "--saddle_length", str(saddle_length),
        "--saddle_width", str(saddle_width),
        "--saddle_height", str(saddle_height),
        "--scroll_radius", str(scroll_radius),
        "--scroll_width", str(scroll_width),
        "--chinrest_x_offset", str(chinrest_x_offset),
        "--chinrest_y_offset", str(chinrest_y_offset),
        "--chinrest_width", str(chinrest_width),
        "--chinrest_length", str(chinrest_length),
        "--chinrest_height", str(chinrest_height),
        "--chinrest_cutout_radius", str(chinrest_cutout_radius),
        "--chinrest_cutout_depth", str(chinrest_cutout_depth),
        "--c_bout_cutout_radius", str(c_bout_cutout_radius)
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
    # We want to minimize some penalty. Let's say target A0 cavity mode is 290Hz and we want low mass and volume.

    mass_g = 400.0 # Default if fail
    volume_mm3 = 300000.0 # Default if fail
    a0_freq = 300.0
    top_thickness_val = 4.0 # Default if fail
    back_thickness_val = 4.0 # Default if fail

    try:
        with open("violin_body.json", "r") as f:
            body_res = json.load(f)
            mass_g = body_res.get("mass_g", mass_g)
            volume_mm3 = body_res.get("volume_mm3", volume_mm3)
            top_thickness_val = body_res.get("top_thickness", top_thickness_val)
            back_thickness_val = body_res.get("back_thickness", back_thickness_val)
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

    score = abs(a0_freq - target_a0) + (mass_g * 0.1) + (volume_mm3 * 1e-4) + (top_thickness_val * 5.0) + (back_thickness_val * 5.0)
    print(f"Result: A0={a0_freq:.1f}Hz, Mass={mass_g:.1f}g, Volume={volume_mm3:.1f}mm3, Top={top_thickness_val:.1f}mm, Back={back_thickness_val:.1f}mm -> Score={score:.2f}")

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
        "--f_hole_width", str(trial.params["f_hole_width"]),
        "--f_hole_profile", str(trial.params["f_hole_profile"]),
        "--f_hole_top_radius", str(trial.params["f_hole_top_radius"]),
        "--f_hole_bottom_radius", str(trial.params["f_hole_bottom_radius"]),
        "--f_hole_y_offset", str(trial.params["f_hole_y_offset"]),
        "--f_hole_angle", str(trial.params["f_hole_angle"]),
        "--neck_length", str(trial.params["neck_length"]),
        "--neck_width", str(trial.params["neck_width"]),
        "--neck_height", str(trial.params["neck_height"]),
        "--bridge_width", str(trial.params["bridge_width"]),
        "--bridge_height", str(trial.params["bridge_height"]),
        "--bridge_thickness", str(trial.params["bridge_thickness"]),
        "--bridge_radius", str(trial.params["bridge_radius"]),
        "--bridge_inner_curve_radius", str(trial.params["bridge_inner_curve_radius"]),
        "--bridge_side_cutout_radius", str(trial.params["bridge_side_cutout_radius"]),
        "--bridge_cutout_radius", str(trial.params["bridge_cutout_radius"]),
        "--bridge_cutout_y_offset", str(trial.params["bridge_cutout_y_offset"]),
        "--bridge_foot_length", str(trial.params["bridge_foot_length"]),
        "--bridge_foot_height", str(trial.params["bridge_foot_height"]),
        "--soundpost_radius", str(trial.params["soundpost_radius"]),
        "--soundpost_x_offset", str(trial.params["soundpost_x_offset"]),
        "--soundpost_y_offset", str(trial.params["soundpost_y_offset"]),
        "--bass_bar_length", str(trial.params["bass_bar_length"]),
        "--bass_bar_width", str(trial.params["bass_bar_width"]),
        "--bass_bar_height", str(trial.params["bass_bar_height"]),
        "--bass_bar_x_offset", str(trial.params["bass_bar_x_offset"]),
        "--bass_bar_y_offset", str(trial.params["bass_bar_y_offset"]),
        "--tailpiece_length", str(trial.params["tailpiece_length"]),
        "--tailpiece_width_top", str(trial.params["tailpiece_width_top"]),
        "--tailpiece_width_bottom", str(trial.params["tailpiece_width_bottom"]),
        "--tailpiece_thickness", str(trial.params["tailpiece_thickness"]),
        "--purfling_groove_depth", str(trial.params["purfling_groove_depth"]),
        "--fingerboard_length", str(trial.params["fingerboard_length"]),
        "--fingerboard_width_top", str(trial.params["fingerboard_width_top"]),
        "--fingerboard_width_bottom", str(trial.params["fingerboard_width_bottom"]),
        "--fingerboard_thickness", str(trial.params["fingerboard_thickness"]),
        "--fingerboard_radius", str(trial.params["fingerboard_radius"]),
        "--pegbox_length", str(trial.params["pegbox_length"]),
        "--pegbox_width", str(trial.params["pegbox_width"]),
        "--pegbox_depth", str(trial.params["pegbox_depth"]),
        "--pegbox_thickness", str(trial.params["pegbox_thickness"]),
        "--peg_hole_radius", str(trial.params["peg_hole_radius"]),
        "--peg_spacing", str(trial.params["peg_spacing"]),
        "--peg_length", str(trial.params["peg_length"]),
        "--endpin_length", str(trial.params["endpin_length"]),
        "--endpin_radius", str(trial.params["endpin_radius"]),
        "--nut_length", str(trial.params["nut_length"]),
        "--nut_width", str(trial.params["nut_width"]),
        "--nut_height", str(trial.params["nut_height"]),
        "--saddle_length", str(trial.params["saddle_length"]),
        "--saddle_width", str(trial.params["saddle_width"]),
        "--saddle_height", str(trial.params["saddle_height"]),
        "--scroll_radius", str(trial.params["scroll_radius"]),
        "--scroll_width", str(trial.params["scroll_width"]),
        "--chinrest_x_offset", str(trial.params["chinrest_x_offset"]),
        "--chinrest_y_offset", str(trial.params["chinrest_y_offset"]),
        "--chinrest_width", str(trial.params["chinrest_width"]),
        "--chinrest_length", str(trial.params["chinrest_length"]),
        "--chinrest_height", str(trial.params["chinrest_height"]),
        "--chinrest_cutout_radius", str(trial.params["chinrest_cutout_radius"]),
        "--chinrest_cutout_depth", str(trial.params["chinrest_cutout_depth"]),
        "--c_bout_cutout_radius", str(trial.params["c_bout_cutout_radius"])
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
