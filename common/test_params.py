import unittest
from unittest.mock import MagicMock
from common.params import add_arguments, suggest, cli_args, SPEC

class TestParams(unittest.TestCase):
    def test_add_arguments(self):
        parser = MagicMock()
        defaults = {"length": 355.0}

        add_arguments(parser, defaults)

        # Verify parser.add_argument was called for each spec item
        self.assertEqual(parser.add_argument.call_count, len(SPEC))

        # Test defaults were picked up properly
        # Since MagicMock tracks calls, we can check a few
        # Length float arg
        parser.add_argument.assert_any_call("--length", type=float, default=355.0, help="Length of the body")

    def test_suggest(self):
        trial = MagicMock()
        trial.suggest_float.return_value = 100.0
        trial.suggest_categorical.return_value = "slot"

        vals = suggest(trial)

        self.assertIn("length", vals)
        self.assertEqual(vals["length"], 100.0)

        self.assertIn("f_hole_profile", vals)
        self.assertEqual(vals["f_hole_profile"], "slot")

    def test_cli_args(self):
        values = {
            "length": 350.0,
            "f_hole_profile": "slot",
            "bridge_central_cutout": True,
            "bridge_cutouts": False,
            "infill_density": 15.0,
            "layer_height": 0.2
        }

        args = cli_args(values)

        self.assertIn("--length", args)
        self.assertIn("350.0", args)
        self.assertIn("--f_hole_profile", args)
        self.assertIn("slot", args)

        # bool args
        self.assertIn("--bridge_central_cutout", args)
        self.assertIn("--no-bridge_cutouts", args)

        # Ensure slicing params are excluded
        self.assertNotIn("--infill_density", args)
        self.assertNotIn("15.0", args)
        self.assertNotIn("--layer_height", args)
        self.assertNotIn("0.2", args)

if __name__ == '__main__':
    unittest.main()
