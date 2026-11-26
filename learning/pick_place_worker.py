"""Run the frozen policy in its training environment over a local pipe."""
import json
import sys
from PIL import Image
from policy import Policy

color_mode = len(sys.argv) >= 3
if color_mode:
    from pathlib import Path
    from color_imitation import ColorPolicy
    policy = ColorPolicy(Path(sys.argv[1]), Path(sys.argv[2]))
else:
    policy = Policy(sys.argv[1], 'cuda')
print(json.dumps({'ready': True}), flush=True)
for line in sys.stdin:
    obs = json.loads(line)
    with Image.open(obs['rgb']) as frame:
        predict = policy.plan if color_mode else policy.predict
        if color_mode and "--adaptive" in sys.argv and obs.get("continuous"):
            predict = policy.vla.policy.predict
        action = predict(frame, obs['instruction'], obs['state'])
    print(json.dumps(action.tolist(), allow_nan=False), flush=True)
