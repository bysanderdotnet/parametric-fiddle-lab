import subprocess
import json
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from sweep_bottom_block_width import sweep_bottom_block_width

class TestSweepBottomBlockWidth(unittest.TestCase):

    @patch("subprocess.run")
    def test_sweep_bottom_block_width(self, mock_run):
        # Mock the JSON output from CAD generation
        fake_json_data = json.dumps({"bottom_block_mass_g": 15.0})

        # When subprocess is called, it does nothing
        mock_run.return_value = MagicMock()

        # Patch open globally so when sweep_bottom_block_width calls open("violin_body.json", "r") it gets fake data
        with patch("builtins.open", mock_open(read_data=fake_json_data)):
            results = sweep_bottom_block_width()

        # Check if subprocess was called the expected number of times (4 times for 4 widths)
        self.assertEqual(mock_run.call_count, 4)

        # Ensure that the subprocess arguments were passed correctly for the first run
        first_call_args = mock_run.call_args_list[0][0][0]
        self.assertEqual(first_call_args, ["python3", "cad/violin.py", "--bottom_block_width", "20.0"])

        # Check the extracted results
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0], (20.0, 15.0))
        self.assertEqual(results[1], (30.0, 15.0))
        self.assertEqual(results[2], (40.0, 15.0))
        self.assertEqual(results[3], (50.0, 15.0))

if __name__ == '__main__':
    unittest.main()
