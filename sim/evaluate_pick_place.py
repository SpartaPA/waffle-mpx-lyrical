"""Evaluate a frozen HF policy using simulated D435 RGB and physical cube poses."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('scene', type=Path)
parser.add_argument('checkpoint', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--varied-poses', action='store_true',
                    help='Sample arm start angles and tabletop positions independently of the controller')
parser.add_argument('--layouts', type=int, default=4)
parser.add_argument('--decisions', type=int, default=48)
parser.add_argument('--seed', type=int, default=41)
parser.add_argument('--controller', choices=['vla','teacher','color','baseline'], default='vla')
parser.add_argument('--parent-vla',type=Path,help='Original HF VLA checkpoint used by the color adapter')
parser.add_argument('--target', choices=['red','blue'], help='Run only the requested cube color')
parser.add_argument('--show', action='store_true', help='Open the Isaac Sim viewport')
parser.add_argument('--capture-rgbd', action='store_true', help='Save the starting aligned depth and optical-to-world calibration for the grounding lab')
parser.add_argument('--record-frames', action='store_true', help='Save the RGB frame at each policy step')
parser.add_argument('--free-instruction', help='Use a live instruction and observation loop on this scene')
parser.add_argument('--mirror-layout', action='store_true', help='Reflect free-instruction cube positions around y=0.010 m')
parser.add_argument('--turns', type=int, default=8)
args = parser.parse_args()
if args.varied_poses and args.free_instruction:
    parser.error('--varied-poses is for trajectory training and evaluation')
if args.free_instruction and (args.controller != 'color' or not 1 <= args.turns <= 32):
    parser.error('Free instructions require the color controller and 1 to 32 turns')
if args.controller == 'color' and args.parent_vla is None:
    parser.error('--controller color requires --parent-vla')
if min(args.layouts, args.decisions) < 1:
    parser.error('layouts and decisions must be positive')
args.output = args.output.resolve()
args.output.mkdir(parents=True, exist_ok=False)
root = Path(__file__).resolve().parents[1]
from isaacsim import SimulationApp
app = SimulationApp({'headless': not args.show, 'width': 640, 'height': 480})
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from isaacsim.core.experimental.prims import Articulation, RigidPrim
from PIL import Image
from pxr import Gf, UsdGeom, UsdPhysics

sys.path.insert(0, str(root / 'learning'))
from actions import HIGH, JOINTS, LOW

TABLE = .040
SIDE = .020
GOAL = np.array([.254, .008])
PAD = .052
COLORS = {'red': (.90,.025,.025), 'blue': (.015,.06,.95)}
DT = .25


def box(stage, name, xyz, size, color, dynamic=False):
    cube = UsdGeom.Cube.Define(stage, '/World/Eval' + name)
    cube.CreateSizeAttr(1.)
    cube.AddTranslateOp().Set(Gf.Vec3d(*xyz))
    cube.AddScaleOp().Set(Gf.Vec3f(*size))
    cube.CreateDisplayColorAttr([Gf.Vec3f(*color)])
    UsdPhysics.CollisionAPI.Apply(cube.GetPrim())
    if dynamic:
        UsdPhysics.RigidBodyAPI.Apply(cube.GetPrim())
        UsdPhysics.MassAPI.Apply(cube.GetPrim()).CreateMassAttr(.008)
    return str(cube.GetPath())


def position(body):
    return body.get_world_poses()[0].numpy()[0].astype(float)


def fingertips(fingers):
    out = []
    for finger in fingers:
        p, q = finger.get_world_poses()
        w, x, y, z = q.numpy()[0]
        axis = np.array([1-2*(y*y+z*z), 2*(x*y+w*z), 2*(x*z-w*y)])
        out.append(p.numpy()[0] + .0443*axis)
    return np.mean(out, axis=0)


def layouts():
    rng = np.random.default_rng(args.seed)
    for index in range(args.layouts):
        y = rng.uniform(.020, .026) if args.controller == "vla" else rng.uniform(.032,.037)
        sign = 1 if index % 2 else -1
        xs = rng.uniform(.202,.221,2)
        if args.varied_poses:
            y = rng.uniform(.028,.041)
            xs = rng.uniform(.204,.226,2)
        elif args.controller == 'teacher':
            xs = rng.uniform(.202,.211,2) + rng.integers(0,2,2)*.017
        elif args.controller in ('color','baseline'):
            xs = rng.uniform(.213,.217,2)
        yield {c: np.array([x, s*y+.010, TABLE+SIDE/2+.002])
               for c,s,x in zip(COLORS,(sign,-sign),xs)}



def inspect_pose(cubes, fingers):
    return {c: position(b) for c, b in cubes.items()}, fingertips(fingers)


def predict(worker, frame_path, state, instruction, continuous=False):
    observation = dict(rgb=str(frame_path), state=state, instruction=instruction, continuous=continuous)
    worker.stdin.write(json.dumps(observation)+'\n')
    worker.stdin.flush()
    response = worker.stdout.readline()
    if not response:
        raise RuntimeError('Policy process exited before returning an action')
    result = json.loads(response)
    if isinstance(result, dict) and "error" in result:
        raise ValueError(result["error"])
    return np.array(result)


def run(worker):
    ctx = omni.usd.get_context()
    if not ctx.open_stage(str(args.scene.resolve())):
        raise RuntimeError('Could not open Isaac scene')
    stage = ctx.get_stage()
    prims = list(stage.Traverse())
    robot_root = next(p for p in prims if p.HasAPI(UsdPhysics.ArticulationRootAPI))
    camera = next(p for p in prims if p.GetName() == 'sensor_color')
    UsdGeom.Camera(camera).CreateClippingRangeAttr(Gf.Vec2f(.01,100.))
    box(stage, 'Table', (.237,0,TABLE/2), (.158,.17,TABLE), (.38,.38,.38))
    box(stage, 'Goal', (*GOAL,TABLE+.0005), (PAD,PAD,.001), (.03,.85,.08))
    paths = {c: box(stage, c, (.21,.025 if c=='red' else -.025,TABLE+.014),
                    (SIDE,)*3, color, True) for c,color in COLORS.items()}
    if args.controller != 'vla':
        # Removable high-friction fingertip liners for the 20 mm blocks.
        from pxr import UsdShade
        material = UsdShade.Material.Define(stage,'/World/FingerRubber')
        friction = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
        friction.CreateStaticFrictionAttr(1.2)
        friction.CreateDynamicFrictionAttr(1.0)
        for side, sign in [('left',1),('right',-1)]:
            link = next(p for p in prims if p.GetName()==f'gripper_{side}_link' and p.HasAPI(UsdPhysics.RigidBodyAPI))
            pad = UsdGeom.Cube.Define(stage,str(link.GetPath())+'/FingerPad')
            pad.CreateSizeAttr(1.)
            pad.AddTranslateOp().Set(Gf.Vec3d(.055,-sign*.002,0))
            pad.AddScaleOp().Set(Gf.Vec3f(.021,.016,.016))
            pad.CreateDisplayColorAttr([Gf.Vec3f(.12)])
            UsdPhysics.CollisionAPI.Apply(pad.GetPrim())
            UsdShade.MaterialBindingAPI.Apply(pad.GetPrim()).Bind(material,materialPurpose='physics')
        for joint in prims:
            if joint.IsA(UsdPhysics.RevoluteJoint) and joint.GetName() in JOINTS[:4]:
                drive = UsdPhysics.DriveAPI.Apply(joint,'angular')
                # USD angular drive coefficients are specified per degree.
                drive.CreateStiffnessAttr(1.75)
                drive.CreateDampingAttr(.085)
        # The importer supplies a Newton mimic relation, but separate PhysX DOFs.
        for j in prims:
            if j.GetName() in ('gripper_left_joint','gripper_right_joint') and j.IsA(UsdPhysics.PrismaticJoint):
                drive = UsdPhysics.DriveAPI.Apply(j,'linear')
                drive.CreateStiffnessAttr(1200.)
                drive.CreateDampingAttr(12.)
    product = rep.create.render_product(str(camera.GetPath()), (640,480))
    rgb = rep.AnnotatorRegistry.get_annotator('rgb')
    rgb.attach(product)
    if args.capture_rgbd:
        depth = rep.AnnotatorRegistry.get_annotator('distance_to_image_plane')
        depth.attach(product)
    clock = omni.timeline.get_timeline_interface()
    clock.set_target_framerate(60)
    clock.play()

    def advance(seconds, sample=None):
        end = clock.get_current_time()+seconds
        for _ in range(math.ceil(seconds*240)+120):
            app.update()
            if sample is not None:
                sample()
            if clock.get_current_time() >= end-1e-6:
                return
        raise RuntimeError('Physics clock did not advance')

    advance(.5)
    body = Articulation(str(robot_root.GetPath()))
    fingers = [RigidPrim(str(next(p for p in prims if p.GetName()==f'gripper_{s}_link' and
                                  p.HasAPI(UsdPhysics.RigidBodyAPI)).GetPath())) for s in ('left','right')]
    cubes = {c: RigidPrim(path) for c,path in paths.items()}
    controls = body.get_dof_indices(JOINTS)
    wheels = body.get_dof_indices(['wheel_left_joint','wheel_right_joint'])
    home_p, home_q = [v.numpy().copy() for v in body.get_world_poses()]
    home = np.zeros_like(body.get_dof_positions().numpy())
    frame_path = args.output / 'observation.png'
    results = []
    if worker and json.loads(worker.stdout.readline()) != {'ready': True}:
        raise RuntimeError('Could not initialize policy')
    if args.free_instruction:
        from instruction_loop import run_instruction
        for color, xyz in next(layouts()).items():
            if args.mirror_layout:
                xyz[1] = .020 - xyz[1]
            cubes[color].set_world_poses(xyz.tolist(), [1.,0.,0.,0.])
            cubes[color].set_velocities([0.]*3,[0.]*3)
        advance(.5)
        run_instruction(args, body, rgb, cubes, controls, wheels, advance, worker, predict, GOAL)
        return
    pose_rng = np.random.default_rng(np.random.SeedSequence([args.seed, 1]))
    for layout, starts in enumerate(layouts()):
        pose = (pose_rng.uniform([-.38,-.18,-.16,-.20,.002], [.38,.28,.20,.24,.012])
                if args.varied_poses else np.zeros(5))
        for selected in ([args.target] if args.target else COLORS):
            other = next(c for c in COLORS if c != selected)
            trial = args.output / f'{layout:02d}-{selected}'
            trial.mkdir()
            body.set_world_poses(home_p, home_q)
            body.set_velocities([0.]*3,[0.]*3)
            body.set_dof_positions(home)
            body.set_dof_velocities(home)
            if args.varied_poses:
                body.set_dof_positions(pose.tolist(),dof_indices=controls)
                right = body.get_dof_indices('gripper_right_joint')
                body.set_dof_positions([pose[-1]],dof_indices=right)
                body.set_dof_position_targets([pose[-1]],dof_indices=right)
            body.set_dof_position_targets(pose.tolist(),dof_indices=controls)
            body.set_dof_velocity_targets([0.,0.],dof_indices=wheels)
            for c,b in cubes.items():
                b.set_world_poses(starts[c].tolist(), [1.,0.,0.,0.])
                b.set_velocities([0.]*3,[0.]*3)
            advance(.5)
            start_joints = body.get_dof_positions(dof_indices=controls).numpy()[0].tolist()
            initial, _ = inspect_pose(cubes, fingers)
            if any(np.linalg.norm(initial[c] - starts[c])>.008 for c in COLORS):
                raise RuntimeError('Cube did not settle on its intended start')
            instruction = f'Pick up the {selected} cube and place it on the green square.'
            held = {c: False for c in COLORS}
            max_lift = dict.fromkeys(COLORS, 0.)
            stable = 0.
            prev = clock.get_current_time()
            def monitor():
                nonlocal prev, stable
                now = clock.get_current_time()
                poses, tip = inspect_pose(cubes, fingers)
                for c, xyz in poses.items():
                    dz = xyz[2]-initial[c][2]
                    max_lift[c] = max(max_lift[c], float(dz))
                    if dz >= .025 and np.linalg.norm(xyz-tip) <= .024:
                        held[c] = True
                xyz = poses[selected]
                linear, angular = cubes[selected].get_velocities()
                # Use the cube orientation to require its full XY footprint on the square.
                w,x,y,z = cubes[selected].get_world_poses()[1].numpy()[0]
                rx = [1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)]
                ry = [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)]
                half = .5*SIDE*np.abs([rx,ry]).sum(axis=1)
                inside = np.all(np.abs(xyz[:2]-GOAL)+half <= PAD/2)
                resting = (inside and abs(xyz[2]-(TABLE+.001+SIDE/2))<.003
                           and np.linalg.norm(linear.numpy()[0])<.012
                           and np.linalg.norm(angular.numpy()[0])<.2
                           and np.linalg.norm(tip-xyz)>.035)
                stable = stable + max(0.,now-prev) if held[selected] and resting else 0.
                prev = now
            with (trial/'trace.jsonl').open('w') as trace:
                for step in range(args.decisions):
                    pixels = np.asarray(rgb.get_data())
                    if pixels.shape[:2] != (480,640):
                        raise RuntimeError('Missing camera observation')
                    image = Image.fromarray(pixels[:,:,:3])
                    image.save(frame_path)
                    if args.record_frames:
                        image.save(trial/f'frame-{step:03d}.jpg', quality=92)
                    if args.controller == 'color' and step in (36,47,59,79):
                        image.save(trial/f'step-{step:02d}.jpg')
                    if step == 0:
                        image.save(trial/'start.png')
                        if args.capture_rgbd:
                            cam = UsdGeom.Camera(camera)
                            fx = 640 * cam.GetFocalLengthAttr().Get() / cam.GetHorizontalApertureAttr().Get()
                            # USD matrix uses row vectors; optical Y and Z oppose USD camera Y and Z.
                            transform = np.array(UsdGeom.XformCache().GetLocalToWorldTransform(camera)).T @ np.diag([1,-1,-1,1])
                            np.savez_compressed(trial/'rgbd.npz', depth_m=np.asarray(depth.get_data()),
                                                optical_to_world=transform, intrinsics=[fx,fx,320.,240.])
                        r,g,b = np.moveaxis(np.asarray(image, dtype=float),-1,0)
                        masks = [(r > 1.4*g) & (r > 1.4*b) & (r>40),
                                 (b > 1.4*r) & (b > 1.4*g) & (b>40),
                                 (g > 1.4*r) & (g > 1.4*b) & (g>40)]
                        if min(np.count_nonzero(mask) for mask in masks) < 50:
                            raise RuntimeError(f'Objects or goal missing from RGB at {trial}')
                    q = body.get_dof_positions(dof_indices=controls).numpy()[0]
                    linear,angular = body.get_velocities()
                    state = [float(linear.numpy()[0,0]),float(angular.numpy()[0,2]),*q.tolist()]
                    if args.controller == 'teacher':
                        from color_teacher import teacher_action
                        action = teacher_action(step,initial[selected],GOAL,fingertips(fingers),q)
                        image.save(trial/f'{step:03d}.jpg', quality=90)
                    elif args.controller == 'color':
                        if step == 0:
                            trajectory = predict(worker, frame_path, state, instruction)
                            if trajectory.shape != (args.decisions,7):
                                raise ValueError('Rollout horizon must equal the trained trajectory length')
                        action = trajectory[step]
                    else:
                        action = predict(worker, frame_path, state, instruction)
                    if action.shape != (7,) or not np.isfinite(action).all() or np.any(np.abs(action[:2])>1e-5):
                        raise ValueError('Expected a finite parked-base policy action')
                    limit = np.array([.35]*4+[.012])*DT
                    target = q+np.clip(np.clip(action,LOW,HIGH)[2:]-q,-limit,limit)
                    body.set_dof_position_targets(target.tolist(),dof_indices=controls)
                    if args.controller != 'vla' and 'gripper_right_joint' in body.dof_names:
                        body.set_dof_position_targets([target[-1]],dof_indices=body.get_dof_indices('gripper_right_joint'))
                    advance(DT, monitor)
                    poses, tip = inspect_pose(cubes, fingers)
                    trace.write(json.dumps(dict(step=step, time=prev, state=state, action=action.tolist(),
                        applied=target.tolist(), cubes={c:v.tolist() for c,v in poses.items()},
                        fingertips=tip.tolist(), stable_s=stable))+'\n')
                advance(.5, monitor)
            final, _ = inspect_pose(cubes, fingers)
            Image.fromarray(np.asarray(rgb.get_data())[:,:,:3]).save(trial/'end.png')
            result = dict(layout=layout, instruction=instruction, selected=selected,
                          start_joints=start_joints, initial={c:v.tolist() for c,v in initial.items()}, goal=GOAL.tolist(),
                          final={c:v.tolist() for c,v in final.items()}, max_lift_m=max_lift,
                          picked=held[selected], wrong_pick=held[other], stable_s=stable,
                          success=bool(stable>=.499 and not held[other]))
            results.append(result)
            (trial/'result.json').write_text(json.dumps(result,indent=2))
            print('PICK_PLACE_TRIAL',layout,selected,result['success'],flush=True)
    count = sum(r['success'] for r in results)
    report = dict(controller=args.controller, checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest() if args.controller != 'teacher' else None,
                  seed=args.seed, decisions=args.decisions, trials=len(results), successes=count,
                  success_rate=count/len(results), picked=sum(r['picked'] for r in results), results=results)
    (args.output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PICK_PLACE_RESULT',count,'/',len(results),flush=True)


try:
    env = os.environ.copy()
    # Kit modifies Python and shared library paths. Use the original training environment.
    env['PYTHONPATH'] = env.get('WAFFLE_LEARNING_DEPS', str(root.parent/'.learning-deps'))
    env.pop('PYTHONHOME', None)
    env['LD_LIBRARY_PATH'] = env.get('WAFFLE_WORKER_LD_LIBRARY_PATH','')
    python = env.get('ISAAC_LAB_PYTHON', str(Path.home()/'IsaacLab/.venv/bin/python'))
    if args.controller == 'teacher':
        run(None)
    else:
        command = [python,str(root/'learning/pick_place_worker.py'),str(args.checkpoint.resolve())]
        if args.controller == 'color':
            command.append(str(args.parent_vla.resolve()))
            if args.free_instruction:
                command.append("--adaptive")
        with subprocess.Popen(command,
                              stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,env=env) as worker:
            try:
                run(worker)
            finally:
                worker.stdin.close()
                worker.terminate()
except BaseException:
    import traceback
    traceback.print_exc()
    app.close(exit_code=1)
    raise
else:
    app.close()
