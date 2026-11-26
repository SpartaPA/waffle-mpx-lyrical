"""Execute free instructions on the Waffle ROS hardware controllers."""

import argparse
import json
import math
import os
from pathlib import Path
import select
import subprocess
import sys
import time

import cv2
from cv_bridge import CvBridge
import message_filters
import numpy as np
from PIL import Image as PILImage
import rclpy
from rclpy.duration import Duration
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from scipy.spatial.transform import Rotation
from tf2_ros import Buffer, TransformListener, TransformException
from sensor_msgs.msg import Image, CameraInfo, JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "learning"), str(ROOT / "sim")])
from actions import JOINTS, LOW, HIGH
from instruction_loop import SYSTEM, plan

SYSTEM_HW = SYSTEM.replace("a simulated Waffle", "a physical Waffle") + (
    " cubes_xyz and goal_xyz are current RGB-D visible surface estimates in base_footprint "
    "(x forward, y left, z up), while base_xyz and yaw_rad are in odom. "
    "Missing detections are unknown. The place primitive needs a visible block and a visible "
    "green pad near the trained target (0.254, 0.008) in the base frame. "
    "Respect an execution error and inspect the new observation before retrying."
)


def landmarks(rgb, depth, info, transform):
    """Median of aligned metric depth points for a single visible patch of each color."""
    out = {}
    axes = {"red": 0, "green": 1, "blue": 2}
    pixels = rgb.astype(np.float32)
    intrinsics = np.asarray(info.k).reshape(3, 3)
    for name, axis in axes.items():
        channel = pixels[:, :, axis]
        mask = (channel > 45) & (channel > 1.6 * np.delete(pixels, axis, 2).max(2))
        _, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype("uint8"))
        candidates = np.flatnonzero(stats[1:, cv2.CC_STAT_AREA] >= 50) + 1
        if len(candidates) != 1:
            continue
        y, x = np.nonzero((labels == candidates[0]) & np.isfinite(depth) & (depth > 0))
        if len(x) < 25:
            continue
        uv = np.column_stack([x, y]).astype("float64").reshape(-1, 1, 2)
        xy = cv2.undistortPoints(
            uv, intrinsics, np.asarray(info.d) if len(info.d) else None
        )
        points = (
            np.column_stack((xy.reshape(-1, 2), np.ones(len(x)))) * depth[y, x, None]
        )
        q, t = transform.rotation, transform.translation
        rot = Rotation.from_quat([q.x, q.y, q.z, q.w])
        out[name] = (
            (rot.apply(np.median(points, axis=0)) + [t.x, t.y, t.z]).round(4).tolist()
        )
    return out


