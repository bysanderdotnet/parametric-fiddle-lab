import subprocess
import json
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from sweep_neck_length import sweep_neck_length

class TestSweepNeckLength(unittest.TestCase):

    @patch("subprocess.run")
    def test_sweep_neck_length(self, mock_run):
        # Mock the JSON output from CAD generation
        fake_json_data = json.dumps({"neck_mass_g": 95.0})

        # When subprocess is called, it does nothing
        mock_run.return_value = MagicMock()

        # Patch open globally so when sweep_neck_length calls open("violin_body.json", "r") it gets fake data
        with patch("builtins.open", mock_open(read_data=fake_json_data)):
            results = sweep_neck_length()

        # Check if subprocess was called the expected number of times (5 times for 5 lengths)
        self.assertEqual(mock_run.call_count, 5)

        # Ensure that the subprocess arguments were passed correctly for the first run
        first_call_args = mock_run.call_args_list[0][0][0]
        self.assertEqual(first_call_args, ["python3", "cad/violin.py", "--neck_length", "110.0"])

        # Check the extracted results
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0], (110.0, 95.0))
        self.assertEqual(results[1], (120.0, 95.0))
        self.assertEqual(results[2], (130.0, 95.0))
        self.assertEqual(results[3], (140.0, 95.0))
        self.assertEqual(results[4], (150.0, 95.0))

if __name__ == '__main__':
    unittest.main()
