#!/usr/bin/env python3
"""刘老师 · 提速棘轮

把性能基线锁进 ratchet.json，之后每次改动后用新指标来对赌：
任何核心指标劣化超过容差 → 退出码 1，发布流程应当终止。

用法：
    python3 scripts/ratchet.py lock   --baseline baseline.json [--tolerance 5]
        用基线文件初始化/重置棘轮（容差为百分比，默认 5）
    python3 scripts/ratchet.py check  --new new-metrics.json
        新测量对赌锁存值：全数守住 → 退出码 0 并滚动更新锁存；任一回退 → 退出码 1

约定：指标单位为毫秒（*_ms）或比率（CLS 等越小越好），一律"越小越好"。
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RATCHET_FILE = Path(__file__).resolve().parent.parent / "ratchet.json"


def load_metrics(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    metrics = data.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        sys.exit(f"FAIL: {path} 中没有可用的 metrics 字段")
    return {k: float(v) for k, v in metrics.items()}


def cmd_lock(args) -> int:
    metrics = load_metrics(Path(args.baseline))
    RATCHET_FILE.write_text(
        json.dumps(
            {
                "locked_metrics": metrics,
                "tolerance_pct": args.tolerance,
                "locked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"棘轮已锁存 {len(metrics)} 项指标（容差 {args.tolerance}%）→ {RATCHET_FILE}")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    return 0


def cmd_check(args) -> int:
    if not RATCHET_FILE.exists():
        sys.exit("FAIL: 尚未锁存棘轮，请先运行 lock --baseline baseline.json")
    ratchet = json.loads(RATCHET_FILE.read_text(encoding="utf-8"))
    locked = {k: float(v) for k, v in ratchet["locked_metrics"].items()}
    tolerance = float(ratchet.get("tolerance_pct", 5)) / 100.0

    new = load_metrics(Path(args.new))
    regressions = []
    for key, lock_val in locked.items():
        if key not in new:
            print(f"MISSING: 锁存指标 {key} 未出现在新测量中（视为未劣化，但请补测）")
            continue
        limit = lock_val * (1 + tolerance)
        if new[key] > limit:
            regressions.append((key, lock_val, new[key], limit))

    if regressions:
        print("棘轮未过 —— 以下指标劣化超过容差：")
        for key, lock_val, now, limit in regressions:
            pct = (now - lock_val) / lock_val * 100
            print(f"  {key}: 锁存 {lock_val:.0f} → 当前 {now:.0f}（劣化 {pct:.1f}%，上限 {limit:.0f}）")
        return 1

    # 全部守住：滚动更新锁存值，棘轮收紧
    rolled = {k: min(v, new.get(k, v)) for k, v in locked.items()}
    ratchet["locked_metrics"] = rolled
    ratchet["locked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    RATCHET_FILE.write_text(json.dumps(ratchet, ensure_ascii=False, indent=2), encoding="utf-8")
    print("棘轮通过：全部指标未劣化，锁存值已滚动更新为更优值")
    for k, v in rolled.items():
        print(f"  {k}: {v}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="性能棘轮：只许变好，不许回退")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_lock = sub.add_parser("lock", help="用基线初始化/重置棘轮")
    p_lock.add_argument("--baseline", required=True, help="基线 JSON 文件")
    p_lock.add_argument("--tolerance", type=float, default=5, help="容差百分比，默认 5")
    p_lock.set_defaults(func=cmd_lock)

    p_check = sub.add_parser("check", help="新测量对赌锁存值")
    p_check.add_argument("--new", required=True, help="新测量 JSON 文件（含 metrics 字段）")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
