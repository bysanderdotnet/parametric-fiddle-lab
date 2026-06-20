import subprocess
import json
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from sweep_corner_block_width import sweep_corner_block_width

class TestSweepCornerBlockWidth(unittest.TestCase):

    @patch("subprocess.run")
    def test_sweep_corner_block_width(self, mock_run):
        # Mock the JSON output from CAD generation
        # We will mock builtins.open to return a fake JSON string
        fake_json_data = json.dumps({"corner_blocks_mass_g": 357.12})

        # When subprocess is called, it does nothing
        mock_run.return_value = MagicMock()

        # Patch open globally so when sweep_corner_block_width calls open("violin_body.json", "r") it gets fake data
        with patch("builtins.open", mock_open(read_data=fake_json_data)):
            results = sweep_corner_block_width()

        # Check if subprocess was called the expected number of times (5 times for 5 widths)
        self.assertEqual(mock_run.call_count, 5)

        # Ensure that the subprocess arguments were passed correctly for the first run
        first_call_args = mock_run.call_args_list[0][0][0]
        self.assertEqual(first_call_args, ["python3", "cad/violin.py", "--corner_block_width", "10.0"])

        # Check the extracted results
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0], (10.0, 357.12))
        self.assertEqual(results[1], (15.0, 357.12))

if __name__ == '__main__':
    unittest.main()
