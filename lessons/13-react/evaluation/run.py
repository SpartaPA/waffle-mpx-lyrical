"""Run four held-out instructions on two independently initialized Isaac scenes."""

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CASES = [
    (
        "before",
        "옮기기 전의 작업대를 사진 한 장으로 기록해. 그런 다음 빨간 큐브를 초록 칸에 올려 둬.",
        ["photo", "place"],
        "red",
    ),
    (
        "after",
        "빨간 큐브부터 초록 칸에 안착시켜. 마지막 모습만 한 컷 찍어 줘.",
        ["place", "photo"],
        "red",
    ),
    (
        "bookends",
        "작업 전과 후의 사진을 한 장씩 남겨. 그 사이에 파란 큐브를 초록 칸에 옮겨 줘.",
        ["photo", "place", "photo"],
        "blue",
    ),
    (
        "relative",
        "두 큐브 중 로봇 기준 왼쪽에 있는 것만 초록 칸에 옮겨. 사진은 찍지 마.",
        ["place"],
        "left",
    ),
]
LAYOUTS = [("A", 9201, False), ("B", 9302, True)]


def run(scene, dest, selected=None):
    sim = os.environ.get(
        "ISAAC_SIM_PYTHON", str(Path.home() / "isaacsim6_venv/bin/python")
    )
    ckpt = ROOT / "learning/checkpoints"
    dest.mkdir(parents=True, exist_ok=False)
    for name, instruction, _, _ in CASES:
        for layout, seed, mirror in LAYOUTS:
            trial = dest / f"{name}-{layout}"
            if selected and trial.name not in selected:
                continue
            cmd = [
                sim,
                str(ROOT / "sim/evaluate_pick_place.py"),
                str(scene.resolve()),
                str(ckpt / "waffle-color-73.npz"),
                str(trial),
                "--controller",
                "color",
                "--parent-vla",
                str(ckpt / "waffle-hf-vla.pt"),
                "--free-instruction",
                instruction,
                "--seed",
                str(seed),
                "--turns",
                "6",
            ]
            if mirror:
                cmd.append("--mirror-layout")
            print(trial.name, flush=True)
            with trial.with_suffix(".log").open("w") as log:
                try:
                    code = subprocess.run(
                        cmd, stdout=log, stderr=subprocess.STDOUT, timeout=900
                    ).returncode
                except subprocess.TimeoutExpired:
                    raise RuntimeError(
                        f"Timed out: inspect {trial.name} before restarting"
                    )
            if code:
                print(f"Isaac exited {code}: {trial.name}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("scene", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--trial", action="append",
                   choices=[f"{case[0]}-{layout[0]}" for case in CASES for layout in LAYOUTS],
                   help="Run only this case in a new output directory (repeatable)")
    args = p.parse_args()
    run(args.scene, args.output, args.trial)
