import argparse
import pytest
from unittest.mock import Mock

from common.params import add_arguments, suggest, cli_args, SPEC, NAMES

def test_add_arguments():
    parser = argparse.ArgumentParser()
    defaults = {"top_thickness": 5.0, "bridge_cutouts": True}
    add_arguments(parser, defaults)

    # Check that arguments were added
    args = parser.parse_args([])

    # Check defaults provided
    assert args.top_thickness == 5.0
    assert args.bridge_cutouts is True

    # Check defaults fallback from SPEC
    # Find the fallback for back_thickness in SPEC
    back_thickness_spec = next(item for item in SPEC if item[0] == "back_thickness")
    assert args.back_thickness == back_thickness_spec[2][0]

    # Check slicing parameters (no fallback provided in defaults, so they get 0.0 or from opt)
    infill_spec = next(item for item in SPEC if item[0] == "infill_density")
    assert args.infill_density == infill_spec[2][0]

def test_suggest():
    trial = Mock()
    trial.suggest_float.side_effect = lambda name, low, high: (low + high) / 2.0
    trial.suggest_int.side_effect = lambda name, low, high: (low + high) // 2
    trial.suggest_categorical.side_effect = lambda name, choices: choices[0]

    vals = suggest(trial)

    for name, kind, opt, _ in SPEC:
        if opt is not None:
            assert name in vals
            if kind == "float":
                assert vals[name] == (opt[0] + opt[1]) / 2.0
            elif kind == "int":
                assert vals[name] == (opt[0] + opt[1]) // 2
            else:
                assert vals[name] == opt[0]

    # Target A0 is in SPEC but opt is None, so it should not be in vals
    target_a0_spec = next(item for item in SPEC if item[0] == "target_a0_freq")
    if target_a0_spec[2] is None:
        assert "target_a0_freq" not in vals

def test_cli_args():
    # Construct input values
    values = {
        "top_thickness": 4.5,
        "bridge_cutouts": True,
        "bridge_central_cutout": False,
        "infill_density": 15.0, # should be excluded
        "layer_height": 0.2, # should be excluded
        "fingerboard_end_shape": "flat"
    }

    args = cli_args(values)

    # Check inclusions
    assert "--top_thickness" in args
    assert "4.5" in args
    assert "--bridge_cutouts" in args # True
    assert "--no-bridge_central_cutout" in args # False
    assert "--fingerboard_end_shape" in args
    assert "flat" in args

    # Check exclusions (slicing params)
    assert "--infill_density" not in args
    assert "15.0" not in args
    assert "--layer_height" not in args
    assert "0.2" not in args
