"""lls-biaoshu 共享工具：招标要求句式库 + 偏离判定。"""
import os
import re
import sys

# 硬性要求句式：招标文件里"必须/应/须/不得/具有/具备"引导的条款
REQ_HINT = r"(必须|应|须|不得|具有|具备|持有|提供|加盖|签署|不低于|不少于|不超过|在.*以内)"
# 高频硬性要求分类（用于需求聚类）
CATS = [
    ("资质证书", r"(资质|许可证|营业执照|认证|ISO|职称)"),
    ("业绩案例", r"(业绩|合同|案例|类似项目|近.{0,3}年)"),
    ("人员配置", r"(人员|项目经理|团队|资格证|持有)"),
    ("时间节点", r"(截止|开标|递交|有效期|工期|交付)"),
    ("保证金与费用", r"(保证金|投标费|工本费)"),
    ("格式与签署", r"(盖章|签字|密封|份数|正本|副本|电子版)"),
    ("技术参数", r"(参数|配置|规格|不低于|满足)"),
]
ENSURE = [("投标保证金", r"保证金"), ("递交截止时间", r"(递交|截止).{0,20}(时间|前)"),
          ("正副本份数", r"(正本|副本)"), ("签署盖章要求", r"(盖章|签字)"), ("有效期", r"有效期")]

def die(msg, code=1):
    print(f"[lls-biaoshu] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def ensure_parent(path):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path

def categorize(sentence: str) -> str:
    for name, pat in CATS:
        if re.search(pat, sentence):
            return name
    return "其他要求"

def extract_requirements(text: str) -> list[dict]:
    """按句切分，保留含硬性要求句式的句子 → [{req, cat}]。"""
    out = []
    for sent in re.split(r"[。\n]", text):
        s = sent.strip()
        if len(s) < 6:
            continue
        if re.search(REQ_HINT, s):
            out.append({"req": s[:160], "cat": categorize(s)})
    return out

def judge_response(req: str, bid_text: str) -> str:
    """粗糙三级判定：响应/部分响应（关键词出现）/未响应。仅供内部核对。"""
    kws = [w for w in re.findall(r"[\u4e00-\u9fff]{2,6}|[A-Za-z0-9]+", req) if len(w) >= 2][:8]
    hits = sum(1 for w in kws if w in bid_text)
    if hits >= max(3, len(kws) * 0.5):
        return "✅ 响应"
    if hits >= 1:
        return "⚠️ 部分响应"
    return "❌ 未响应"