class Hardware:
    def __init__(self, node):
        self.node = node
        self.bridge = CvBridge()
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, node)
        self.info = self.sample = None
        node.create_subscription(
            CameraInfo,
            "camera/color/camera_info",
            self.set_info,
            qos_profile_sensor_data,
        )
        topics = [
            (Image, "camera/color/image_raw"),
            (Image, "camera/aligned_depth_to_color/image_raw"),
            (JointState, "joint_states"),
            (Odometry, "odom"),
        ]
        self.subs = [
            message_filters.Subscriber(
                node, typ, topic, qos_profile=qos_profile_sensor_data
            )
            for typ, topic in topics
        ]
        self.sync = message_filters.ApproximateTimeSynchronizer(self.subs, 15, 0.1)
        self.sync.registerCallback(self.receive)
        self.arm = node.create_publisher(
            JointTrajectory, "arm_controller/joint_trajectory", 1
        )
        self.grip = node.create_publisher(
            JointTrajectory, "gripper_controller/joint_trajectory", 1
        )
        self.base = node.create_publisher(TwistStamped, "cmd_vel", 1)

    def set_info(self, msg):
        self.info = msg

    def receive(self, *msgs):
        self.sample = msgs

    def observe(self, timeout=4):
        deadline = time.monotonic() + timeout
        self.sample = None
        diagnostic = (
            "missing synchronized RGB, aligned depth, joints, odometry or camera_info"
        )
        while time.monotonic() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.05)
            if self.sample is None or self.info is None:
                continue
            rgb, depth, joints, odom = self.sample
            self.sample = None
            stamp = Time.from_msg(rgb.header.stamp)
            age = (self.node.get_clock().now() - stamp).nanoseconds * 1e-9
            if not -0.1 <= age <= 0.4:
                diagnostic = "stale sensor stamps; check host clock synchronization"
                continue
            if (
                rgb.header.frame_id != self.info.header.frame_id
                or depth.header.frame_id != rgb.header.frame_id
            ):
                raise ValueError(
                    "RGB, depth and calibration must share the color optical frame"
                )
            if (
                (rgb.width, rgb.height) != (640, 480)
                or (depth.width, depth.height) != (640, 480)
                or (self.info.width, self.info.height) != (640, 480)
            ):
                raise ValueError("Expected aligned 640x480 images and calibration")
            if (
                self.info.distortion_model not in ("plumb_bob", "rational_polynomial")
                or self.info.k[0] <= 0
                or self.info.k[4] <= 0
            ):
                raise ValueError("Unsupported or missing color calibration")
            try:
                tf = self.buffer.lookup_transform(
                    "base_footprint", rgb.header.frame_id, stamp
                )
            except TransformException as exc:
                diagnostic = str(exc)
                continue
            image = self.bridge.imgmsg_to_cv2(rgb, "rgb8")
            z = self.bridge.imgmsg_to_cv2(depth, "passthrough").astype(float)
            if depth.encoding == "16UC1":
                z *= 0.001
            elif depth.encoding != "32FC1":
                raise ValueError("Unsupported depth units")
            marks = landmarks(image, z, self.info, tf.transform)
            positions = dict(zip(joints.name, joints.position))
            q = [positions[k] for k in JOINTS]
            pose, vel = odom.pose.pose, odom.twist.twist
            quat = pose.orientation
            yaw = Rotation.from_quat([quat.x, quat.y, quat.z, quat.w]).as_euler("xyz")[
                2
            ]
            state = dict(
                base_xyz=[pose.position.x, pose.position.y, pose.position.z],
                yaw_rad=float(yaw),
                joints=q,
                twist=[vel.linear.x, vel.angular.z],
                cubes_xyz={k: v for k, v in marks.items() if k != "green"},
                goal_xyz=marks.get("green"),
            )
            if not np.isfinite([*q, *state["base_xyz"], yaw, *state["twist"]]).all():
                raise ValueError("Invalid robot feedback")
            return state, PILImage.fromarray(image)
        raise TimeoutError(diagnostic)

    def drive(self, linear=0.0, angular=0.0):
        msg = TwistStamped()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.twist.linear.x, msg.twist.angular.z = linear, angular
        self.base.publish(msg)

    def move_base(self, op, value, state):
        cap = 0.15 if op == "translate" else 1.57
        if not 0 < abs(value) <= cap or not self.base.get_subscription_count():
            raise ValueError("Invalid base target or controller unavailable")
        yaw = state["yaw_rad"]
        start = np.array(state["base_xyz"][:2])
        deadline = time.monotonic() + 15
        try:
            while time.monotonic() < deadline:
                now, _ = self.observe()
                delta = (
                    np.dot(
                        np.array(now["base_xyz"][:2]) - start,
                        [math.cos(yaw), math.sin(yaw)],
                    )
                    if op == "translate"
                    else math.remainder(now["yaw_rad"] - yaw, 2 * math.pi)
                )
                if delta / value >= 0.97:
                    return {"measured_change": float(delta)}
                speed = math.copysign(
                    min(
                        0.05 if op == "translate" else 0.3,
                        max(0.01, abs(value - delta)),
                    ),
                    value,
                )
                if op == "translate":
                    self.drive(speed, 0.0)
                else:
                    self.drive(0.0, speed)
            raise ValueError("Base target not reached")
        finally:
            self.drive()

    def step(self, target):
        state, _ = self.observe()
        if not all(p.get_subscription_count() for p in (self.arm, self.grip)):
            raise ValueError("Missing trajectory controller subscribers")
        q = np.array(state["joints"])
        limits = np.array([0.35] * 4 + [0.012]) * 0.25
        values = q + np.clip(np.clip(target, LOW[2:], HIGH[2:]) - q, -limits, limits)
        for pub, names, pos in [
            (self.arm, JOINTS[:4], values[:4]),
            (self.grip, JOINTS[4:], values[4:]),
        ]:
            point = JointTrajectoryPoint(
                positions=pos.tolist(), time_from_start=Duration(seconds=0.25).to_msg()
            )
            pub.publish(JointTrajectory(joint_names=names, points=[point]))
        time.sleep(0.25)


