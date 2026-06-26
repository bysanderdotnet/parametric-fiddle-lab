import argparse
import optuna
import subprocess
import json
import os
import shutil
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model
from common.params import suggest, cli_args
from opt.objective import evaluate_objective


# --- Persistence ---

def _study_storage_path():
    return os.environ.get(
        "OPTUNA_STORAGE",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "optuna_study.db")),
    )


def _load_or_create_study(study_name, seed=None, n_startup_trials=5, storage_url=None):
    sampler = optuna.samplers.TPESampler(n_startup_trials=n_startup_trials, seed=seed)
    if storage_url is None:
        storage_url = _study_storage_path()
    if storage_url.startswith("sqlite://") or storage_url.startswith("postgresql://") or storage_url.startswith("mysql://"):
        storage = optuna.storages.RDBStorage(url=storage_url)
    elif storage_url.startswith("journal:"):
        file_path = storage_url[len("journal:"):]
        storage = optuna.storages.JournalStorage(
            optuna.storages.journal.JournalFileBackend(file_path)
        )
    else:
        storage = optuna.storages.JournalStorage(
            optuna.storages.journal.JournalFileBackend(storage_url)
        )
    study = optuna.create_study(
        study_name=study_name,
        direction="minimize",
        sampler=sampler,
        storage=storage,
        load_if_exists=True,
    )
    return study


# --- Early Stopping ---

class EarlyStoppingCallback:
    def __init__(self, patience_ratio=0.15, min_trials=10, n_trials=20):
        self.patience_ratio = patience_ratio
        self.min_trials = min_trials
        self.n_trials = n_trials
        self._best_value = float("inf")
        self._best_trial = 0

    def __call__(self, study, trial):
        if trial.value is None:
            return
        if trial.value < self._best_value:
            self._best_value = trial.value
            self._best_trial = trial.number
        elapsed_since_improvement = trial.number - self._best_trial
        patience = max(self.min_trials, int(self.n_trials * self.patience_ratio))
        if elapsed_since_improvement >= patience:
            print(
                f"Early stopping: no improvement in {elapsed_since_improvement} trials "
                f"(best={self._best_value:.2f} @ trial {self._best_trial}). "
                f"Patience={patience}."
            )
            study.stop()


# --- Convergence Diagnostics ---

def print_convergence_diagnostics(study):
    print("\n=== Convergence Diagnostics ===")

    try:
        df = study.trials_dataframe()
        completed = df[df["state"] == "COMPLETE"]
        print(f"  Trials: {len(completed)} complete / {len(df)} total")
        if not completed.empty:
            print(f"  Best value: {completed['value'].min():.4f}")
            print(f"  Worst value: {completed['value'].max():.4f}")
            print(f"  Mean value: {completed['value'].mean():.4f}")
            print(f"  Std value:  {completed['value'].std():.4f}")
    except Exception as e:
        print(f"  Could not compute trial stats: {e}")

    try:
        importances = optuna.importance.get_param_importances(study)
        print("\n  Parameter Importances (FANOVA):")
        for param, imp in sorted(importances.items(), key=lambda x: -x[1]):
            print(f"    {param}: {imp:.4f}")
    except Exception as e:
        print(f"  Could not compute param importances: {e}")

    try:
        if len(study.trials) < 2:
            print("\n  Pareto front: too few trials")
        else:
            completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE and t.values is not None]
            if len(completed) >= 2:
                n_objectives = len(completed[0].values)
                if n_objectives > 1:
                    trials_2d = [t for t in completed if len(t.values) >= 2]
                    pareto = optuna.pareto_front(trials_2d=trials_2d)
                    print(f"\n  Pareto front: {len(pareto)} non-dominated trials")
                    for t in pareto[:5]:
                        print(f"    Trial {t.number}: values={t.values}")
                    if len(pareto) > 5:
                        print(f"    ... and {len(pareto) - 5} more")
                else:
                    pareto = optuna.pareto_front(study)
                    print(f"\n  Pareto front (single objective): {len(pareto)} non-dominated trials")
            else:
                print("\n  Pareto front: fewer than 2 completed trials")
    except Exception as e:
        print(f"  Could not compute Pareto front: {e}")

    study_path = _study_storage_path()
    if os.path.exists(study_path):
        size_mb = os.path.getsize(study_path) / (1024 * 1024)
        print(f"\n  Study DB size: {size_mb:.2f} MB")
    print()


