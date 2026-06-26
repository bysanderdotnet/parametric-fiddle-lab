import os
import sys
import unittest.mock
import json
import datetime
import pytest
import optuna

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opt.optimize import objective, EarlyStoppingCallback, _load_or_create_study


# --- objective() tests ---

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
    mock_evaluate_objective.assert_called_once()


@unittest.mock.patch('opt.optimize.suggest')
@unittest.mock.patch('opt.optimize.subprocess.run')
def test_objective_exception(mock_subprocess_run, mock_suggest):
    mock_suggest.return_value = {"infill_density": 15, "layer_height": 0.2, "infill_pattern": "grid", "wall_loops": 2}
    mock_subprocess_run.side_effect = Exception("Simulated subprocess failure")

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 2

    with pytest.raises(optuna.TrialPruned):
        objective(trial)

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
    mock_suggest.return_value = {}
    mock_cli_args.return_value = []
    mock_slice_model.return_value = ("Success", {})

    trial = unittest.mock.MagicMock(spec=optuna.Trial)
    trial.number = 4

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


# --- main() tests ---

@unittest.mock.patch('opt.optimize._load_or_create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_block(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_load_study):
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_trial = unittest.mock.MagicMock()
    mock_trial.value = 50.0
    mock_trial.params = {"infill_density": 20, "layer_height": 0.16, "infill_pattern": "honeycomb", "wall_loops": 4}
    mock_study.best_trial = mock_trial
    mock_study.study_name = "test"
    mock_study.direction = "minimize"
    mock_study.best_value = 50.0
    mock_study.best_params = {"infill_density": 20}
    mock_study.trials = []
    mock_load_study.return_value = mock_study
    mock_cli_args.return_value = ["--infill-density", "20", "--layer-height", "0.16"]
    mock_slice_model.return_value = ("Success", {})

    main(diagnostics=False)

    mock_load_study.assert_called_once_with(
        study_name="violin_optimization",
        seed=None,
        n_startup_trials=5,
        storage_url=None,
    )
    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=20, callbacks=unittest.mock.ANY)

    mock_cli_args.assert_called_once_with(mock_trial.params)
    assert mock_subprocess_run.call_count == 4


@unittest.mock.patch('opt.optimize._load_or_create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_trials_configurable(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_load_study):
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_study.best_trial.params = {}
    mock_study.study_name = "test"
    mock_study.direction = "minimize"
    mock_study.trials = []
    mock_load_study.return_value = mock_study
    mock_cli_args.return_value = []

    main(n_trials=7, n_startup_trials=2, seed=42, diagnostics=False)

    mock_load_study.assert_called_once_with(
        study_name="violin_optimization",
        seed=42,
        n_startup_trials=2,
        storage_url=None,
    )
    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=7, callbacks=unittest.mock.ANY)


@unittest.mock.patch('opt.optimize._load_or_create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_storage_and_study_name(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_load_study):
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_study.best_trial.params = {}
    mock_study.study_name = "my_custom_study"
    mock_study.direction = "minimize"
    mock_study.trials = []
    mock_load_study.return_value = mock_study
    mock_cli_args.return_value = []

    main(
        study_name="my_custom_study",
        storage_url="sqlite:///tmp/test_optuna.db",
        early_stop=False,
        diagnostics=False,
    )

    mock_load_study.assert_called_once_with(
        study_name="my_custom_study",
        seed=None,
        n_startup_trials=5,
        storage_url="sqlite:///tmp/test_optuna.db",
    )
    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=20, callbacks=[])


# --- _load_or_create_study tests ---

