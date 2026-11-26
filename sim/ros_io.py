"""Lyrical standard-message transport for the Isaac Sim 6.1 standalone process."""
import math
import numpy as np
import omni.physx
from pxr import Gf
import rclpy
from builtin_interfaces.msg import Time
from rclpy.qos import qos_profile_sensor_data
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import CameraInfo, Image, JointState, LaserScan


class RosIO:
    def __init__(self, body, cameras, scan_transform):
        self.body, self.cameras, self.scan_transform = body, cameras, scan_transform
        rclpy.init()
        self.node = rclpy.create_node('isaac_waffle')
        self.clock = self.node.create_publisher(Clock,'/clock',10)
        self.feedback = self.node.create_publisher(JointState,'/isaac/joint_states',10)
        self.scan = self.node.create_publisher(LaserScan,'/scan',qos_profile_sensor_data)
        self.images, self.infos = {}, {}
        for stream in cameras:
            prefix = '/camera/'+stream+'/'
            topic = 'image_raw' if stream in ('color','aligned_depth_to_color') else 'image_rect_raw'
            self.images[stream] = self.node.create_publisher(Image,prefix+topic,5)
            self.infos[stream] = self.node.create_publisher(CameraInfo,prefix+'camera_info',5)
        self.node.create_subscription(JointState,'/isaac/arm_commands',self.arm,1)
        self.node.create_subscription(JointState,'/isaac/wheel_commands',self.drive,1)
        self.query = omni.physx.get_physx_scene_query_interface()
        self.last_scan = -1.
        self.last_drive = -1.
        self.now = 0.
        self.wheels = body.get_dof_indices(['wheel_left_joint','wheel_right_joint'])
        # PhysX reports continuous wheel joints wrapped to [-2pi, 2pi]. diff_drive_controller integrates
        # positions, so each 4pi jump would add about 82 degrees of false yaw. Publish unwrapped angles.
        self.wheel_ids = [body.dof_names.index(n) for n in ('wheel_left_joint','wheel_right_joint')]
        self.wheel_raw = self.wheel_angle = None

    def arm(self, msg):
        if msg.name and len(msg.position)==len(msg.name) and np.isfinite(msg.position).all():
            self.body.set_dof_position_targets(list(msg.position),dof_indices=self.body.get_dof_indices(msg.name))

    def drive(self, msg):
        if msg.name and len(msg.velocity)==len(msg.name) and np.isfinite(msg.velocity).all():
            self.body.set_dof_velocity_targets(list(msg.velocity),dof_indices=self.body.get_dof_indices(msg.name))
            self.last_drive = self.now

    def laser(self,stamp):
        pos,quat = self.body.get_world_poses()
        w,x,y,z = map(float,quat.numpy()[0])
        pose = Gf.Matrix4d(1).SetRotate(Gf.Quatd(w,Gf.Vec3d(x,y,z)))
        pose.SetTranslateOnly(Gf.Vec3d(*map(float,pos.numpy()[0])))
        sensor = self.scan_transform * pose
        origin = sensor.ExtractTranslation()
        scan = LaserScan()
        scan.header.stamp,scan.header.frame_id = stamp,'base_scan'
        scan.angle_min,scan.angle_increment = -math.pi,math.tau/400
        scan.angle_max = scan.angle_min+399*scan.angle_increment
        scan.range_min,scan.range_max,scan.scan_time = .05,12.,.1
        ranges = []
        for i in range(400):
            a = scan.angle_min+i*scan.angle_increment
            direction = sensor.TransformDir(Gf.Vec3d(math.cos(a),math.sin(a),0))
            start = origin + scan.range_min*direction
            hit = self.query.raycast_closest(tuple(start),tuple(direction),scan.range_max-scan.range_min)
            ranges.append(hit['distance']+scan.range_min if hit['hit'] else math.inf)
        scan.ranges = ranges
        self.scan.publish(scan)

    def camera(self,stream,stamp):
        _,annotator,f = self.cameras[stream]
        data = annotator.get_data()
        if data is None or not data.size:
            return
        if stream=='color':
            pixels,encoding = np.ascontiguousarray(data[:,:,:3],dtype=np.uint8),'rgb8'
        elif stream.startswith('infra'):
            gray = np.mean(data[:,:,:3],axis=2).astype(np.uint8)
            pixels,encoding = np.ascontiguousarray(gray),'mono8'
        elif stream=='aligned_depth_to_color':
            valid = np.isfinite(data) & (data>0) & (data<65.535)
            pixels,encoding = np.ascontiguousarray(np.where(valid,data,0)*1000,dtype='<u2'),'16UC1'
        else:
            pixels,encoding = np.ascontiguousarray(data,dtype='<f4'),'32FC1'
        h,w = pixels.shape[:2]
        image = Image(height=h,width=w,encoding=encoding,step=pixels.strides[0],data=pixels.tobytes())
        image.header.stamp,image.header.frame_id = stamp,'camera_'+('color' if stream=='aligned_depth_to_color' else stream)+'_optical_frame'
        info = CameraInfo(header=image.header,width=w,height=h,distortion_model='plumb_bob',
                          d=[0.]*5,k=[f,0.,w/2,0.,f,h/2,0.,0.,1.],
                          r=[1.,0.,0.,0.,1.,0.,0.,0.,1.],
                          p=[f,0.,w/2,-.05*f if stream=='infra2' else 0.,0.,f,h/2,0.,0.,0.,1.,0.])
        self.images[stream].publish(image)
        self.infos[stream].publish(info)

    def step(self,now,tick):
        self.now = now
        sec,nsec = divmod(round(now*1e9),10**9)
        stamp = Time(sec=sec,nanosec=nsec)
        self.clock.publish(Clock(clock=stamp))
        for _ in range(2):
            rclpy.spin_once(self.node,timeout_sec=0.)
        if now-self.last_drive > .5:
            self.body.set_dof_velocity_targets([0.,0.],dof_indices=self.wheels)
        positions = np.array(self.body.get_dof_positions().numpy()[0],dtype=float)
        raw = positions[self.wheel_ids]
        if self.wheel_raw is None:
            self.wheel_angle = raw.copy()
        else:
            delta = raw-self.wheel_raw
            self.wheel_angle += delta-np.round(delta/math.tau)*math.tau
        self.wheel_raw = raw
        positions[self.wheel_ids] = self.wheel_angle
        joints = JointState(name=self.body.dof_names,position=positions.tolist(),
                            velocity=self.body.get_dof_velocities().numpy()[0].tolist())
        joints.header.stamp = stamp
        self.feedback.publish(joints)
        if now-self.last_scan >= .0999:
            self.laser(stamp)
            self.last_scan = now
        if tick%2 == 0:
            for stream in self.cameras:
                self.camera(stream,stamp)

    def close(self):
        self.node.destroy_node()
        rclpy.try_shutdown()
