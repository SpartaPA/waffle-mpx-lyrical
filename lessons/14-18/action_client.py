"""Exercise ROS 2 FollowJointTrajectory against the course simulation controller."""
import argparse
import json
import math
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint


def wait(node, future, timeout):
    rclpy.spin_until_future_complete(node, future, timeout_sec=timeout)
    if not future.done():
        raise TimeoutError("result.unknown")
    return future.result()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cancel',action='store_true')
    args=p.parse_args()
    rclpy.init()
    node=rclpy.create_node('lesson14_action_client')
    current={}
    def update(msg):
        current.update(zip(msg.name,msg.position))
    node.create_subscription(JointState,'joint_states',update,qos_profile_sensor_data)
    client=ActionClient(node,FollowJointTrajectory,'arm_controller/follow_joint_trajectory')
    events=[]
    try:
        if not client.wait_for_server(timeout_sec=8): raise TimeoutError("server missing")
        names=[f'joint{i}' for i in range(1,5)]
        end=time.monotonic()+5
        while not all(n in current for n in names) and time.monotonic()<end:
            rclpy.spin_once(node,timeout_sec=.1)
        start=[current[n] for n in names]
        target=start.copy()
        target[0]=.12 if start[0]<=0 else -.12
        if not all(map(math.isfinite,target)): raise ValueError("non-finite angle")
        goal=FollowJointTrajectory.Goal()
        goal.trajectory.joint_names=names
        goal.trajectory.points=[JointTrajectoryPoint(positions=target,time_from_start=Duration(sec=3))]
        feedback=[]
        def record(msg):
            feedback.append(list(msg.feedback.actual.positions))
        handle=wait(node,client.send_goal_async(goal,feedback_callback=record),5)
        if not handle.accepted: raise RuntimeError("rejected")
        events.append('accepted')
        done=handle.get_result_async()
        if args.cancel:
            end=time.monotonic()+1
            while time.monotonic()<end and not done.done(): rclpy.spin_once(node,timeout_sec=.05)
            response=wait(node,handle.cancel_goal_async(),3)
            events.append('cancel_accepted' if response.goals_canceling else 'cancel_rejected')
        result=wait(node,done,10)
        expected=GoalStatus.STATUS_CANCELED if args.cancel else GoalStatus.STATUS_SUCCEEDED
        print(json.dumps(dict(events=events,status=result.status,feedback_count=len(feedback),start=start,target=target,
                              final=[current[n] for n in names],error_code=result.result.error_code)))
        if result.status!=expected or not feedback: raise RuntimeError("unexpected lifecycle")
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
if __name__=='__main__': main()
