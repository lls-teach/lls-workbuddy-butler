#!/usr/bin/env python3
"""按纳税人类型生成季度/月度报税资料清单与征期自查表（Markdown）。

用法: python3 baoshui_list.py --type "个体工商户·查账征收" -o 报税清单.md
类型: 个体工商户·定期定额 / 个体工商户·查账征收 / 小规模纳税人·查账征收 / 一般纳税人
"""
import argparse

from lls_baoshui_utils import CHECKLISTS, DISCLAIMER, QUARTER_DEADLINES, die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("--type", required=True, help=" | ".join(CHECKLISTS))
ap.add_argument("--quarter", default="Q4（10 月征期）")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

if args.type not in CHECKLISTS:
    die(f"类型必须是: {' / '.join(CHECKLISTS)}")
data = CHECKLISTS[args.type]
freq = "按月" if args.type == "一般纳税人" else "按季"

lines = [
    f"# {args.type} · 报税资料清单（{args.quarter}）", "",
    f"征期节点（{freq}）：{'、'.join(QUARTER_DEADLINES) if freq == '按季' else '每月 15 日前（节假日顺延）'}", "",
    "## 一、需要准备的资料", "",
]
for i, item in enumerate(data["按季资料" if freq == "按季" else "按月资料"], 1):
    lines.append(f"- [ ] {i}. {item}")
lines += ["", "## 二、申报动作", ""]
for a in data["动作"]:
    lines.append(f"- [ ] {a}")
lines += ["", "## 三、自查要点", "",
          "- [ ] 收入是否全部入账（开票 + 未开票）",
          "- [ ] 优惠是否适用（小规模免税额度/个体户减半）",
          "- [ ] 上期申报回执是否留存",
          "- [ ] 是否有逾期未申报记录", "",
          DISCLAIMER]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print(f"[lls-baoshui] 清单已生成 → {args.output}（{args.type} · {len(data['按季资料' if freq == '按季' else '按月资料'])} 项资料 + {len(data['动作'])} 项动作）")
