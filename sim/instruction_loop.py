"""Ground free-language requests in a persistent Isaac tabletop episode."""

import json
import math
import os
from urllib.request import Request, urlopen

import numpy as np
from actions import HIGH, LOW
from PIL import Image

ACTIONS = {
    "place": "Move one visible red/blue block onto the green square using the color VLA. color = red or blue.",
    "vla": "Run eight steps of the learned sensorimotor policy. text = English subgoal.",
    "joint": "Set one arm joint. index = 1..4, value = absolute radians.",
    "grip": "Set the gripper opening target. value = meters in [-0.010, 0.019].",
    "translate": "Drive forward (+) or backwards (-). value = signed meters, at most 0.15 per call.",
    "rotate": "Turn left (+) or right (-). value = signed radians, at most 1.57 per call.",
    "photo": "Save the current camera observation as a requested photograph.",
    "finish": "End when all requested changes are supported by the history and observation.",
    "blocked": "End with the missing capability or ambiguous target in text.",
}
SYSTEM = (
    "You control a simulated Waffle robot. Given the original user instruction, current observed "
    "state and action history, select ONLY the next action. Preserve order, conditions and quantities. "
    "Inspect physical feedback before finishing. Never invent a successful effect. If the goal is "
    "unsupported or ambiguous choose blocked. No commentary. In depends_on give only zero-based prior successful turns whose result this action needs. Do not repeat a completed operation. Only take a photo after requested prerequisites succeed. Available primitives: "
    + json.dumps(ACTIONS)
)
SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": list(ACTIONS)},
        "color": {"type": "string", "enum": ["red", "blue", "none"]},
        "depends_on": {"type": "array", "items": {"type": "integer"}},
        "text": {"type": "string"},
        "index": {"type": "integer"},
        "value": {"type": "number"},
    },
    "required": ["action", "color", "text", "index", "value", "depends_on"],
}


def ask_model(system, message, schema):
    payload = {
        "model": os.getenv("WAFFLE_PLANNER_MODEL", "qwen2.5:7b"),
        "format": schema,
        "stream": False,
        "keep_alive": "3m",
        "options": {"temperature": 0, "num_ctx": 4096, "num_gpu": 0},
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(message, ensure_ascii=False),
            },
        ],
    }
    req = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(req, timeout=120) as response:
        return json.loads(json.load(response)["message"]["content"])


def plan(instruction, observation, history, *, system=SYSTEM):
    return ask_model(
        system,
        dict(instruction=instruction, current=observation, history=history),
        SCHEMA,
    )


TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "mode": {"enum": ["ordered", "reactive"]},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"enum": ["place", "photo"]},
                    "target": {"enum": ["none", "red", "blue", "left", "right"]},
                },
                "required": ["action", "target"],
            },
        },
    },
    "required": ["mode", "steps"],
}
TASK_SYSTEM = (
    "Translate the user's request into its ordered effects. Use ordered mode only for "
    "unconditional sequences consisting entirely of taking photographs and/or placing visible "
    "red/blue cubes on the green pad. Use reactive mode for other goals, questions, conditions, "
    "ambiguous referents, or unsupported destinations. Preserve explicit counts, before/after "
    "relations and negation. A photograph is one photo step, target none. A transfer is one "
    "place step, never locomotion. For a robot-relative reference use left/right as the target. "
    "Only include requested effects. Emit each step in chronological execution order."
)


