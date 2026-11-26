"""Grade recorded physical effects and requested order without consulting the planner."""

import argparse
import json
import math
from pathlib import Path

from PIL import Image
from run import CASES, LAYOUTS


def left_color(state):
    x, y, _ = state["base_xyz"]
    yaw = state["yaw_rad"]

    def lateral(color):
        cx, cy, _ = state["cubes_xyz"][color]
        return -(cx - x) * math.sin(yaw) + (cy - y) * math.cos(yaw)

    return max(state["cubes_xyz"], key=lateral)


def on_goal(state, color):
    x, y, z = state["cubes_xyz"][color]
    error = math.dist((x, y), state["goal_xy"])
    return error <= 0.016 and abs(z - 0.051) <= 0.004, error


def score(trial, expected, target):
    rows = [json.loads(x) for x in (trial / "turns.jsonl").read_text().splitlines()]
    end = json.loads((trial / "outcome.json").read_text())
    initial = rows[0]["before"]
    color = left_color(initial) if target == "left" else target
    other = "red" if color == "blue" else "blue"
    problems = []
    actions = []
    placed = False
    photos = []

    def fail(turn, stage, detail):
        problems.append({"turn": turn, "stage": stage, "detail": detail})

    for row in rows:
        turn = row["turn"]
        choice = row["decision"]
        op = choice["action"]
        evidence = row["evidence"]
        if op in ("finish", "blocked"):
            if "error" in evidence:
                fail(turn, "execution", evidence["error"])
            if len(actions) < len(expected):
                fail(turn, "early_stop", f"{op} before {expected[len(actions) :]}")
            continue
        i = len(actions)
        actions.append(op)
        if i >= len(expected) or op != expected[i]:
            fail(
                turn,
                "sequence",
                f"expected {expected[i] if i < len(expected) else 'finish'}, got {op}",
            )
        if op == "place":
            picked = choice["color"]
            if picked != color:
                fail(turn, "selection", f"expected {color}, selected {picked}")
            heights = row.get("peak_lift_m", {})
            if heights.get(color, 0) < 0.025:
                fail(turn, "lift", f"{color} peak lift {heights.get(color, 0):.4f} m")
            if heights.get(other, 0) >= 0.025:
                fail(turn, "wrong_lift", f"{other} peak lift {heights[other]:.4f} m")
            settled, error = on_goal(row["after"], color)
            if not settled:
                fail(
                    turn,
                    "placement",
                    f"{color} center error {error:.4f} m; height {row['after']['cubes_xyz'][color][2]:.4f} m",
                )
            placed = settled and picked == color
        if op == "photo":
            filename = evidence.get("photo")
            if not filename or not (trial / filename).is_file():
                fail(turn, "photo", "photo file missing")
            else:
                photos.append(filename)
                try:
                    with Image.open(trial / filename) as im:
                        im.load()
                        if im.size != (640, 480) or im.format != "PNG":
                            fail(turn, "photo", f"unexpected image {im.format} {im.size}")
                except OSError as exc:
                    fail(turn, "photo", str(exc))
            intended_after = i < len(expected) and "place" in expected[:i]
            actual_after, _ = on_goal(row["before"], color)
            if intended_after != actual_after:
                fail(
                    turn,
                    "photo_state",
                    f"expected on_goal={intended_after}; observed {actual_after}",
                )
        if "error" in evidence:
            fail(turn, "execution", evidence["error"])
    recorded_photos = sorted(p.name for p in trial.glob("photo-*.png"))
    if sorted(photos) != recorded_photos or len(recorded_photos) != expected.count("photo"):
        fail(None, "photo_count", f"expected {expected.count('photo')} photos, found {recorded_photos}")
    if actions != expected and not any(
        p["stage"] in ("sequence", "early_stop") for p in problems
    ):
        fail(None, "sequence", f"expected {expected}, got {actions}")
    if end["stop"] != "model_finished":
        fail(None, "termination", end["stop"])
    final_ok, error = on_goal(end["state"], color)
    if not final_ok or not placed:
        fail(None, "final_state", f"{color} center error {error:.4f} m")
    return {
        "trial": trial.name,
        "success": not problems,
        "target": color,
        "expected": expected,
        "observed": actions,
        "initial_positions": initial["cubes_xyz"],
        "final_error_m": error,
        "stop": end["stop"],
        "first_failure": problems[0] if problems else None,
        "diagnostics": problems,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    results = []
    for name, _, expected, target in CASES:
        for layout, _, _ in LAYOUTS:
            trial = args.output / f"{name}-{layout}"
            if not (trial / "outcome.json").exists():
                raise SystemExit(f"Missing terminal result: {trial}")
            results.append(score(trial, expected, target))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
