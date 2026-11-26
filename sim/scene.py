"""Build an Isaac Sim 6.1 robot USD and run the ROS camera, lidar and joint graphs."""
import argparse
import math
from pathlib import Path
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('urdf', type=Path)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--stereo', action='store_true', help='Render the two D435 IR viewpoints for stereo cuVSLAM')
parser.add_argument('--headless', action='store_true')
parser.add_argument('--steps', type=int, default=0, help='Stop after this many frames (0 runs continuously)')
args = parser.parse_args()

from isaacsim import SimulationApp
app = SimulationApp({'headless': args.headless})
import omni.replicator.core as rep
import omni.kit.app
import omni.timeline
import omni.usd
from pxr import Gf, PhysxSchema, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, UsdShade
from isaacsim.asset.importer.urdf import URDFImporter, URDFImporterConfig
from isaacsim.core.experimental.prims import Articulation
from ros_io import RosIO


def fixed_transform(frame):
    joints = {j.find('child').get('link'): j for j in ET.parse(args.urdf).findall('joint')}
    matrix = Gf.Matrix4d(1)
    while frame in joints:
        joint = joints[frame]
        assert joint.get('type') == 'fixed'
        origin = joint.find('origin')
        xyz = [float(v) for v in origin.get('xyz','0 0 0').split()]
        r,p,y = [math.degrees(float(v)) for v in origin.get('rpy','0 0 0').split()]
        transform = Gf.Matrix4d(1)
        rotation = (Gf.Rotation(Gf.Vec3d.XAxis(), r) * Gf.Rotation(Gf.Vec3d.YAxis(), p)
                    * Gf.Rotation(Gf.Vec3d.ZAxis(), y))
        transform.SetRotate(rotation)
        transform.SetTranslateOnly(Gf.Vec3d(*xyz))
        matrix *= transform
        frame = joint.find('parent').get('link')
    return matrix


def contact_material(stage, name, friction, combine):
    material = UsdShade.Material.Define(stage, '/World/PhysicsMaterials/'+name)
    physics = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
    physics.CreateStaticFrictionAttr(friction)
    physics.CreateDynamicFrictionAttr(friction)
    physics.CreateRestitutionAttr(0.)
    PhysxSchema.PhysxMaterialAPI.Apply(material.GetPrim()).CreateFrictionCombineModeAttr(combine)
    return material


def bind_contacts(stage, prims, base):
    # The real casters are ball casters, but the URDF models them as boxes that drag on the floor
    # and make the wheels slip while turning. Give tires grip and make the low base contacts frictionless.
    tire = contact_material(stage, 'tire', 1., 'max')
    caster = contact_material(stage, 'caster', 0., 'min')
    bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_, UsdGeom.Tokens.guide])
    for prim in prims:
        if not prim.HasAPI(UsdPhysics.CollisionAPI):
            continue
        parent = prim.GetParent()
        if parent.GetName().startswith('wheel_'):
            material = tire
        elif str(parent.GetPath()) == base and bounds.ComputeWorldBound(prim).ComputeAlignedRange().GetMin()[2] < .01:
            material = caster
        else:
            continue
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(material, UsdShade.Tokens.weakerThanDescendants, 'physics')


def camera_reader(stage, base, stream):
    frame = f'camera_{stream}_optical_frame'
    cam = UsdGeom.Camera.Define(stage, base+'/sensor_'+stream)
    # USD camera looks down -Z with +Y up. ROS optical convention is +Z forward and +Y down.
    flip = Gf.Matrix4d(1).SetRotate(Gf.Rotation(Gf.Vec3d.XAxis(),180))
    cam.AddTransformOp().Set(flip*fixed_transform(frame))
    cam.CreateClippingRangeAttr(Gf.Vec2f(.01, 100.0))
    cam.CreateHorizontalApertureAttr(20.0)
    cam.CreateVerticalApertureAttr(15.0)
    cam.CreateFocalLengthAttr(14.3 if stream=='color' else 10.5)
    product = rep.create.render_product(str(cam.GetPath()), (640,480))
    annotator = rep.AnnotatorRegistry.get_annotator('distance_to_image_plane' if stream=='depth' else 'rgb')
    annotator.attach(product)
    return product, annotator, float(cam.GetFocalLengthAttr().Get())*640/20


