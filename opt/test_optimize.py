import os
import sys
import unittest.mock
import pytest
import optuna

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opt.optimize import objective

@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.cli_args')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.evaluate_objective')
def test_objective_success(mock_evaluate_objective, mock_slice_model, mock_subprocess_run, mock_cli_args, mock_suggest):
    # Setup mocks
    mock_suggest.return_value = {"infill_density": 15, "layer_height": 0.2}
    mock_cli_args.return_value = ["--infill-density", "15", "--layer-height", "0.2"]
    mock_evaluate_objective.return_value = (100.0, "Result string")

    # Create a dummy trial
    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 1

    # Call the objective function
    score = objective(trial)

    # Assertions
    assert score == 100.0

    mock_suggest.assert_called_once_with(trial)
    mock_cli_args.assert_called_once_with({"infill_density": 15, "layer_height": 0.2})

    # Verify subprocess.run calls
    assert mock_subprocess_run.call_count == 4

    # 1. CAD
    mock_subprocess_run.assert_any_call(["python3", "cad/violin.py", "--infill-density", "15", "--layer-height", "0.2"], check=True)
    # 2. Mesher
    mock_subprocess_run.assert_any_call(["python3", "mesh/mesher.py"], check=True)
    # 3. Struct Sim
    mock_subprocess_run.assert_any_call(["python3", "sim_struct/structural.py", "--mesh", "violin_body.msh"], check=True)
    # 4. Acoustic Sim
    mock_subprocess_run.assert_any_call(["python3", "sim_acoustic/acoustic.py", "--mesh", "violin_cavity.msh"], check=True)

    # Verify slice_model call
    dummy_profile = {
        "machine": "profiles/machine.json",
        "process": "profiles/process.json",
        "filament": "profiles/filament.json"
    }
    mock_slice_model.assert_called_once_with(
        "violin_body.stl",
        dummy_profile,
        "violin_body.gcode",
        extra_args=["--sparse-infill-density", "15%", "--layer-height", "0.2"]
    )

    mock_evaluate_objective.assert_called_once()

@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.subprocess.run')
def test_objective_exception(mock_subprocess_run, mock_suggest):
    # Setup mock to raise an exception
    mock_suggest.return_value = {"infill_density": 15, "layer_height": 0.2}
    mock_subprocess_run.side_effect = Exception("Simulated subprocess failure")

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 2

    # Verify that TrialPruned is raised when an exception occurs
    with pytest.raises(optuna.TrialPruned):
        objective(trial)

    # Verify subprocess.run was called at least once before failing
    mock_subprocess_run.assert_called_once()






@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_block(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_create_study):
    from opt.optimize import main

    # Setup mocks
    mock_study = unittest.mock.MagicMock()
    mock_trial = unittest.mock.MagicMock()
    mock_trial.value = 50.0
    mock_trial.params = {"infill_density": 20, "layer_height": 0.16}
    mock_study.best_trial = mock_trial
    mock_create_study.return_value = mock_study
    mock_cli_args.return_value = ["--infill-density", "20", "--layer-height", "0.16"]

    # Call main function
    main()

    # Assert study was created (with a sampler) and optimize was called with
    # the default trial count.
    mock_create_study.assert_called_once_with(direction="minimize", sampler=unittest.mock.ANY)
    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=20)

    # Assert final pipeline was run with best_trial.params
    mock_cli_args.assert_called_once_with(mock_trial.params)

    # subprocess.run should be called for CAD, Mesh, Struct Sim, Acoustic Sim
    assert mock_subprocess_run.call_count == 4
    mock_subprocess_run.assert_any_call(["python3", "cad/violin.py", "--infill-density", "20", "--layer-height", "0.16"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "mesh/mesher.py"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "sim_struct/structural.py", "--mesh", "violin_body.msh"], check=True)
    mock_subprocess_run.assert_any_call(["python3", "sim_acoustic/acoustic.py", "--mesh", "violin_cavity.msh"], check=True)

    dummy_profile = {
        "machine": "profiles/machine.json",
        "process": "profiles/process.json",
        "filament": "profiles/filament.json"
    }
    mock_slice_model.assert_called_once_with(
        "violin_body.stl",
        dummy_profile,
        "violin_body.gcode",
        extra_args=["--sparse-infill-density", "20%", "--layer-height", "0.16"]
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
