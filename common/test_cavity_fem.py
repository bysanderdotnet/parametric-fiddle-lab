import unittest
import math
import numpy as np
from unittest.mock import patch, mock_open
from common.cavity_fem import is_in_f_hole, cavity_eigenmodes

class TestCavityFem(unittest.TestCase):
    def test_is_in_f_hole_slot(self):
        p = {
            "f_hole_spacing": 80.0,
            "f_hole_x_offset": 0.0,
            "f_hole_y_offset": 0.0,
            "f_hole_angle": 90.0,
            "f_hole_profile": "slot",
            "f_hole_length": 70.0,
            "f_hole_width": 8.0,
            "f_hole_top_radius": 4.0,
            "f_hole_bottom_radius": 5.0
        }

        # Center of the right f-hole (x = 40, y = 0) should be inside
        self.assertTrue(is_in_f_hole(40.0, 0.0, p))

        # Center of the violin (x = 0, y = 0) should be outside
        self.assertFalse(is_in_f_hole(0.0, 0.0, p))

        # Far outside
        self.assertFalse(is_in_f_hole(100.0, 100.0, p))

    def test_is_in_f_hole_classic(self):
        p = {
            "f_hole_spacing": 80.0,
            "f_hole_x_offset": 0.0,
            "f_hole_y_offset": 0.0,
            "f_hole_angle": 90.0,
            "f_hole_profile": "classic",
            "f_hole_length": 70.0,
            "f_hole_width": 8.0,
            "f_hole_top_radius": 4.0,
            "f_hole_bottom_radius": 5.0
        }

        # Center of the right f-hole (x = 40, y = 0) should be inside
        self.assertTrue(is_in_f_hole(40.0, 0.0, p))

        # Center of the violin (x = 0, y = 0) should be outside
        self.assertFalse(is_in_f_hole(0.0, 0.0, p))

    @patch('common.cavity_fem.os.path.exists')
    @patch('common.cavity_fem._read_tets')
    def test_cavity_eigenmodes(self, mock_read_tets, mock_exists):
        # Create a single tetrahedron mesh: 4 vertices
        coords = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
        tets = np.array([[0, 1, 2, 3]])
        boundary_nodes = {0, 1, 2, 3}

        mock_read_tets.return_value = (coords, tets, boundary_nodes)

        # Simulate missing violin_body.json to avoid json.load parsing logic
        mock_exists.return_value = False

        # Should ask for min(4 vertices, n_modes) which might cause issues with eigsh if n is too small,
        # but let's test if it handles the math setup. Wait, eigsh needs shape > k.
        # Let's make a slightly bigger dummy mesh so k=6 modes can be asked if n_nodes > 6.
        # A simple cube-like arrangement
        coords = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
            [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1],
            [0.5, 0.5, 0.5], [0.5, 0.5, 1.5]
        ], dtype=float)
        # Non-degenerate tets
        # A valid tetrahedral mesh connecting these nodes
        tets = np.array([
            [0, 1, 2, 4],
            [1, 3, 2, 4],
            [1, 5, 3, 4],
            [2, 3, 6, 4],
            [3, 7, 6, 4],
            [3, 5, 7, 4],
            [4, 5, 6, 8],
            [5, 7, 6, 8],
            [6, 7, 8, 9]
        ])
        boundary_nodes = set(range(10))
        mock_read_tets.return_value = (coords, tets, boundary_nodes)

        modes = cavity_eigenmodes("dummy.msh", sound_speed=343.0, n_modes=3)

        self.assertIsInstance(modes, list)
        self.assertLessEqual(len(modes), 3) # Can be less because we filter > 1e-3
        for m in modes:
            self.assertIn("mode", m)
            self.assertIn("frequency_hz", m)
            self.assertIn("description", m)

if __name__ == '__main__':
    unittest.main()
