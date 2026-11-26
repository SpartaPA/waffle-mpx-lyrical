"""Run a Korean request through a local LLM and the Isaac photo or arm policy."""
import argparse
import json
import math
import os
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = "qwen2.5:1.5b"
SYSTEM = """Translate the Korean robot request into one intent. photo means conditional camera capture; convert its distance from centimeters or meters to meters. drive means move the base straight forward by the stated distance, convert it to meters. approach means move forward until the object in front is at the stated distance, convert it to meters. pick_red / pick_blue mean pick the named cube and place it on the green square. For unsupported goals, multiple actions, missing color for picking, or missing photo threshold choose unsupported. Examples: '20센티미터 안이면 사진 찍어줘' -> photo with meters 0.2; '앞으로 10센티미터 가줘' -> drive with meters 0.1; '앞 물체와 30센티미터가 될 때까지 다가가줘' -> approach with meters 0.3; '파란 블록을 초록 칸에 놓아줘' -> pick_blue. For pick or unsupported use meters 0."""
PHOTO_WORDS = ("사진","촬영","찍")
UNTIL_WORDS = ("까지","될때","될 때")
MOVE_WORDS = ("가까이","다가","접근","가 줘","가줘","가 주","가주","이동","전진")
def check(sentence,plan):
    """Reject intents whose key words are missing from the sentence; the 1.5B model confuses distance phrases."""
    text=sentence.replace(" ","")
    def has(words):return any(w.replace(" ","") in text for w in words)
    approach=has(UNTIL_WORDS) and has(MOVE_WORDS) and not has(PHOTO_WORDS)
    if plan["intent"]=="photo" and not has(PHOTO_WORDS):
        plan=dict(plan,intent="approach" if approach else "unsupported")
    elif plan["intent"]=="drive" and approach:
        plan=dict(plan,intent="approach")
    elif plan["intent"]=="approach" and not approach:
        plan=dict(plan,intent="unsupported")
    elif plan["intent"] in ("pick_red","pick_blue"):
        colors=[c for c,words in (("red",("빨간","빨강","red")),("blue",("파란","파랑","blue"))) if has(words)]
        plan=dict(plan,intent="pick_"+colors[0] if len(colors)==1 else "unsupported")
    return plan
def interpret(sentence):
    schema = {"type":"object","properties":{"intent":{"type":"string","enum":["photo","pick_red","pick_blue","drive","approach","unsupported"]},"meters":{"type":"number"}},"required":["intent","meters"]}
    payload = {"model":MODEL,"stream":False,"keep_alive":0,"format":schema,"options":{"temperature":0,"num_predict":64,"num_ctx":2048},"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":sentence}]}
    req=Request("http://127.0.0.1:11434/api/chat",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=120) as response:
        plan=json.loads(json.load(response)["message"]["content"])
    if plan.get("intent") not in schema["properties"]["intent"]["enum"] or type(plan.get("meters")) not in (float,int):
        raise ValueError("Invalid model output")
    return check(sentence,plan)