class TaskPlanner:
    """Retain the requested sequence and advance only on successful execution feedback."""

    def __init__(self, instruction, state):
        self.instruction = instruction
        task = ask_model(TASK_SYSTEM, {"instruction": instruction}, TASK_SCHEMA)
        self.steps = None
        self.task = task
        if task.get("mode") != "ordered" or not task.get("steps"):
            return
        steps = []
        for step in task["steps"]:
            op, target = step["action"], step["target"]
            if op == "place":
                if target in ("left", "right"):
                    x, y, _ = state["base_xyz"]
                    yaw = state["yaw_rad"]
                    offsets = {
                        c: -(xyz[0] - x) * math.sin(yaw) + (xyz[1] - y) * math.cos(yaw)
                        for c, xyz in state["cubes_xyz"].items()
                    }
                    if (
                        len(offsets) != 2
                        or abs(max(offsets.values()) - min(offsets.values())) < 0.001
                    ):
                        return
                    pick = max if target == "left" else min
                    target = pick(offsets, key=offsets.get)
                if target not in state["cubes_xyz"]:
                    return
            elif op != "photo" or target != "none":
                return
            steps.append((op, target))
        self.steps = steps

    def next(self, state, history):
        if self.steps is None or any("error" in h["result"] for h in history):
            return plan(self.instruction, state, history)
        index = len(history)
        op, target = (
            self.steps[index] if index < len(self.steps) else ("finish", "none")
        )
        return dict(
            action=op,
            color=target,
            depends_on=[index - 1] if index else [],
            text="",
            value=0,
            index=0,
        )