def write_diagnostics_report(study, report_path="optimization_report.json"):
    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "study_name": str(getattr(study, "study_name", "")),
        "direction": str(getattr(study, "direction", "")),
        "n_trials": len(getattr(study, "trials", [])),
        "best_value": getattr(study, "best_value", None) if getattr(study, "best_trial", None) else None,
        "best_params": getattr(study, "best_params", None) if getattr(study, "best_trial", None) else None,
    }
    try:
        report["param_importances"] = optuna.importance.get_param_importances(study)
    except Exception:
        pass
    try:
        completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE] if hasattr(study, "trials") else []
        report["trial_values"] = {
            str(t.number): {"value": t.value, "params": dict(t.params) if hasattr(t, "params") else {}}
            for t in completed
        }
    except Exception:
        pass
    try:
        pareto = optuna.pareto_front(study)
        report["pareto_front_trials"] = [t.number for t in pareto]
    except Exception:
        pass
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Optimization report written to {report_path}")


# --- Objective ---

def objective(trial):
    params = suggest(trial)

    print(f"\n--- Starting Trial {trial.number} ---")
    print("Params: " + ", ".join(f"{k}={v}" for k, v in params.items()))

    try:
        subprocess.run(["python3", "cad/violin.py", *cli_args(params)], check=True)

        gcode_path = "violin_body.gcode"
        if os.path.exists(gcode_path):
            os.remove(gcode_path)

        if shutil.which("orca-slicer") is None:
            print("Warning: orca-slicer not installed; skipping slice for this trial.")
        else:
            extra_args = []
            if "infill_density" in params:
                extra_args.extend(["--sparse-infill-density", f"{params['infill_density']}%"])
            if "layer_height" in params:
                extra_args.extend(["--layer-height", str(params['layer_height'])])
            if "infill_pattern" in params:
                extra_args.extend(["--sparse-infill-pattern", params['infill_pattern']])
            if "wall_loops" in params:
                extra_args.extend(["--wall-loops", str(params['wall_loops'])])

            dummy_profile = {
                "machine": "profiles/machine.json",
                "process": "profiles/process.json",
                "filament": "profiles/filament.json"
            }
            _, slice_meta = slice_model("violin_body.stl", gcode_path, dummy_profile, extra_args=extra_args)
            if not os.path.exists(gcode_path):
                raise RuntimeError("Slicing produced no G-code; geometry not printable")
            print("Slice generated for trial.")
            if slice_meta:
                with open("slice_metadata.json", "w") as f:
                    json.dump(slice_meta, f)

        mesh_file = "violin_body.msh"
        cavity_mesh = "violin_cavity.msh"
        subprocess.run(["python3", "mesh/mesher.py"], check=True)

        struct_args = ["python3", "sim_struct/structural.py", "--mesh", mesh_file]
        if "infill_density" in params:
            struct_args += ["--infill-density", str(params["infill_density"])]
        if "infill_pattern" in params:
            struct_args += ["--infill-pattern", params["infill_pattern"]]
        if "layer_height" in params:
            struct_args += ["--layer-height", str(params["layer_height"])]
        if "wall_loops" in params:
            struct_args += ["--wall-loops", str(params["wall_loops"])]
        subprocess.run(struct_args, check=True)

        subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", cavity_mesh], check=True)

        score, result_str = evaluate_objective()
        print(result_str)

        return score
    except Exception as e:
        print(f"Trial failed due to an error: {e}")
        raise optuna.TrialPruned()


# --- Main ---

