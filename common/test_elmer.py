import unittest
import math
import os
import tempfile
from unittest.mock import patch, MagicMock

from common.elmer import parse_eigenmodes, write_sif, run_elmer

class TestElmer(unittest.TestCase):
    def test_parse_eigenmodes(self):
        stdout = """
Some Elmer output
EigenSolve:            1  1.000000000000E+04
EigenSolve:            2  4.000000000000E+04
More Elmer output
        """
        modes = parse_eigenmodes(stdout)

        self.assertEqual(len(modes), 2)

        self.assertEqual(modes[0]["mode"], 1)
        self.assertAlmostEqual(modes[0]["eigenvalue"], 10000.0)
        self.assertAlmostEqual(modes[0]["frequency_hz"], math.sqrt(10000.0) / (2 * math.pi))

        self.assertEqual(modes[1]["mode"], 2)
        self.assertAlmostEqual(modes[1]["eigenvalue"], 40000.0)
        self.assertAlmostEqual(modes[1]["frequency_hz"], math.sqrt(40000.0) / (2 * math.pi))

    def test_write_sif(self):
        with tempfile.TemporaryDirectory() as d:
            sif_path = os.path.join(d, "test.sif")
            mesh_dir = "my_mesh_dir"
            solver = "Solver 1\n  Equation = Heat Equation\nEnd"
            material = "Material 1\n  Density = 1.2\nEnd"

            write_sif(sif_path, mesh_dir, solver, material)

            self.assertTrue(os.path.exists(sif_path))

            with open(sif_path, "r") as f:
                content = f.read()

            self.assertIn('Mesh DB "." "my_mesh_dir"', content)
            self.assertIn('Solver 1', content)
            self.assertIn('Material 1', content)

    @patch('common.elmer.subprocess.run')
    def test_run_elmer(self, mock_run):
        # We need to mock two subprocess.run calls
        # 1. ElmerGrid
        # 2. ElmerSolver

        mock_grid_result = MagicMock()
        mock_grid_result.returncode = 0

        mock_solver_result = MagicMock()
        mock_solver_result.stdout = "EigenSolve:            1  1.000000000000E+04\n"
        mock_solver_result.returncode = 0

        # We'll set the side_effect to return mock_grid_result for ElmerGrid
        # and mock_solver_result for ElmerSolver.
        mock_run.side_effect = [mock_grid_result, mock_solver_result]

        with tempfile.TemporaryDirectory() as d:
            sif_path = os.path.join(d, "test.sif")
            modes = run_elmer("dummy.msh", "mesh_dir", sif_path, "Solver 1", "Material 1")

            self.assertEqual(mock_run.call_count, 2)

            # Check parsing worked
            self.assertIsNotNone(modes)
            self.assertEqual(len(modes), 1)
            self.assertEqual(modes[0]["mode"], 1)
            self.assertAlmostEqual(modes[0]["eigenvalue"], 10000.0)

if __name__ == '__main__':
    unittest.main()
