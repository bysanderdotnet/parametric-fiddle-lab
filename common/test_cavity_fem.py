import unittest
import math
import numpy as np
from unittest.mock import patch, mock_open, MagicMock
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

        # Test ends of slot (rx > half_len)
        # rotated: x=40, y=36 => rx=36, ry=0 (inside circle at end)
        self.assertTrue(is_in_f_hole(40.0, 36.0, p))

    def test_is_in_f_hole_classic(self):
        p = {
            "f_hole_spacing": 80.0,
            "f_hole_x_offset": 0.0,
            "f_hole_y_offset": 0.0,
            "f_hole_angle": 90.0, # rotated 90 degrees
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

        # Ends of classic shape
        # rx = 30, ry = 0 -> top circle
        self.assertTrue(is_in_f_hole(40.0, 30.0, p))

        # rx = -30, ry = 0 -> bottom circle
        self.assertTrue(is_in_f_hole(40.0, -30.0, p))

        # Test ends of slot part
        self.assertTrue(is_in_f_hole(40.0, 29.0, p))

    @patch('common.cavity_fem.os.path.exists')
    @patch('common.cavity_fem._read_tets')
    def test_cavity_eigenmodes(self, mock_read_tets, mock_exists):
        # A simple cube-like arrangement
        coords = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
            [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1],
            [0.5, 0.5, 0.5], [0.5, 0.5, 1.5]
        ], dtype=float)
        # Non-degenerate tets
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

        # Simulate missing violin_body.json to avoid json.load parsing logic
        mock_exists.return_value = False

        modes = cavity_eigenmodes("dummy.msh", sound_speed=343.0, n_modes=3)

        self.assertIsInstance(modes, list)
        self.assertLessEqual(len(modes), 3) # Can be less because we filter > 1e-3
        for m in modes:
            self.assertIn("mode", m)
            self.assertIn("frequency_hz", m)
            self.assertIn("description", m)

    @patch('common.cavity_fem.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"rib_height": 30.0, "f_hole_spacing": 80.0, "f_hole_x_offset": 0.0, "f_hole_y_offset": 0.0, "f_hole_angle": 90.0, "f_hole_profile": "slot", "f_hole_length": 70.0, "f_hole_width": 8.0, "f_hole_top_radius": 4.0, "f_hole_bottom_radius": 5.0}')
    @patch('common.cavity_fem._read_tets')
    def test_cavity_eigenmodes_with_json(self, mock_read_tets, mock_file, mock_exists):
        # Coordinates that might hit the F-hole
        coords = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
            [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1],
            [40, 0, 25], [40, 0, 30] # Inside F-hole, z > rib_height * 0.8
        ], dtype=float)
        # Non-degenerate tets
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

        mock_exists.return_value = True

        modes = cavity_eigenmodes("dummy.msh", sound_speed=343.0, n_modes=3)

        self.assertIsInstance(modes, list)
        self.assertLessEqual(len(modes), 3)

    def test_is_in_f_hole_classic_circles(self):
        p = {
            "f_hole_spacing": 80.0,
            "f_hole_x_offset": 0.0,
            "f_hole_y_offset": 0.0,
            "f_hole_angle": 0.0,  # NOT rotated for simpler testing
            "f_hole_profile": "classic",
            "f_hole_length": 70.0,
            "f_hole_width": 8.0,
            "f_hole_top_radius": 4.0,
            "f_hole_bottom_radius": 5.0
        }

        dx_top = 70.0 * 0.4

        # Test top radius
        self.assertTrue(is_in_f_hole(40.0 + dx_top, 0.0, p))

        # Test bottom radius
        self.assertTrue(is_in_f_hole(40.0 - dx_top, 0.0, p))

        # Test classic slot edges (where cx2 is used)
        self.assertTrue(is_in_f_hole(40.0 + 31.0, 0.0, p))

    @patch.dict("sys.modules", {"gmsh": MagicMock()})
    def test_read_tets(self):
        import sys
        mock_gmsh = sys.modules['gmsh']
        mock_gmsh.model.mesh.getNodes.return_value = (
            [1, 2, 3, 4, 5],
            [0,0,0, 1,0,0, 0,1,0, 0,0,1, 0.5,0.5,0.5],
            None
        )
        mock_gmsh.model.mesh.getElementsByType.side_effect = [
            (None, [1, 2, 3, 4, 1, 2, 3, 5]), # 4-node tets flat
            (None, [1, 2, 3, 1, 2, 4])        # 3-node tri (boundary) flat
        ]

        from common.cavity_fem import _read_tets
        coords, tets, bnd = _read_tets("dummy.msh")

        self.assertEqual(coords.shape, (5, 3))
        self.assertEqual(tets.shape, (2, 4))
        self.assertIn(0, bnd)
        self.assertIn(1, bnd)
        self.assertIn(2, bnd)
        self.assertIn(3, bnd)
        self.assertNotIn(4, bnd)

    def test_is_in_f_hole_classic_circles_rotated(self):
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

        dx_top = 70.0 * 0.4

        # Test top radius
        self.assertTrue(is_in_f_hole(40.0, dx_top, p))

        # Test bottom radius
        self.assertTrue(is_in_f_hole(40.0, -dx_top, p))
    def test_is_in_f_hole_classic_circles_exact(self):
        p = {
            "f_hole_spacing": 80.0,
            "f_hole_x_offset": 0.0,
            "f_hole_y_offset": 0.0,
            "f_hole_angle": 0.0,
            "f_hole_profile": "classic",
            "f_hole_length": 70.0,
            "f_hole_width": 8.0,
            "f_hole_top_radius": 4.0,
            "f_hole_bottom_radius": 5.0
        }

        dx_top = 70.0 * 0.4

        # We need a point that is OUTSIDE the central slot but INSIDE the top/bottom circles.
        # The central slot length is 70 * 0.8 = 56, so half_len = 28.
        # Top circle center is at rx = dx_top = 28.
        # Wait, if rx=28, it's <= half_len, so it returns True on line 61.
        # We need a point with rx > 28 where it's inside the circle but outside the slot end-cap.
        # Slot end-cap is centered at rx=28, radius=half_width=4.
        # Top circle is centered at rx=28, radius=4. They are the same!
        # Wait, if rx > 28, the point is checked against the slot end-cap first:
        # (rx - 28)**2 + ry**2 <= 4**2. If true, returns True on line 66.
        # Then it checks the top circle: (rx - 28)**2 + ry**2 <= 4**2. It's the same condition!
        # So line 70 is unreachable if top_radius <= half_width.

        # Let's make top_radius > half_width to hit line 70
        p["f_hole_top_radius"] = 6.0
        p["f_hole_bottom_radius"] = 7.0

        # Now pick a point inside top circle but outside slot end-cap
        # e.g., rx = 28, ry = 5
        # For rx=28, abs(rx) <= 28, but abs(ry) = 5 > 4 (half_width), so line 61 is false.
        # Wait, if rx=28, abs(rx) is not > half_len, so line 63 is false.
        # Then it hits line 69! (rx-28)**2 + ry**2 = 0 + 25 = 25 <= 36 (6**2).
        self.assertTrue(is_in_f_hole(40.0 + 28.0, 5.0, p))

        # Bottom circle: center at rx=-28, radius=7
        # Point: rx=-28, ry=6
        self.assertTrue(is_in_f_hole(40.0 - 28.0, 6.0, p))

if __name__ == '__main__':
    unittest.main()
