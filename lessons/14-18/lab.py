"""Waffle MPX course lab. Replay Isaac observations and audit each decision."""
import argparse
import json
import math
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "learning"))
from actions import HIGH, LOW, JOINTS, NAMES


class Reject(ValueError):
    pass


def contract(goal):
    if goal["version"] != "command.v1" or goal["frame"] != "world" or goal["unit"] != "m":
        raise Reject("contract.frame_unit_version")
    if not goal["request_id"] or not all(math.isfinite(v) for v in goal["xyz"]):
        raise Reject("contract.fields")
    if len(goal["xyz"]) != 3 or not all(abs(x) < 1 for x in goal["xyz"]):
        raise Reject("contract.workspace")
    if not 0 <= goal["age_s"] <= .4:
        raise Reject("contract.stale")


def ground(color, folder):
    rgb = np.asarray(Image.open(folder / "start.png").convert("RGB"), dtype=float)
    if color not in ("red", "blue"):
        raise Reject("ground.ambiguous")
    # Interpretable common color space for image pixels and the two language labels.
    axis = {"red": 0, "blue": 2}[color]
    cosine = rgb[:,:,axis] / np.maximum(np.linalg.norm(rgb, axis=2), 1.)
    mask = (cosine > .92) & (rgb[:,:,axis] > 45)
    with np.load(folder / "rgbd.npz") as d:
        z = d["depth_m"].squeeze()
        v,u = np.nonzero(mask & np.isfinite(z) & (z>0))
        if len(u)<50:
            raise Reject("ground.depth")
        fx,fy,cx,cy = d["intrinsics"]
        points = np.stack([(u-cx)*z[v,u]/fx,(v-cy)*z[v,u]/fy,z[v,u],np.ones(len(u))])
        xyz = np.median((d["optical_to_world"] @ points)[:3],axis=1)
    return dict(color=color,pixels=len(u),xyz=xyz.tolist(),frame="world",unit="m")


def adapt(values, names=NAMES):
    a = np.asarray(values,dtype=float)
    if list(names)!=list(NAMES) or a.shape!=(7,) or not np.isfinite(a).all():
        raise Reject("adapter.schema")
    if np.any(a<LOW-1e-6) or np.any(a>HIGH+1e-6) or np.any(abs(a[:2])>1e-5):
        raise Reject("adapter.limits")
    return dict(zip(JOINTS,a[2:].tolist()))


def retrieve(query, version, k=2):
    docs=json.loads((HERE/"manual.json").read_text())
    words=set(re.findall(r"\w+",query.lower()))
    ranks=[]
    for doc in docs:
        if doc["version"]!=version: continue
        score=len(words.intersection(doc["terms"]))
        if score: ranks.append((score,doc))
    return [d for _,d in sorted(ranks,key=lambda x:-x[0])[:k]]


def answer(query, version):
    docs=retrieve(query,version)
    if not docs: return dict(status="no_evidence")
    payload=dict(model="qwen2.5:7b",stream=False,format="json",options={"temperature":0,"num_gpu":0},
                 messages=[dict(role="system",content='근거에서 답을 찾아 {"quote":"원문 그대로","id":"chunk id"} JSON으로 답하세요.'),
                           dict(role="user",content=json.dumps(dict(question=query,evidence=docs),ensure_ascii=False))])
    req=Request("http://localhost:11434/api/chat",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=120) as res: result=json.loads(json.load(res)["message"]["content"])
    verified=any(d["id"]==result.get("id") and result.get("quote") and result["quote"] in d["text"] for d in docs)
    return dict(retrieved=[d["id"] for d in docs],generated=result,status="cited" if verified else "unsupported")


def ordered_nodes(graph):
    remaining={node:set(parents) for node,parents in graph.items()}
    finished=[]
    while remaining:
        ready=[node for node,parents in remaining.items() if parents.issubset(finished)]
        if not ready: raise Reject("plan.cycle")
        finished.extend(ready)
        for node in ready: del remaining[node]
    return finished


def run_case(case, guarded, folder):
    query=case["instruction"]
    colors=[c for c,word in (("red","빨간"),("blue","파란")) if word in query]
    if guarded and len(colors)!=1: raise Reject("ground.ambiguous")
    color=colors[0] if colors else "red"
    if guarded: ordered_nodes(case["graph"])
    if guarded and not retrieve(query,case["version"]): raise Reject("rag.no_evidence")
    target=ground(color,folder)
    goal=dict(version="command.v1",request_id=case["id"],frame=case["frame"],unit=case["unit"],
              xyz=target["xyz"],age_s=case["age"])
    if guarded: contract(goal)
    if case["tool_failed"]: raise Reject("tool.unavailable")
    if case["timeout"]: raise Reject("result.unknown")
    trial=HERE/"records"/color
    for line in (trial/"trace.jsonl").read_text().splitlines():
        row=json.loads(line)
        if guarded: adapt(row["applied"] if len(row["applied"])==7 else [0.,0.,*row["applied"]])
    if not json.loads((trial/"result.json").read_text())["success"]: raise Reject("physics.failed")
    return "completed"


def benchmark(folder):
    cases=json.loads((HERE/"cases.json").read_text())
    result={}
    for guarded in (False,True):
        rows=[]
        for case in cases:
            t=time.perf_counter()
            try: observed=run_case(case,guarded,folder)
            except Reject as exc: observed=str(exc)
            rows.append(dict(id=case["id"],expected=case["expected"],observed=observed,
                             correct=observed==case["expected"],ms=round((time.perf_counter()-t)*1000,2)))
        result["guarded" if guarded else "baseline"]=dict(correct=sum(r["correct"] for r in rows),total=len(rows),cases=rows)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("lesson",type=int,choices=range(14,19))
    p.add_argument("--color",choices=["red","blue"],default="blue")
    p.add_argument("--version",default="2")
    p.add_argument("--query",default="블록 운반 후 안착 조건은 무엇인가요?")
    p.add_argument("--rgbd",type=Path,default=HERE/"records"/"blue")
    args=p.parse_args()
    if args.lesson==14:
        g=dict(version="command.v1",request_id="lab14",frame="world",unit="m",xyz=[.254,.008,.051],age_s=.1)
        contract(g)
        result={"validated":g,"next":"action_client.py"}
    elif args.lesson==15: result=ground(args.color,args.rgbd)
    elif args.lesson==16:
        rows=[json.loads(l) for l in (HERE/"records"/args.color/"trace.jsonl").read_text().splitlines()]
        rejected=0
        for r in rows:
            try: adapt(r["action"])
            except Reject: rejected+=1
        result=dict(steps=len(rows),rejected_raw=rejected,first_applied=adapt([0.,0.,*rows[0]["applied"]]),
                    physics=json.loads((HERE/"records"/args.color/"result.json").read_text())["success"])
    elif args.lesson==17: result=answer(args.query,args.version)
    else: result=benchmark(args.rgbd)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
