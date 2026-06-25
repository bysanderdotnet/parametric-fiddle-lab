import argparse
import optuna
import subprocess
import json
import os
import shutil
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

    try:
        # 2. Generate CAD (STEP)
        subprocess.run(["python3", "cad/violin.py", *cli_args(params)], check=True)

        # 3. Slice Model. A design that cannot be sliced is not printable, so a
        # genuine slicing failure (or a silent no-G-code result) must prune the
        # trial — let it propagate to the handler below. Only a missing
        # orca-slicer install is tolerated, so envs without it still optimize.
        gcode_path = "violin_body.gcode"
        if os.path.exists(gcode_path):
            os.remove(gcode_path)  # drop stale gcode so the check below is meaningful

        if shutil.which("orca-slicer") is None:
            print("Warning: orca-slicer not installed; skipping slice for this trial.")
        else:
            extra_args = []
            if "infill_density" in params:
                extra_args.extend(["--sparse-infill-density", f"{params['infill_density']}%"])
            if "layer_height" in params:
                extra_args.extend(["--layer-height", str(params['layer_height'])])

            dummy_profile = {
                "machine": "profiles/machine.json",
                "process": "profiles/process.json",
                "filament": "profiles/filament.json"
            }
            slice_model("violin_body.stl", dummy_profile, gcode_path, extra_args=extra_args)
            if not os.path.exists(gcode_path):
                raise RuntimeError("Slicing produced no G-code; geometry not printable")
            print("Slice generated for trial.")

        # 4. Generate Mesh
        mesh_file = "violin_body.msh"
        cavity_mesh = "violin_cavity.msh"
        # mesher meshes both violin_body.step and violin_cavity.step when run directly
        subprocess.run(["python3", "mesh/mesher.py"], check=True)

        # 5. Run Structural Sim (solid body mesh)
        subprocess.run(["python3", "sim_struct/structural.py", "--mesh", mesh_file], check=True)

        # 6. Run Acoustic Sim (air cavity mesh)
        subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", cavity_mesh], check=True)

        # 7. Evaluate Objective
        score, result_str = evaluate_objective()
        print(result_str)

        return score
    except Exception as e:
        print(f"Trial failed due to an error: {e}")
        raise optuna.TrialPruned()

def main(n_trials=20, n_startup_trials=5, seed=None):
    # TPE explores randomly for the first n_startup_trials, then models the
    # search space. Each trial runs the full CAD -> slice -> mesh -> FEA chain,
    # so trials are expensive; n_trials is the main run-length knob.
    sampler = optuna.samplers.TPESampler(n_startup_trials=n_startup_trials, seed=seed)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=n_trials)

    print("\nOptimization finished.")
    try:
        trial = study.best_trial
        print("Best trial:")
        print(f"  Value: {trial.value}")
        print("  Params: ")
        for key, value in trial.params.items():
            print(f"    {key}: {value}")

        print("\nGenerating final geometry and sliced file for best trial...")
        try:
            # Generate final CAD
            subprocess.run(["python3", "cad/violin.py", *cli_args(trial.params)], check=True)

            # Slice Model
            try:
                extra_args = []
                if "infill_density" in trial.params:
                    extra_args.extend(["--sparse-infill-density", f"{trial.params['infill_density']}%"])
                if "layer_height" in trial.params:
                    extra_args.extend(["--layer-height", str(trial.params['layer_height'])])

                dummy_profile = {
                    "machine": "profiles/machine.json",
                    "process": "profiles/process.json",
                    "filament": "profiles/filament.json"
                }
                slice_model("violin_body.stl", dummy_profile, "violin_body.gcode", extra_args=extra_args)
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
        except Exception as e:
            print(f"Final trial failed due to an error: {e}")
    except ValueError:
        print("No trials completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize violin parameters via Optuna.")
    parser.add_argument("--trials", type=int, default=20,
                        help="Number of optimization trials; each runs full CAD+slice+mesh+FEA (default 20).")
    parser.add_argument("--startup-trials", type=int, default=5,
                        help="Random-sampled trials before the TPE model engages (default 5).")
    parser.add_argument("--seed", type=int, default=None,
                        help="Sampler seed for reproducible runs (default: random).")
    args = parser.parse_args()
    main(n_trials=args.trials, n_startup_trials=args.startup_trials, seed=args.seed)
