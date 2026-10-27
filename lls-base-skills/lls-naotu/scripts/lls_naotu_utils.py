"""lls-naotu 共享工具。"""
import sys

def die(msg, code=1):
    print(f"[lls-naotu] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