def build():
    args.output.mkdir(parents=True, exist_ok=True)
    robot_usd = URDFImporter(URDFImporterConfig(
        urdf_path=str(args.urdf.resolve()), usd_path=str(args.output.resolve()/'converted'),
        merge_fixed_joints=True, fix_base=False, run_asset_transformer=False,
        joint_target_type={'wheel_.*':'velocity','joint[1-4]':'position','gripper_left_joint':'position'},
        override_joint_stiffness={'wheel_.*':0.,'joint[1-4]':20.,'gripper_left_joint':150.},
        override_joint_damping={'wheel_.*':1.,'joint[1-4]':1.,'gripper_left_joint':5.})).import_urdf()
    asset = args.output.resolve()/'waffle.usda'
    Sdf.Layer.FindOrOpen(robot_usd).Export(str(asset))
    print('Isaac Lab robot asset:',asset,flush=True)
    ctx = omni.usd.get_context()
    ctx.new_stage()
    stage = ctx.get_stage()
    UsdGeom.SetStageMetersPerUnit(stage,1)
    UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z)
    world = UsdGeom.Xform.Define(stage,'/World')
    stage.SetDefaultPrim(world.GetPrim())
    robot = stage.DefinePrim('/World/Robot','Xform')
    robot.GetReferences().AddReference(str(asset))
    prims = list(Usd.PrimRange(robot))
    root = next(p for p in prims if p.HasAPI(UsdPhysics.ArticulationRootAPI))
    base = next(p for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI) and p.GetName()=='base_footprint')
    base = str(base.GetPath())
    UsdPhysics.Scene.Define(stage,'/World/Physics')
    bind_contacts(stage, prims, base)
    UsdLux.DomeLight.Define(stage,'/World/Light').CreateIntensityAttr(800)
    boxes = [('Floor',(0,0,-.05),(6,6,.1)),('Back',(-2,0,.22),(.1,4,.44)),
             ('Front',(2,0,.22),(.1,4,.44)),('Left',(0,2,.22),(4,.1,.44)),
             ('Right',(0,-2,.22),(4,.1,.44)),('Block',(1,.4,.18),(.4,.3,.36))]
    for name, xyz, size in boxes:
        box = UsdGeom.Cube.Define(stage,'/World/'+name)
        box.CreateSizeAttr(1)
        box.AddTranslateOp().Set(Gf.Vec3d(*xyz))
        box.AddScaleOp().Set(Gf.Vec3f(*size))
        UsdPhysics.CollisionAPI.Apply(box.GetPrim())
    cameras = {s: camera_reader(stage,base,s) for s in (['color','depth','infra1','infra2'] if args.stereo else ['color','depth'])}
    color_product,_,f = cameras['color']
    aligned = rep.AnnotatorRegistry.get_annotator('distance_to_image_plane')
    aligned.attach(color_product)
    cameras['aligned_depth_to_color'] = (color_product,aligned,f)
    stage.GetRootLayer().Export(str(args.output.resolve()/'scene.usda'))
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    for _ in range(5):
        app.update()
    body = Articulation(str(root.GetPath()))
    bridge = RosIO(body, cameras, fixed_transform('base_scan'))
    count = 0
    try:
        while app.is_running() and (args.steps == 0 or count < args.steps):
            app.update()
            bridge.step(timeline.get_current_time(),count)
            count += 1
    finally:
        bridge.close()


try:
    build()
except Exception:
    import traceback
    traceback.print_exc()
    raise
finally:
    app.close()