def run_instruction(
    args, body, rgb, cubes, controls, wheels, advance, worker, predict, goal
):
    def position(prim):
        return prim.get_world_poses()[0].numpy()[0].astype(float)

    def joints():
        return body.get_dof_positions(dof_indices=controls).numpy()[0].astype(float)

    def status():
        quat = body.get_world_poses()[1].numpy()[0]
        w, x, y, z = quat
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        return {
            "base_xyz": position(body).round(4).tolist(),
            "yaw_rad": round(yaw, 4),
            "joints": joints().round(4).tolist(),
            "goal_xy": goal.tolist(),
            "cubes_xyz": {k: position(v).round(4).tolist() for k, v in cubes.items()},
        }

    def camera(path):
        pixels = np.asarray(rgb.get_data())
        if pixels.shape[:2] != (480, 640):
            raise RuntimeError("No live D435 frame")
        Image.fromarray(pixels[:, :, :3]).save(path)

    def apply(target):
        q = joints()
        target = np.asarray(target, dtype=float)
        if target.shape != (5,) or not np.isfinite(target).all():
            raise ValueError("Invalid arm target")
        step = np.array([0.35] * 4 + [0.012]) * 0.25
        q = q + np.clip(np.clip(target, LOW[2:], HIGH[2:]) - q, -step, step)
        body.set_dof_position_targets(q.tolist(), dof_indices=controls)
        body.set_dof_position_targets(
            [q[-1]], dof_indices=body.get_dof_indices("gripper_right_joint")
        )
        advance(0.25)

    history = []
    reason = "budget_exhausted"
    vla_inferences = 0
    completed_edges = 0
    planner = TaskPlanner(args.free_instruction, status())
    (args.output / "task.json").write_text(
        json.dumps(planner.task, ensure_ascii=False, indent=2)
    )
    for turn in range(args.turns):
        before = status()
        frame = args.output / f"observation-{turn:02d}.png"
        camera(frame)
        item = planner.next(before, history)
        op = item.get("action")
        evidence = {}
        peak_lift = None
        try:
            deps = item["depends_on"]
            if not isinstance(deps, list) or any(
                type(d) != int or not 0 <= d < turn or "error" in history[d]["result"]
                for d in deps
            ):
                raise ValueError("Unresolved predecessor")
            if op not in ACTIONS:
                raise ValueError("Unknown action")
            value = float(item["value"])
            if not math.isfinite(value):
                raise ValueError("Invalid value")
            if op == "photo":
                dest = args.output / f"photo-{turn:02d}.png"
                camera(dest)
                evidence["photo"] = dest.name
            elif op in ("translate", "rotate"):
                cap = 0.15 if op == "translate" else 1.57
                if abs(value) > cap or value == 0:
                    raise ValueError("Base target outside range")
                rates = np.array(
                    [1.0, 1.0] if op == "translate" else [-1.0, 1.0]
                ) * math.copysign(2.0, value)
                try:
                    for _ in range(160):
                        body.set_dof_velocity_targets(
                            rates.tolist(), dof_indices=wheels
                        )
                        advance(0.1)
                        current = status()
                        dx, dy = np.subtract(
                            current["base_xyz"][:2], before["base_xyz"][:2]
                        )
                        delta = (
                            dx * math.cos(before["yaw_rad"])
                            + dy * math.sin(before["yaw_rad"])
                            if op == "translate"
                            else math.remainder(
                                current["yaw_rad"] - before["yaw_rad"], 2 * math.pi
                            )
                        )
                        if delta / value >= 0.97:
                            break
                    else:
                        raise ValueError("Base target not reached")
                finally:
                    body.set_dof_velocity_targets([0.0, 0.0], dof_indices=wheels)
                    advance(0.2)
                evidence["measured_change"] = round(delta, 4)
            elif op in ("joint", "grip"):
                idx = item["index"] - 1 if op == "joint" else 4
                if (op == "joint" and not 0 <= idx < 4) or not LOW[
                    2 + idx
                ] <= value <= HIGH[2 + idx]:
                    raise ValueError("Joint target outside limits")
                target = joints()
                target[idx] = value
                for _ in range(48):
                    apply(target)
                    if abs(joints()[idx] - value) < (0.002 if idx == 4 else 0.035):
                        break
                else:
                    raise ValueError("Joint target not reached")
            elif op in ("place", "vla"):
                text = item["color"] if op == "place" else item["text"].strip()
                if not text or (op == "place" and text not in cubes):
                    raise ValueError("Invalid VLA argument")
                instruction = (
                    f"Pick up the {text} cube and place it on the green square."
                    if op == "place"
                    else text
                )
                steps = 92 if op == "place" else 8
                peak_lift = {color: 0.0 for color in cubes}
                for step in range(steps):
                    if op == "vla" or step == 0:
                        camera(frame)
                        lin, ang = body.get_velocities()
                        state = [
                            float(lin.numpy()[0, 0]),
                            float(ang.numpy()[0, 2]),
                            *joints().tolist(),
                        ]
                        vla_inferences += 1
                        pred = predict(
                            worker, frame, state, instruction, continuous=op == "vla"
                        )
                        expected = (7,) if op == "vla" else (92, 7)
                        if pred.shape != expected or not np.isfinite(pred).all():
                            raise ValueError("Invalid VLA prediction")
                    action = pred if op == "vla" else pred[step]
                    if np.abs(action[:2]).max() > 1e-5:
                        raise ValueError("Expected a parked-base arm policy")
                    apply(action[2:])
                    for color, cube in cubes.items():
                        lift = float(position(cube)[2] - before["cubes_xyz"][color][2])
                        peak_lift[color] = max(peak_lift[color], lift)
                advance(0.5)
                if op == "place":
                    evidence["center_error_m"] = float(
                        np.linalg.norm(position(cubes[text])[:2] - goal)
                    )
                    if (
                        evidence["center_error_m"] > 0.016
                        or abs(position(cubes[text])[2] - 0.051) > 0.004
                    ):
                        raise ValueError("Block did not settle at target")
            elif op in ("finish", "blocked"):
                reason = "model_finished" if op == "finish" else "blocked"
        except (ValueError, KeyError, TypeError) as exc:
            evidence["error"] = str(exc)
        record = {
            "turn": turn,
            **(
                {"peak_lift_m": peak_lift}
                if op in ("place", "vla") and peak_lift is not None
                else {}
            ),
            "decision": item,
            "before": before,
            "after": status(),
            "evidence": evidence,
        }
        with (args.output / "turns.jsonl").open("a") as log:
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
        if "error" not in evidence:
            completed_edges += len(set(item["depends_on"]))
        print("TURN", turn, op, evidence, flush=True)
        history.append({"turn": turn, "decision": item, "result": evidence})
        if reason != "budget_exhausted":
            break
    camera(args.output / "final.png")
    (args.output / "outcome.json").write_text(
        json.dumps(
            {
                "instruction": args.free_instruction,
                "stop": reason,
                "planner_calls": 1
                + sum(
                    planner.steps is None
                    or any("error" in h["result"] for h in history[:i])
                    for i in range(len(history))
                ),
                "vla_inferences": vla_inferences,
                "declared_dependency_edges": completed_edges,
                "state": status(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
