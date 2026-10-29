#!/usr/bin/env python3
"""大纲 → 自包含单文件 HTML 交互演示（键盘/触摸翻页、进度条、全屏，零外部依赖）。

用法: python3 htmlppt_build.py --outline 大纲.md -o 演示.html [--accent 1F469C]
特性: ←→/空格/PgUp/PgDn 翻页、F 全屏、触摸滑动、进度条、页码、单文件离线可用。
"""
import argparse
import html

from lls_htmlppt_utils import die, ensure_parent, guard_overwrite, parse_outline

ap = argparse.ArgumentParser()
ap.add_argument("--outline", required=True)
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--accent", default="1F469C")
ap.add_argument("--force", action="store_true")
args = ap.parse_args()

try:
    with open(args.outline, encoding="utf-8-sig", errors="ignore") as f:
        data = parse_outline(f.read())
except OSError as e:
    die(f"无法读取大纲文件 {args.outline}: {e}")
slides = data["slides"]
if not slides:
    die("大纲为空")

def esc(s):
    return html.escape(s, quote=True)

slide_html = []
for i, sl in enumerate(slides):
    parts = [f'<section class="slide" id="s{i}">']
    if sl.get("title"):
        parts.append(f'<h2>{esc(sl["title"])}</h2>')
    if sl.get("bullets"):
        parts.append('<ul>' + "".join(f"<li>{esc(b)}</li>" for b in sl["bullets"]) + '</ul>')
    if sl.get("takeaway"):
        parts.append(f'<p class="takeaway">{esc(sl["takeaway"])}</p>')
    parts.append(f'<div class="folio">{i + 1} / {len(slides)}</div>')
    parts.append('</section>')
    slide_html.append("\n".join(parts))

deck = "\n".join(slide_html)
accent = "".join(ch for ch in args.accent if ch in "0123456789abcdefABCDEF")[:6].ljust(6, "0")

DOC = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(data["title"] or "演示")}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#1a1a1a;font-family:'PingFang SC','Microsoft YaHei',sans-serif;overflow:hidden}}
#stage{{position:relative;width:100vw;height:100vh}}
.slide{{position:absolute;inset:0;display:none;flex-direction:column;justify-content:center;
  padding:8vh 10vw;background:#fafaf7;color:#212428}}
.slide.active{{display:flex}}
.slide h2{{font-size:clamp(28px,4.5vw,44px);color:#212428;border-bottom:3px solid #{accent};
  padding-bottom:12px;margin-bottom:5vh}}
.slide ul{{list-style:none;font-size:clamp(18px,2.4vw,26px);line-height:1.7}}
.slide ul li{{margin:1.4vh 0;padding-left:1.2em;position:relative}}
.slide ul li::before{{content:"•";position:absolute;left:0;color:#{accent}}}
.takeaway{{margin-top:auto;font-size:clamp(16px,2vw,22px);font-weight:bold;color:#{accent};
  border-top:2px solid #{accent};padding-top:2vh}}
.folio{{position:absolute;bottom:3vh;right:4vw;font-size:13px;color:#999}}
#bar{{position:fixed;top:0;left:0;height:4px;background:#{accent};width:0;transition:width .25s}}
.hint{{position:fixed;bottom:3vh;left:4vw;font-size:12px;color:#666}}
</style></head><body>
<div id="bar"></div>
<div id="stage">
{deck}
</div>
<div class="hint">← → 翻页 · F 全屏</div>
<script>
const slides=[...document.querySelectorAll('.slide')];let cur=0;
const bar=document.getElementById('bar');
function show(i){{
  cur=Math.max(0,Math.min(slides.length-1,i));
  slides.forEach((s,k)=>s.classList.toggle('active',k===cur));
  bar.style.width=((cur+1)/slides.length*100)+'%';
}}
show(0);
addEventListener('keydown',e=>{{
  if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){{show(cur+1);e.preventDefault();}}
  if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){{show(cur-1);e.preventDefault();}}
  if(e.key==='f'||e.key==='F'){{document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}}
}});
let tx=null;
addEventListener('touchstart',e=>tx=e.touches[0].clientX);
addEventListener('touchend',e=>{{
  if(tx===null)return;const dx=e.changedTouches[0].clientX-tx;
  if(Math.abs(dx)>50)show(cur+(dx<0?1:-1));tx=null;
}});
</script></body></html>"""

out = guard_overwrite(args.output, args.force)
try:
    ensure_parent(out)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(DOC)
except OSError as e:
    die(f"无法写入演示文件 {out}: {e}")
print(f"[lls-htmlppt] 单文件 HTML 演示 {len(slides)} 页 → {out}")
print(f"[lls-htmlppt] 浏览器打开即放映：←→ 翻页 · F 全屏 · 发链接即可分享")
