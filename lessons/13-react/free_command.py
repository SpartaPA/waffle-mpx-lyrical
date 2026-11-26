"""Launch one persistent simulated Waffle episode and accept a free instruction."""

import argparse
import os
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--scene", type=Path, default=root.parent / "simulation/scene.usda")
p.add_argument("--output", type=Path, required=True)
p.add_argument("--show", action="store_true")
p.add_argument("--turns", type=int, default=8)
args = p.parse_args()
instruction = input("로봇에게 할 말 > ").strip()
if not instruction:
    p.error("지시문을 입력하세요.")
weights = root / "learning/checkpoints"
python = os.environ.get(
    "ISAAC_SIM_PYTHON", str(Path.home() / "isaacsim6_venv/bin/python")
)
cmd = [
    python,
    str(root / "sim/evaluate_pick_place.py"),
    str(args.scene),
    str(weights / "waffle-color-73.npz"),
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