def photo(limit,output,wait_s=12):
    import rclpy
    from sensor_msgs.msg import Image,LaserScan
    from rclpy.qos import qos_profile_sensor_data
    rclpy.init()
    node=rclpy.create_node("lesson13_model_case")
    latest,count={},{"rgb":0,"scan":0}
    def keep(key):
        def store(m):
            latest[key]=(m,time.monotonic())
            count[key]+=1
        return store
    node.create_subscription(Image,"/camera/color/image_raw",keep("rgb"),qos_profile_sensor_data)
    node.create_subscription(LaserScan,"/scan",keep("scan"),qos_profile_sensor_data)
    try:
        # Pair by arrival time, not header stamps: the D435 and LDS-03 stamp with different clocks on the robot.
        deadline=time.monotonic()+wait_s
        while time.monotonic()<deadline:
            rclpy.spin_once(node,timeout_sec=.1)
            if len(latest)==2 and abs(latest["rgb"][1]-latest["scan"][1])<=.3:break
        else:raise RuntimeError(f"Timed out waiting for camera and lidar samples ({wait_s:g} s): "
                                f"/camera/color/image_raw {count['rgb']} msgs, /scan {count['scan']} msgs received")
        rgb,scan=latest["rgb"][0],latest["scan"][0]
    finally:
        node.destroy_node()
        rclpy.shutdown()
    hits=[x for x in scan.ranges if math.isfinite(x) and scan.range_min<=x<=scan.range_max]
    if not hits or rgb.encoding!="rgb8":raise RuntimeError("Invalid sensor observation")
    from PIL import Image as PILImage
    img=PILImage.frombytes("RGB",(rgb.width,rgb.height),bytes(rgb.data),"raw","RGB",rgb.step)
    with tempfile.TemporaryDirectory() as temp:
        observation=Path(temp)/"rgb.png"
        img.save(observation)
        env=os.environ.copy()
        env["PYTHONPATH"]=env.get("WAFFLE_LEARNING_DEPS",str(ROOT.parent/".learning-deps"))
        lab=os.environ.get("ISAAC_LAB_PYTHON",str(Path.home()/"IsaacLab/.venv/bin/python"))
        result=subprocess.check_output([lab,str(HERE/"photo_policy.py"),str(observation),str(min(hits)),str(limit)],env=env,text=True)
    decision=json.loads(result)
    if decision["action"]=="capture": img.save(output/"photo.png")
    return dict(distance_m=min(hits),threshold_m=limit,**decision)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--scene",type=Path,default=Path(os.environ.get("WAFFLE_SCENE", ROOT.parent/"simulation/scene.usda")))
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--show",action="store_true")
    p.add_argument("--hardware",action="store_true",help="Drive the real robot through /cmd_vel and /joint_states")
    p.add_argument("--sensor-timeout",type=float,default=12)
    args=p.parse_args()
    sentence=input("자연어 명령 > ").strip()
    plan=interpret(sentence)
    print("LLM",json.dumps(plan,ensure_ascii=False),flush=True)
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/"request.json").write_text(json.dumps({"request":sentence,"model":MODEL,"plan":plan},ensure_ascii=False,indent=2))
    if plan["intent"]=="photo" and 0<plan["meters"]<=12:
        outcome=photo(plan["meters"],args.output,args.sensor_timeout)
    elif plan["intent"]=="drive" and 0<plan["meters"]<=.15:
        from drive_feedback import advance
        outcome=advance(plan["meters"],args.hardware)
    elif plan["intent"]=="approach" and .2<=plan["meters"]<=1.5:
        from drive_feedback import approach
        outcome=approach(plan["meters"],args.hardware)
    elif plan["intent"] in ("pick_red","pick_blue") and args.hardware:
        raise SystemExit("블록 집기는 Isaac Sim에서만 실행합니다. --hardware 없이 실행하세요.")
    elif plan["intent"] in ("pick_red","pick_blue"):
        target=plan["intent"].split("_")[1]
        sim=os.environ.get("ISAAC_SIM_PYTHON",str(Path.home()/"isaacsim6_venv/bin/python"))
        ckpt=ROOT/"learning/checkpoints"
        run=args.output/"physics"
        cmd=[sim,str(ROOT/"sim/evaluate_pick_place.py"),str(args.scene.resolve()),str(ckpt/"waffle-color-73.npz"),str(run),"--controller","color","--parent-vla",str(ckpt/"waffle-hf-vla.pt"),"--target",target,"--layouts","1","--seed","8601","--decisions","92","--record-frames"]
        if args.show:cmd.append("--show")
        print("VLA → Isaac Sim · "+target+" · 92개 목표를 실행합니다.",flush=True)
        with (args.output/"isaac.log").open("w") as log:
            subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
        outcome=json.loads((run/"results.json").read_text())["results"][0]
    else: raise SystemExit("지원하지 않는 작업 또는 거리입니다.")
    (args.output/"outcome.json").write_text(json.dumps(outcome,ensure_ascii=False,indent=2))
    print("RESULT",json.dumps(outcome,ensure_ascii=False))
if __name__=="__main__":main()
