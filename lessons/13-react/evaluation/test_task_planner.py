"""Regression tests for ordered task dispatch after the language-model call."""

import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.extend([str(ROOT / "learning"), str(ROOT / "sim")])
from instruction_loop import TaskPlanner


class TaskPlannerTests(unittest.TestCase):
    def setUp(self):
        self.state = dict(
            base_xyz=[1, 2, 0],
            yaw_rad=math.pi / 2,
            cubes_xyz={"red": [0.9, 2, 0], "blue": [1.1, 2, 0]},
        )

    def test_robot_relative_reference_and_progress(self):
        task = {"steps": ["place_left", "photo"]}
        with patch("instruction_loop.ask_model", return_value=task):
            planner = TaskPlanner(
                "왼쪽 블록을 초록 칸에 옮기고 사진을 찍어", self.state
            )
        self.assertEqual(planner.next(self.state, [])["color"], "red")
        ok = {"result": {}}
        self.assertEqual(planner.next(self.state, [ok])["action"], "photo")
        self.assertEqual(planner.next(self.state, [ok, ok])["action"], "finish")
        with patch(
            "instruction_loop.plan", return_value={"action": "blocked"}
        ) as model:
            self.assertEqual(
                planner.next(self.state, [{"result": {"error": "lost block"}}])[
                    "action"
                ],
                "blocked",
            )
            model.assert_called_once()

    def test_unrelated_decoded_token_falls_back(self):
        with patch(
            "instruction_loop.ask_model", return_value={"steps": ["place_right"]}
        ):
            planner = TaskPlanner("팔 2번 관절을 움직여", self.state)
        self.assertIsNone(planner.steps)

    def test_conditional_task_uses_live_planner(self):
        with patch("instruction_loop.ask_model", return_value=dict(steps=["reactive"])):
            planner = TaskPlanner("가까워지면 촬영해", self.state)
        with patch("instruction_loop.plan", return_value={"action": "photo"}) as model:
            self.assertEqual(planner.next(self.state, [])["action"], "photo")
            model.assert_called_once()


if __name__ == "__main__":
    unittest.main()
