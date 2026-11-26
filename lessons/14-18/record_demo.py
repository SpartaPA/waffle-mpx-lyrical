"""Encode two actual Isaac frame sequences with their measured feedback into a lesson video."""
import argparse
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('run',type=Path)
p.add_argument('output',type=Path)
args=p.parse_args()
font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(size): return ImageFont.truetype(font_path,size,index=1)
large,small=font(32),font(23)
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1152x648','-r','8','-i','-','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(args.output)]
with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
    for color,ko in [('red','빨간'),('blue','파란')]:
        folder=args.run/f'00-{color}'
        rows=[json.loads(s) for s in (folder/'trace.jsonl').read_text().splitlines()]
        result=json.loads((folder/'result.json').read_text())
        for idx in [0]*12+list(range(len(rows)))+[len(rows)-1]*16:
            r=rows[idx]; im=Image.new('RGB',(1152,648),'#121c29'); d=ImageDraw.Draw(im)
            d.text((24,12),'14–18강   |   '+ko+' 블록을 초록 칸에 놓기',font=large,fill='white')
            with Image.open(folder/f'frame-{idx:03d}.jpg') as view: im.paste(view,(24,76))
            d.text((688,78),'Isaac Sim 6.1 · D435',font=small,fill='#8bddd0')
            d.multiline_text((688,136),f'행동 {idx+1} / {len(rows)}\n\n관절 1    {r["applied"][0]:+.3f} rad\n그리퍼    {1000*r["applied"][-1]:.1f} mm\n블록 높이    {1000*r["cubes"][color][2]:.1f} mm\n안착 시간    {r["stable_s"]:.2f} s',font=small,fill='white',spacing=8)
            if idx==len(rows)-1:
                d.text((688,460),'판정   '+('성공' if result['success'] else '실패'),font=large,fill='#95e7b2')
            d.text((24,584),'시드 1927  ·  SmolVLM2 + Waffle 색상 궤적 헤드  ·  관절 제어 4 Hz  ·  동작 2배속',font=small,fill='#cfdae3')
            proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('encoding failed')
