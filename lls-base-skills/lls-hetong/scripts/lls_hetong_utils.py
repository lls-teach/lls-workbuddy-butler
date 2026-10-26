"""lls-hetong 共享工具：条款切分 + 风险关键词库。"""
import re

RISKS = [
    ("违约金上限缺失或过高", ["违约金"], "核对违约金计算方式与上限；超过实际损失 30% 的部分可请求酌减"),
    ("管辖地不利", ["管辖", "诉讼", "仲裁"], "确认管辖法院/仲裁地；异地管辖会增加维权成本，仲裁为一裁终局"),
    ("付款节点模糊", ["付款", "支付", "结算"], "核对金额、时点、方式是否三要素齐全"),
    ("自动续约", ["自动续约", "自动续期", "顺延"], "警惕默认自动续约条款与退出窗口期"),
    ("单方解除权不对等", ["单方解除", "有权解除", "随时解除"], "核对解除条件是否对等、通知期是否合理"),
    ("知识产权归属", ["知识产权", "著作权", "专利", "商标"], "确认成果归属、授权范围与是否可再授权"),
    ("保密期限", ["保密"], "确认保密范围、期限与违约责任是否对等"),
    ("定金与订金混淆", ["定金"], "「定金」适用双倍罚则、「订金」仅为预付款——一字之差法律后果不同"),
    ("竞业限制", ["竞业"], "核对竞业范围、期限（一般不超过 2 年）与补偿金"),
    ("不可抗力", ["不可抗力"], "确认不可抗力定义范围与通知义务"),
    ("通知送达", ["通知", "送达"], "确认送达地址、方式与生效时点"),
    ("税费承担", ["税费", "税金", "发票"], "确认各项税费承担方与发票开具义务"),
]
CLAUSE_PAT = re.compile(r"第[一二三四五六七八九十百\d]+条")

def split_clauses(text: str) -> list[tuple[str, str]]:
    """按 第X条 切分条款，返回 (条款头, 条款全文)。前置部分归为 Preamble。"""
    matches = list(CLAUSE_PAT.finditer(text))
    clauses = []
    if matches:
        pre = text[:matches[0].start()].strip()
        if pre:
            clauses.append(("Preamble", pre))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            clauses.append((m.group(0), text[m.start():end].strip()))
    else:
        clauses.append(("Preamble", text.strip()))
    return clauses


def ensure_parent(path: str) -> str:
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
