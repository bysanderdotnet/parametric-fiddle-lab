import os
import sys
import unittest.mock
import pytest
import optuna

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opt.optimize import objective

@unittest.mock.patch('opt.optimize.shutil.which', return_value='/usr/bin/orca-slicer')
@unittest.mock.patch('opt.optimize.os.path.exists', return_value=True)
@unittest.mock.patch('opt.optimize.os.remove')
@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.cli_args')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.evaluate_objective')
def test_objective_success(mock_evaluate_objective, mock_slice_model, mock_subprocess_run, mock_cli_args, mock_suggest, mock_remove, mock_exists, mock_which):
    mock_suggest.return_value = {"infill_density": 15, "layer_height": 0.2, "infill_pattern": "gyroid", "wall_loops": 3}
    mock_cli_args.return_value = ["--infill-density", "15", "--layer-height", "0.2"]
    mock_evaluate_objective.return_value = (100.0, "Result string")
    mock_slice_model.return_value = ("Success", {"weight": 42.0})

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 1

    score = objective(trial)

    assert score == 100.0

    mock_suggest.assert_called_once_with(trial)
    mock_cli_args.assert_called_once_with({"infill_density": 15, "layer_height": 0.2, "infill_pattern": "gyroid", "wall_loops": 3})

    assert mock_subprocess_run.call_count == 4

    mock_subprocess_run.assert_any_call(["python3", "cad/violin.py", "--infill-density", "15", "--layer-height", "0.2"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "mesh/mesher.py"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "sim_struct/structural.py", "--mesh", "violin_body.msh",
                                          "--infill-density", "15", "--infill-pattern", "gyroid",
                                          "--layer-height", "0.2", "--wall-loops", "3"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "sim_acoustic/acoustic.py", "--mesh", "violin_cavity.msh"], check=True)

    dummy_profile = {
        "machine": "profiles/machine.json",
        "process": "profiles/process.json",
        "filament": "profiles/filament.json"
    }
    mock_slice_model.assert_called_once_with(
        "violin_body.stl",
        "violin_body.gcode",
        dummy_profile,
        extra_args=["--sparse-infill-density", "15%", "--layer-height", "0.2",
                     "--sparse-infill-pattern", "gyroid", "--wall-loops", "3"]
    )

    mock_evaluate_objective.assert_called_once()

@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.subprocess.run')
def test_objective_exception(mock_subprocess_run, mock_suggest):
    mock_suggest.return_value = {"infill_density": 15, "layer_height": 0.2, "infill_pattern": "grid", "wall_loops": 2}
    mock_subprocess_run.side_effect = Exception("Simulated subprocess failure")

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 2

    # Verify that TrialPruned is raised when an exception occurs
    with pytest.raises(optuna.TrialPruned):
        objective(trial)

    # Verify subprocess.run was called at least once before failing
    mock_subprocess_run.assert_called_once()


@unittest.mock.patch('opt.optimize.shutil.which', return_value='/usr/bin/orca-slicer')
@unittest.mock.patch('opt.optimize.os.path.exists', return_value=True)
@unittest.mock.patch('opt.optimize.os.remove')
@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.cli_args')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
def test_objective_slice_failure_prunes(mock_slice_model, mock_subprocess_run, mock_cli_args, mock_suggest, mock_remove, mock_exists, mock_which):
    mock_suggest.return_value = {}
    mock_cli_args.return_value = []
    mock_slice_model.side_effect = RuntimeError("Orca Slicer CLI error: boom")

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 3

    with pytest.raises(optuna.TrialPruned):
        objective(trial)

    mock_slice_model.assert_called_once()


@unittest.mock.patch('opt.optimize.shutil.which', return_value='/usr/bin/orca-slicer')
@unittest.mock.patch('opt.optimize.os.path.exists', return_value=True)
@unittest.mock.patch('opt.optimize.os.remove')
@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.cli_args')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
def test_objective_no_gcode_prunes(mock_slice_model, mock_subprocess_run, mock_cli_args, mock_suggest, mock_remove, mock_exists, mock_which):
    # Orca can exit 0 yet produce no G-code; absent gcode must prune, not pass.
    mock_suggest.return_value = {}
    mock_cli_args.return_value = []
    mock_slice_model.return_value = ("Success", {})

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 4

    # os.path.exists returns True for gcode check after slice_model
    def exists_side_effect(path):
        return path != "violin_body.gcode"
    mock_exists.side_effect = exists_side_effect

    with pytest.raises(optuna.TrialPruned):
        objective(trial)


@unittest.mock.patch('opt.optimize.shutil.which', return_value=None)
@unittest.mock.patch('opt.optimize.os.path.exists', return_value=False)
@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.cli_args')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.evaluate_objective')
def test_objective_missing_slicer_tolerated(mock_evaluate_objective, mock_slice_model, mock_subprocess_run, mock_cli_args, mock_suggest, mock_exists, mock_which):
    mock_suggest.return_value = {}
    mock_cli_args.return_value = []
    mock_evaluate_objective.return_value = (42.0, "ok")

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 5

    assert objective(trial) == 42.0
    mock_slice_model.assert_not_called()






@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_block(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_create_study):
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_trial = unittest.mock.MagicMock()
    mock_trial.value = 50.0
    mock_trial.params = {"infill_density": 20, "layer_height": 0.16, "infill_pattern": "honeycomb", "wall_loops": 4}
    mock_study.best_trial = mock_trial
    mock_create_study.return_value = mock_study
    mock_cli_args.return_value = ["--infill-density", "20", "--layer-height", "0.16"]
    mock_slice_model.return_value = ("Success", {})

    main()

    mock_create_study.assert_called_once_with(direction="minimize", sampler=unittest.mock.ANY)
    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=20)

    mock_cli_args.assert_called_once_with(mock_trial.params)

    assert mock_subprocess_run.call_count == 4
    mock_subprocess_run.assert_any_call(["python3", "cad/violin.py", "--infill-density", "20", "--layer-height", "0.16"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "mesh/mesher.py"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "sim_struct/structural.py", "--mesh", "violin_body.msh",
                                          "--infill-density", "20", "--infill-pattern", "honeycomb",
                                          "--layer-height", "0.16", "--wall-loops", "4"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "sim_acoustic/acoustic.py", "--mesh", "violin_cavity.msh"], check=True)

    dummy_profile = {
        "machine": "profiles/machine.json",
        "process": "profiles/process.json",
        "filament": "profiles/filament.json"
    }
    mock_slice_model.assert_called_once_with(
        "violin_body.stl",
        "violin_body.gcode",
        dummy_profile,
        extra_args=["--sparse-infill-density", "20%", "--layer-height", "0.16",
                     "--sparse-infill-pattern", "honeycomb", "--wall-loops", "4"]
    )


@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_trials_configurable(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_create_study):
    # n_trials must propagate to study.optimize so runs aren't a fixed smoke test.
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_study.best_trial.params = {}
    mock_create_study.return_value = mock_study
    mock_cli_args.return_value = []

    main(n_trials=7, n_startup_trials=2, seed=42)

    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=7)