def main(n_trials=20, n_startup_trials=5, seed=None, study_name=None, storage_url=None,
         early_stop=True, diagnostics=True, report_path="optimization_report.json"):
    study = _load_or_create_study(
        study_name=study_name or "violin_optimization",
        seed=seed,
        n_startup_trials=n_startup_trials,
        storage_url=storage_url,
    )

    callbacks = []
    if early_stop:
        callbacks.append(EarlyStoppingCallback(patience_ratio=0.15, min_trials=10, n_trials=n_trials))

    study.optimize(objective, n_trials=n_trials, callbacks=callbacks)

    print("\nOptimization finished.")
    try:
        trial = study.best_trial
        print("Best trial:")
        print(f"  Value: {trial.value}")
        print("  Params: ")
        for key, value in trial.params.items():
            print(f"    {key}: {value}")

        if diagnostics:
            print_convergence_diagnostics(study)
            write_diagnostics_report(study, report_path=report_path)

        print("\nGenerating final geometry and sliced file for best trial...")
        try:
            subprocess.run(["python3", "cad/violin.py", *cli_args(trial.params)], check=True)

            try:
                extra_args = []
                if "infill_density" in trial.params:
                    extra_args.extend(["--sparse-infill-density", f"{trial.params['infill_density']}%"])
                if "layer_height" in trial.params:
                    extra_args.extend(["--layer-height", str(trial.params['layer_height'])])
                if "infill_pattern" in trial.params:
                    extra_args.extend(["--sparse-infill-pattern", trial.params['infill_pattern']])
                if "wall_loops" in trial.params:
                    extra_args.extend(["--wall-loops", str(trial.params['wall_loops'])])

                dummy_profile = {
                    "machine": "profiles/machine.json",
                    "process": "profiles/process.json",
                    "filament": "profiles/filament.json"
                }
                _, slice_meta = slice_model("violin_body.stl", "violin_body.gcode", dummy_profile, extra_args=extra_args)
                if slice_meta:
                    with open("slice_metadata.json", "w") as f:
                        json.dump(slice_meta, f)
                print("Final slice generated.")
            except Exception as e:
                print(f"Warning: Slicing final model failed or orca-slicer not installed: {e}")

            print("\nRunning final meshing and simulation...")
            mesh_file = "violin_body.msh"
            cavity_mesh = "violin_cavity.msh"
            subprocess.run(["python3", "mesh/mesher.py"], check=True)
            struct_args = ["python3", "sim_struct/structural.py", "--mesh", mesh_file]
            for key, flag in [("infill_density", "--infill-density"), ("infill_pattern", "--infill-pattern"), ("layer_height", "--layer-height"), ("wall_loops", "--wall-loops")]:
                if key in trial.params:
                    struct_args += [flag, str(trial.params[key])]
            subprocess.run(struct_args, check=True)
            subprocess.run(["python3", "sim_acoustic/acoustic.py", "--mesh", cavity_mesh], check=True)
            print("End-to-End Pipeline Completed Successfully.")
        except Exception as e:
            print(f"Final trial failed due to an error: {e}")
    except ValueError:
        print("No trials completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize violin parameters via Optuna.")
    parser.add_argument("--trials", type=int, default=20,
                        help="Number of optimization trials (default 20).")
    parser.add_argument("--startup-trials", type=int, default=5,
                        help="Random-sampled trials before the TPE model engages (default 5).")
    parser.add_argument("--seed", type=int, default=None,
                        help="Sampler seed for reproducible runs (default: random).")
    parser.add_argument("--study-name", type=str, default="violin_optimization",
                        help="Study name for storage (default: violin_optimization).")
    parser.add_argument("--storage", type=str, default=None,
                        help="Storage URL. Default: data/optuna_study.db (JournalFile). "
                             "Examples: sqlite:///path/to/db.sqlite3, journal:/path/to/journal.log, "
                             "postgresql://user:pass@host/db")
    parser.add_argument("--no-early-stop", action="store_true",
                        help="Disable early stopping.")
    parser.add_argument("--no-diagnostics", action="store_true",
                        help="Disable convergence diagnostics report.")
    parser.add_argument("--report-path", type=str, default="optimization_report.json",
                        help="Path for the JSON diagnostics report (default: optimization_report.json).")
    args = parser.parse_args()
    main(
        n_trials=args.trials,
        n_startup_trials=args.startup_trials,
        seed=args.seed,
        study_name=args.study_name,
        storage_url=args.storage,
        early_stop=not args.no_early_stop,
        diagnostics=not args.no_diagnostics,
        report_path=args.report_path,
    )