@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.optuna.samplers.TPESampler')
@unittest.mock.patch('opt.optimize.optuna.storages.RDBStorage')
def test_load_or_create_study_rdb(mock_rdb_storage, mock_tpe_sampler, mock_create_study):
    mock_rdb_storage.return_value = "rdb_storage_obj"
    mock_tpe_sampler.return_value = "sampler_obj"
    mock_create_study.return_value = "study_obj"

    result = _load_or_create_study(
        study_name="test_study",
        seed=42,
        n_startup_trials=7,
        storage_url="sqlite:///tmp/test.db",
    )

    assert result == "study_obj"
    mock_rdb_storage.assert_called_once_with(url="sqlite:///tmp/test.db")
    mock_create_study.assert_called_once_with(
        study_name="test_study",
        direction="minimize",
        sampler="sampler_obj",
        storage="rdb_storage_obj",
        load_if_exists=True,
    )


@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.optuna.samplers.TPESampler')
@unittest.mock.patch('opt.optimize.optuna.storages.JournalStorage')
def test_load_or_create_study_journal(mock_journal_storage, mock_tpe_sampler, mock_create_study):
    mock_journal_storage.return_value = "journal_storage_obj"
    mock_tpe_sampler.return_value = "sampler_obj"
    mock_create_study.return_value = "study_obj"

    result = _load_or_create_study(
        study_name="journal_study",
        storage_url="journal:/tmp/optuna.journal",
    )

    assert result == "study_obj"
    mock_journal_storage.assert_called_once()
    mock_create_study.assert_called_once_with(
        study_name="journal_study",
        direction="minimize",
        sampler="sampler_obj",
        storage="journal_storage_obj",
        load_if_exists=True,
    )


@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.optuna.samplers.TPESampler')
@unittest.mock.patch('opt.optimize.optuna.storages.JournalStorage')
def test_load_or_create_study_default_path(mock_journal_storage, mock_tpe_sampler, mock_create_study):
    mock_journal_storage.return_value = "journal_storage_obj"
    mock_tpe_sampler.return_value = "sampler_obj"
    mock_create_study.return_value = "study_obj"

    result = _load_or_create_study(study_name="default_study")

    assert result == "study_obj"
    # Default path should construct JournalStorage with JournalFileBackend wrapping a path
    mock_journal_storage.assert_called_once()
    args, _ = mock_journal_storage.call_args
    assert args[0] is not None  # a real JournalFileBackend is constructed
    mock_create_study.assert_called_once_with(
        study_name="default_study",
        direction="minimize",
        sampler="sampler_obj",
        storage="journal_storage_obj",
        load_if_exists=True,
    )


@unittest.mock.patch('opt.optimize.optuna.create_study')
@unittest.mock.patch('opt.optimize.optuna.samplers.TPESampler')
@unittest.mock.patch('opt.optimize.optuna.storages.RDBStorage')
def test_load_or_create_study_postgres(mock_rdb_storage, mock_tpe_sampler, mock_create_study):
    mock_rdb_storage.return_value = "rdb_storage_obj"
    mock_tpe_sampler.return_value = "sampler_obj"
    mock_create_study.return_value = "study_obj"

    result = _load_or_create_study(
        study_name="pg_study",
        storage_url="postgresql://user:pass@host/db",
    )

    assert result == "study_obj"
    mock_rdb_storage.assert_called_once_with(url="postgresql://user:pass@host/db")
    mock_create_study.assert_called_once_with(
        study_name="pg_study",
        direction="minimize",
        sampler="sampler_obj",
        storage="rdb_storage_obj",
        load_if_exists=True,
    )


# --- EarlyStoppingCallback tests ---

def test_early_stop_triggers_when_below_patience():
    study = unittest.mock.MagicMock()

    cb = EarlyStoppingCallback(patience_ratio=0.15, min_trials=3, n_trials=20)

    values = [10.0, 9.0, 9.5, 9.6]
    for i, val in enumerate(values):
        trial = unittest.mock.MagicMock()
        trial.number = i
        trial.value = val
        cb(study, trial)
    assert not study.stop.called, "should not stop before patience exhausted"

    trial = unittest.mock.MagicMock()
    trial.number = len(values)
    trial.value = 9.4
    cb(study, trial)
    assert study.stop.called, "should stop after patience exhausted"


