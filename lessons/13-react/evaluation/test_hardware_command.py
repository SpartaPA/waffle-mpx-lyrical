"""Offline regressions for hardware RGB-D coordinates and placement verification."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from geometry_msgs.msg import Transform
from sensor_msgs.msg import CameraInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hardware_command import landmarks, perform


class HardwareTests(unittest.TestCase):
    def test_projects_only_unambiguous_patches_with_depth(self):
        rgb = np.zeros((100, 100, 3), np.uint8)
        rgb[45:56, 45:56, 0] = 255
        rgb[10:20, 10:20, 1] = 255
        rgb[70:80, 70:80, 1] = 255
        rgb[80:90, 20:30, 2] = 255
        depth = np.full((100, 100), 0.25)
        depth[80:90, 20:30] = np.nan
        info = CameraInfo(k=[100.0, 0.0, 50.0, 0.0, 100.0, 50.0, 0.0, 0.0, 1.0])
        tf = Transform()
        tf.rotation.w = 1.0
        tf.translation.x = 0.03
        self.assertEqual(landmarks(rgb, depth, info, tf), {"red": [0.03, 0.0, 0.25]})

    def test_unmoved_cube_fails_after_policy_trajectory(self):
        hw, worker = Mock(), Mock()
        state = {
            "goal_xyz": [0.254, 0.008, 0.041],
            "cubes_xyz": {"red": [0.215, -0.022, 0.054]},
        }
        hw.observe.return_value = state, Mock()
        worker.predict.return_value = np.zeros((92, 7))
        item = dict(action="place", color="red", value=0.0, depends_on=[])
        with (
            patch("hardware_command.time.sleep"),
            self.assertRaisesRegex(ValueError, "Placement outside tolerance"),
        ):
            perform(hw, worker, item, [], Path("."))
        self.assertEqual(hw.step.call_count, 92)

    def test_missing_pad_prevents_actuation(self):
        hw, worker = Mock(), Mock()
        hw.observe.return_value = (
            {"goal_xyz": None, "cubes_xyz": {"red": [0.215, 0, 0.055]}},
            Mock(),
        )
        with self.assertRaisesRegex(ValueError, "missing"):
            perform(
                hw,
                worker,
                dict(action="place", color="red", value=0.0, depends_on=[]),
                [],
                Path("."),
            )
        worker.predict.assert_not_called()
        hw.step.assert_not_called()


if __name__ == "__main__":
    unittest.main()