class PolicyWorker:
    def __init__(self, output):
        self.output = output
        self.process = None
        self.calls = 0

    def reply(self, timeout):
        if not select.select([self.process.stdout], [], [], timeout)[0]:
            self.close()
            raise TimeoutError("VLA inference timed out")
        line = self.process.stdout.readline()
        if not line:
            self.close()
            raise RuntimeError("VLA worker exited; inspect stderr")
        return json.loads(line)

    def predict(self, image, state, text, continuous):
        if self.process is None:
            weights = ROOT / "learning/checkpoints"
            env = os.environ.copy()
            env["PYTHONPATH"] = env.get(
                "WAFFLE_LEARNING_DEPS", str(ROOT.parent / ".learning-deps")
            )
            env["LD_LIBRARY_PATH"] = env.get("WAFFLE_WORKER_LD_LIBRARY_PATH", "")
            cmd = [
                env.get(
                    "ISAAC_LAB_PYTHON", str(Path.home() / "IsaacLab/.venv/bin/python")
                ),
                str(ROOT / "learning/pick_place_worker.py"),
                env.get("WAFFLE_COLOR_CHECKPOINT", str(weights / "waffle-color-73.npz")),
                str(weights / "waffle-hf-vla.pt"),
                "--adaptive",
            ]
            self.process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env
            )
            if self.reply(180) != {"ready": True}:
                raise RuntimeError("VLA worker initialization failed")
        path = self.output / f"policy-{self.calls:03d}.png"
        image.save(path)
        obs = dict(
            rgb=str(path.resolve()),
            state=state["twist"] + state["joints"],
            instruction=text,
            continuous=continuous,
        )
        self.process.stdin.write(json.dumps(obs) + "\n")
        self.process.stdin.flush()
        self.calls += 1
        result = self.reply(60)
        if isinstance(result, dict):
            raise ValueError(result["error"])
        a = np.asarray(result, dtype=float)
        if a.shape != ((7,) if continuous else (92, 7)) or not np.isfinite(a).all():
            raise ValueError("Invalid VLA output")
        if np.max(np.abs(a[..., :2])) > 1e-5:
            raise ValueError("This arm policy requires a parked base")
        return a

    def close(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process.stdin.close()
            self.process.stdout.close()
            self.process = None


def perform(hw, worker, item, history, output):
    op, value = item["action"], float(item["value"])
    deps = item["depends_on"]
    if not isinstance(deps, list) or any(
        type(i) != int or not 0 <= i < len(history) or "error" in history[i]["result"]
        for i in deps
    ):
        raise ValueError("Unresolved predecessor")
    if not math.isfinite(value):
        raise ValueError("Invalid target")
    state, frame = hw.observe()
    if op == "photo":
        path = output / f"photo-{len(history):02d}.png"
        frame.save(path)
        return {"photo": path.name}
    if op in ("finish", "blocked"):
        return {}
    if op in ("rotate", "translate"):
        return hw.move_base(op, value, state)
    if op in ("joint", "grip"):
        i = item["index"] - 1 if op == "joint" else 4
        if (op == "joint" and not 0 <= i < 4) or not LOW[2 + i] <= value <= HIGH[2 + i]:
            raise ValueError("Joint target outside limits")
        for _ in range(80):
            target = state["joints"].copy()
            if abs(target[i] - value) <= (0.001 if i == 4 else 0.025):
                return {"measured_position": target[i]}
            target[i] = value
            hw.step(target)
            state, _ = hw.observe()
        raise ValueError("Joint target not reached")
    if op not in ("place", "vla"):
        raise ValueError("Unknown action")
    if op == "vla":
        if not item["text"].strip():
            raise ValueError("Empty VLA subgoal")
        for _ in range(8):
            state, frame = hw.observe()
            action = worker.predict(frame, state, item["text"], True)
            hw.step(action[2:])
        return {"policy_steps": 8}
    color = item["color"]
    if color not in state["cubes_xyz"] or state["goal_xyz"] is None:
        raise ValueError("Block or pad missing from RGB-D")
    goal = np.asarray(state["goal_xyz"])
    if math.dist(goal[:2], [0.254, 0.008]) > 0.016 or abs(goal[2] - 0.041) > 0.01:
        raise ValueError("Green pad outside learned tabletop workspace")
    text = f"Pick up the {color} cube and place it on the green square."
    trajectory = worker.predict(frame, state, text, False)
    current, _ = hw.observe()
    if (
        color not in current["cubes_xyz"]
        or current["goal_xyz"] is None
        or max(
            math.dist(state["cubes_xyz"][color], current["cubes_xyz"][color]),
            math.dist(goal, current["goal_xyz"]),
        )
        > 0.012
    ):
        raise ValueError("Scene changed during inference")
    for action in trajectory:
        hw.step(action[2:])
    time.sleep(0.5)
    end, _ = hw.observe()
    if color not in end["cubes_xyz"] or end["goal_xyz"] is None:
        raise ValueError("Cannot verify placement from aligned RGB-D")
    delta = np.asarray(end["cubes_xyz"][color]) - end["goal_xyz"]
    error = float(np.linalg.norm(delta[:2]))
    if error > 0.016 or not 0.002 <= delta[2] <= 0.026:
        raise ValueError(
            f"Placement outside tolerance: xy={error:.4f}, dz={delta[2]:.4f} m"
        )
    return {"surface_xy_error_m": error, "surface_height_above_pad_m": float(delta[2])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--instruction", required=True)
    p.add_argument("--turns", type=int, default=8, choices=range(1, 33))
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rclpy.init()
    node = rclpy.create_node("waffle_free_instruction")
    hw = Hardware(node)
    worker = PolicyWorker(args.output)
    history = []
    state = None
    stop = "interrupted"
    try:
        stop = "budget_exhausted"
        for turn in range(args.turns):
            before, image = hw.observe(timeout=10)
            image.save(args.output / f"observation-{turn:02d}.png")
            item = plan(args.instruction, before, history, system=SYSTEM_HW)
            try:
                evidence = perform(hw, worker, item, history, args.output)
            except (ValueError, KeyError, TypeError) as exc:
                evidence = {"error": str(exc)}
            state, image = hw.observe()
            row = dict(
                turn=turn, decision=item, before=before, after=state, evidence=evidence
            )
            with (args.output / "turns.jsonl").open("a") as log:
                log.write(json.dumps(row, ensure_ascii=False) + "\n")
            print("TURN", turn, item["action"], evidence, flush=True)
            history.append(dict(turn=turn, decision=item, result=evidence))
            if "error" not in evidence and item["action"] in ("finish", "blocked"):
                stop = "model_finished" if item["action"] == "finish" else "blocked"
                break
        image.save(args.output / "final.png")
    except BaseException as exc:
        stop = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        worker.close()
        (args.output / "outcome.json").write_text(
            json.dumps(
                dict(
                    backend="hardware",
                    instruction=args.instruction,
                    stop=stop,
                    state=state,
                    vla_inferences=worker.calls,
                    completed_turns=len(history),
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