def test_early_stop_not_triggers_when_improving():
    study = unittest.mock.MagicMock()

    cb = EarlyStoppingCallback(patience_ratio=0.15, min_trials=3, n_trials=20)

    for i, val in enumerate([10.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0]):
        trial = unittest.mock.MagicMock()
        trial.number = i
        trial.value = val
        cb(study, trial)

    assert not study.stop.called


def test_early_stop_ignores_none_value():
    study = unittest.mock.MagicMock()

    cb = EarlyStoppingCallback(patience_ratio=0.15, min_trials=3, n_trials=20)

    trial = unittest.mock.MagicMock()
    trial.number = 0
    trial.value = None
    cb(study, trial)

    assert not study.stop.called


def test_early_stop_triggers_boundary():
    study = unittest.mock.MagicMock()

    cb = EarlyStoppingCallback(patience_ratio=0.15, min_trials=3, n_trials=20)

    for i, val in enumerate([10.0, 9.0, 9.1, 9.2]):
        trial = unittest.mock.MagicMock()
        trial.number = i
        trial.value = val
        cb(study, trial)
    assert not study.stop.called

    trial = unittest.mock.MagicMock()
    trial.number = 4
    trial.value = 9.3
    cb(study, trial)
    assert study.stop.called


# --- CLI argument passthrough tests ---

@unittest.mock.patch('opt.optimize._load_or_create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_no_early_stop_disables_callbacks(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_load_study):
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_study.best_trial.params = {}
    mock_study.study_name = "test"
    mock_study.direction = "minimize"
    mock_study.trials = []
    mock_load_study.return_value = mock_study
    mock_cli_args.return_value = []

    main(early_stop=False, diagnostics=False)

    mock_study.optimize.assert_called_once_with(unittest.mock.ANY, n_trials=20, callbacks=[])


@unittest.mock.patch('opt.optimize._load_or_create_study')
@unittest.mock.patch('opt.optimize.subprocess.run')
@unittest.mock.patch('opt.optimize.slice_model')
@unittest.mock.patch('opt.optimize.cli_args')
def test_main_report_path_writes_diagnostics(mock_cli_args, mock_slice_model, mock_subprocess_run, mock_load_study, tmp_path):
    from opt.optimize import main

    mock_study = unittest.mock.MagicMock()
    mock_trial = unittest.mock.MagicMock()
    mock_trial.value = 25.0
    mock_trial.params = {"length": 355.0}
    mock_study.best_trial = mock_trial
    mock_study.study_name = "test"
    mock_study.direction = "minimize"
    mock_study.best_value = 25.0
    mock_study.best_params = {"length": 355.0}

    real_trial = unittest.mock.MagicMock()
    real_trial.state = optuna.trial.TrialState.COMPLETE
    real_trial.number = 0
    real_trial.value = 25.0
    real_trial.params = {"length": 355.0}
    real_trial.values = (25.0,)
    mock_study.trials = [real_trial]

    mock_load_study.return_value = mock_study
    mock_cli_args.return_value = []

    report_file = os.path.join(tmp_path, "test_report.json")
    main(diagnostics=True, report_path=report_file, early_stop=False)

    assert os.path.exists(report_file)
    with open(report_file) as f:
        report = json.load(f)
    assert report["study_name"] == "test"
    assert report["best_value"] == 25.0
    assert report["direction"] == "minimize"
    assert report["n_trials"] == 1


# --- print_convergence_diagnostics smoke test ---

def test_print_convergence_diagnostics_runs(capsys):
    from opt.optimize import print_convergence_diagnostics

    study = unittest.mock.MagicMock()
    study.study_name = "test"
    study.direction = "minimize"
    study.trials = []

    print_convergence_diagnostics(study)
    captured = capsys.readouterr()
    assert "Convergence Diagnostics" in captured.out
