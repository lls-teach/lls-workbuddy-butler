"""lls-baoshui 共享工具：征期日历、四类型资料清单、免责声明。"""
import sys

# Windows 兼容：旧版 cmd 控制台默认 GBK，打印 →/✅/❌/⚠️ 会 UnicodeEncodeError；
# 导入时即把 stdout/stderr 切为 UTF-8（失败则静默保持原编码，Linux 下无影响）。
# 放在模块顶层是为了覆盖 --help 与 die() 在内的所有后续打印。
try:
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr is not None:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DISCLAIMER = "> ⚠️ 本清单为通用备稿工具，**不构成税务意见**；征期遇节假日顺延以主管税务机关公告为准，具体政策以当地执行口径为准。"

# 征期规律（增值税/附加税费/经营所得个税，按季：1/4/7/10 月 15 日前，节假日顺延）
QUARTER_DEADLINES = ["1 月 15 日前", "4 月 15 日前", "7 月 15 日前", "10 月 15 日前"]

CHECKLISTS = {
    "个体工商户·定期定额": {
        "按季资料": [
            "收入流水汇总（对账单/收款码后台导出）",
            "开票汇总（数电票开具/代开记录）",
            "上期完税凭证（备查）",
            "成本费用票据（进货/房租/水电，备查）",
            "银行对账单（经营账户）",
        ],
        "动作": ["登录电子税务局确认定期定额核定情况", "超额时按实际申报（超过定额 30% 须主动申报）"],
    },
    "个体工商户·查账征收": {
        "按季资料": [
            "收入明细账（全部开票+未开票收入）",
            "成本费用发票与台账",
            "银行对账单与现金流水",
            "工资表（有雇工时）+ 社保缴费凭证",
            "上季度经营所得预缴凭证",
        ],
        "动作": ["经营所得 A 表（季度预缴，15 日前）", "年终 3 月 31 日前经营所得 B 表汇算清缴"],
    },
    "小规模纳税人·查账征收": {
        "按季资料": [
            "销项发票汇总（数电票台账）",
            "进项发票台账（取得合规凭证）",
            "银行对账单",
            "库存盘点表（备查）",
            "上期申报回执",
        ],
        "动作": ["增值税及附加税费申报（季报，征期内）", "季度利润核对（联动经营所得/企业所得税）"],
    },
    "一般纳税人": {
        "按月资料": [
            "销项发票汇总表（全电票平台导出）",
            "进项抵扣凭证勾选确认记录",
            "银行对账单与应收应付台账",
            "工资社保台账",
            "上期申报回执与完税凭证",
        ],
        "动作": ["增值税按月申报（征期内）", "附加税费同步申报", "进项发票勾选确认（抵扣期内）"],
    },
}

def die(msg, code=1):
    print(f"[lls-baoshui] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
