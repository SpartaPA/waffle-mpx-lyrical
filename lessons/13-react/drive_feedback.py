"""Move the base forward with wheel-encoder or lidar feedback in Isaac Sim or on the robot."""
import math
import time
import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState, LaserScan

NAMES = ["wheel_left_joint", "wheel_right_joint"]
RADIUS = .033
SPEED = .033          # m/s, 1 rad/s at the wheels
FRONT = math.radians(10)


class Base:
    """Isaac takes wheel velocities on /isaac/wheel_commands; the robot takes /cmd_vel through diff_drive_controller."""
    def __init__(self, node, hardware):
        self.node, self.hardware = node, hardware
        if hardware:
            from geometry_msgs.msg import TwistStamped
            self.msg = TwistStamped
            self.pub = node.create_publisher(TwistStamped, "/cmd_vel", 1)
        else:
            self.pub = node.create_publisher(JointState, "/isaac/wheel_commands", 1)
        self.wheels = []
        def observe(msg):
            if all(name in msg.name for name in NAMES):
                self.wheels[:] = [msg.position[msg.name.index(name)] for name in NAMES]
        node.create_subscription(JointState, "/joint_states" if hardware else "/isaac/joint_states", observe, 1)

    def send(self, speed):
        if self.hardware:
            msg = self.msg()
            msg.header.stamp = self.node.get_clock().now().to_msg()
            msg.twist.linear.x = speed
        else:
            msg = JointState(name=NAMES, velocity=[speed/RADIUS]*2)
        self.pub.publish(msg)

    def stop(self):
        for _ in range(4):
            self.send(0.)
            rclpy.spin_once(self.node, timeout_sec=.05)


def front_range(scan):
    """Nearest valid return within +-10 degrees of the base_scan x axis."""
    hits = [r for i, r in enumerate(scan.ranges)
            if abs(math.remainder(scan.angle_min+i*scan.angle_increment, math.tau)) <= FRONT
            and math.isfinite(r) and scan.range_min <= r <= scan.range_max]
    return min(hits) if hits else math.inf


def wait(node, ready, end, what):
    while not ready():
        if time.monotonic() > end:
            raise TimeoutError(what+" unavailable")
        rclpy.spin_once(node, timeout_sec=.1)


def advance(distance, hardware=False):
    rclpy.init()
    node = rclpy.create_node("lesson13_drive")
    base = Base(node, hardware)
    try:
        end = time.monotonic()+40
        wait(node, lambda: base.wheels and base.pub.get_subscription_count(), end, "Wheel feedback")
        start = base.wheels.copy()
        while time.monotonic() < end:
            delta = [(p-q)*RADIUS for p, q in zip(base.wheels, start)]
            if min(delta) >= distance:
                return {"action":"drive","requested_m":distance,"left_encoder_m":delta[0],"right_encoder_m":delta[1]}
            base.send(SPEED)
            rclpy.spin_once(node, timeout_sec=.1)
        raise TimeoutError("Requested wheel travel not reached")
    finally:
        base.stop()
        node.destroy_node()
        rclpy.shutdown()


def approach(target, hardware=False, max_travel=1.):
    """Drive forward until the front lidar range is at most target meters."""
    rclpy.init()
    node = rclpy.create_node("lesson13_approach")
    base = Base(node, hardware)
    scan = {}
    node.create_subscription(LaserScan, "/scan", lambda m: scan.update(m=m, t=time.monotonic()), qos_profile_sensor_data)
    try:
        wait(node, lambda: "m" in scan and base.wheels and base.pub.get_subscription_count(), time.monotonic()+40, "Lidar or wheel feedback")
        initial = front_range(scan["m"])
        if not math.isfinite(initial):
            raise RuntimeError("No lidar return in front of the robot")
        if initial-target > max_travel:
            raise RuntimeError(f"Front object is {initial:.2f} m away; more than {max_travel:g} m of travel is required")
        start = base.wheels.copy()
        best, moved = initial, time.monotonic()
        while True:
            front = front_range(scan["m"])
            travel = min((p-q)*RADIUS for p, q in zip(base.wheels, start))
            if front <= target:
                return {"action":"approach","target_m":target,"initial_front_m":initial,"front_m":front,"encoder_m":travel}
            if time.monotonic()-scan["t"] > .5:
                raise TimeoutError("Lidar stopped publishing")
            if front < best-.01:
                best, moved = front, time.monotonic()
            # Stop when the front range has not shrunk for 5 s or the travel cap is used up.
            if time.monotonic()-moved > 5 or travel > max_travel:
                raise TimeoutError(f"Target distance not reached: front {front:.3f} m after {travel:.3f} m of travel")
            base.send(SPEED)
            rclpy.spin_once(node, timeout_sec=.05)
    finally:
        base.stop()
        node.destroy_node()
        rclpy.shutdown()
