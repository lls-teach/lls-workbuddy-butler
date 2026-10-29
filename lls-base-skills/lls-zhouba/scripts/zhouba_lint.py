#!/usr/bin/env python3
"""周报/日报量化 lint：无数字条目点名 + 空话检测 + 结构完整性。

用法: python3 zhouba_lint.py 周报.md
空话黑名单：持续推进/持续优化/加强/提升/完善 等"无数字无对象"的表述。
"""
import re
import sys

FILLER_PHRASES = ["持续推进", "持续优化", "不断加强", "进一步完善", "努力提升", "加强沟通", "持续推进中"]
QUANT = re.compile(r"(\d+(?:\.\d+)?\s*[%％万亿个条家次人元小时天周月项件份单篇])|(\d{2,})")

def main() -> None:
    # Windows 旧控制台默认编码（如 cp936）无法输出 ❌/⚠️/✅ 等符号时会直接
    # 抛 UnicodeEncodeError；能重设就重设为 UTF-8，不能则用 replace 兜底，
    # Linux/macOS 现代终端上行为不变。
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("用法: zhouba_lint.py 周报.md")
        sys.exit(0)
    if len(sys.argv) < 2:
        print("[lls-zhouba] 用法: zhouba_lint.py 周报.md")
        sys.exit(1)
    path = sys.argv[1]
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        die(f"找不到文件: {path}")
    except OSError as e:
        die(f"无法读取文件 {path}: {e}")
    except UnicodeDecodeError as e:
        die(f"文件不是 UTF-8 编码: {path} ({e})")
    items = [l.strip() for l in text.split("\n") if l.strip().startswith(("-", "*", "•"))]
    problems, warnings = [], []
    no_quant = [i for i in items if not QUANT.search(i)]
    if no_quant:
        problems.append(f"{len(no_quant)} 条事项无量化数字：")
        for i in no_quant:
            problems.append(f"    {i[:60]}")
    for i in items:
        for fp in FILLER_PHRASES:
            if fp in i and not QUANT.search(i):
                warnings.append(f"空话嫌疑：「{i[:60]}」（有'{fp}'但无数字无对象）")
                break
    for kw in ("本周", "下周", "完成", "计划"):
        if kw not in text:
            warnings.append(f"缺少「{kw}」相关内容——周报四要素：完成/进行中/下周计划/风险求助")
    risk = [l for l in text.split("\n") if "风险" in l or "求助" in l or "阻塞" in l]
    if not risk:
        warnings.append("无「风险/求助」段——阻塞项越早暴露越安全")
    if problems:
        print(f"[lls-zhouba] ❌ {len(problems)} 项：")
        for p in problems:
            print("  " + p)
    if warnings:
        print(f"[lls-zhouba] ⚠️ {len(warnings)} 条建议：")
        for w in warnings:
            print("  " + w)
    if not problems and not warnings:
        print("[lls-zhouba] ✅ 量化完整、结构健康")
    sys.exit(1 if problems else 0)

def die(msg, code=1):
    print(f"[lls-zhouba] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

main()
