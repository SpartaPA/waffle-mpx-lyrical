"""Run a free instruction on an Isaac scene or the ROS hardware backend."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--backend", choices=["isaac", "hardware"], default="isaac")
p.add_argument("--scene", type=Path, default=root.parent / "simulation/scene.usda")
p.add_argument("--output", type=Path, required=True)
p.add_argument("--show", action="store_true")
p.add_argument("--turns", type=int, default=8)
args = p.parse_args()
instruction = input("로봇에게 할 말 > ").strip()
if not instruction:
    p.error("지시문을 입력하세요.")
if not 1 <= args.turns <= 32:
    p.error("--turns must be between 1 and 32")
if args.backend == "hardware":
    if args.show:
        p.error("--show is an Isaac viewport option")
    subprocess.run(
        [
            sys.executable,
            str(root / "lessons/13-react/hardware_command.py"),
            "--instruction",
            instruction,
            "--output",
            str(args.output),
            "--turns",
            str(args.turns),
        ],
        check=True,
    )
    sys.exit(0)
weights = root / "learning/checkpoints"
python = os.environ.get(
    "ISAAC_SIM_PYTHON", str(Path.home() / "isaacsim6_venv/bin/python")
)
cmd = [
    python,
    str(root / "sim/evaluate_pick_place.py"),
    str(args.scene),
    os.environ.get("WAFFLE_COLOR_CHECKPOINT", str(weights / "waffle-color-73.npz")),
    str(args.output),
    "--controller",
    "color",
    "--parent-vla",
    str(weights / "waffle-hf-vla.pt"),
    "--free-instruction",
    instruction,
    "--turns",
    str(args.turns),
    "--seed",
    "8601",
]
if args.show:
    cmd.append("--show")
subprocess.run(cmd, check=True)
