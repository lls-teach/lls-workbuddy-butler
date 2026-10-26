"""kejian 的极简辅助（避免跨包依赖）。"""
import os, sys

def die(msg, code=1):
    print(f"[lls-kejian] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def ensure_parent(path):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
