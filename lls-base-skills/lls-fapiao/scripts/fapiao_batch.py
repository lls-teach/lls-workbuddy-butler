#!/usr/bin/env python3
"""批量处理发票文件夹/文件列表：提取 → 解析 → 合并 JSONL，并跑查重与校验。

用法:
  python3 fapiao_batch.py 发票目录/ -o 汇总.jsonl
  python3 fapiao_batch.py 1.pdf 2.pdf -o 汇总.jsonl [--owner 张三]
有文字层的 PDF 直接提取；扫描件/图片走 OCR（需 PaddleOCR，见失败分支）。
每个文件输出一行 JSON：{"file", "owner", "fields", "manual_review", "problems", "ocr_used"}
"""
import argparse
import json
import os
import sys

from lls_fapiao_utils import die, ensure_parent, first_match, norm_date, to_amount

try:
    import pypdfium2 as pdfium
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


def pdf_text(path: str, password: str = "") -> tuple[str, bool]:
    """返回 (文本, 是否有文字层)。"""
    if not HAS_PDF:
        die("缺 pypdfium2: pip install pypdfium2")
    pdf = pdfium.PdfDocument(path, password=password or None)
    parts = []
    for page in pdf:
        tp = page.get_textpage()
        parts.append(tp.get_text_bounded())
        tp.close()
    pdf.close()
    return "\n".join(parts), bool("".join(parts).strip())


def ocr_text(path: str, lang: str = "ch") -> str:
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        die("扫描件需要 OCR：pip install paddleocr paddlepaddle（首次运行会下载模型）。"
            "若无需 OCR，请只提交带文字层的 PDF。")
    ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
    lines = []
    for block in (ocr.ocr(path, cls=True)[0] or []):
        lines.append(block[1][0])
    return "\n".join(lines)


def collect_inputs(inputs: list[str]) -> list[str]:
    files = []
    for p in inputs:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
                    files.append(os.path.join(p, name))
        elif os.path.exists(p):
            files.append(p)
        else:
            print(f"[lls-fapiao] ⚠️ 跳过不存在的输入: {p}", file=sys.stderr)
    return files


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="目录或文件（pdf/png/jpg/txt）")
    ap.add_argument("-o", "--output", required=True, help="输出 JSONL")
    ap.add_argument("--owner", default="", help="报销人（批量归属）")
    ap.add_argument("--password", default="")
    args = ap.parse_args()

    files = collect_inputs(args.inputs)
    if not files:
        die("没有可处理的文件")
    print(f"[lls-fapiao] 待处理 {len(files)} 个文件")
    ensure_parent(args.output)

    records, seen_nos = [], {}
    for path in files:
        rec = {"file": os.path.basename(path), "owner": args.owner}
        ocr_used = False
        try:
            if path.lower().endswith(".pdf"):
                text, has_layer = pdf_text(path, args.password)
                if not has_layer:
                    text = ocr_text(path)
                    ocr_used = True
            elif path.lower().endswith(".txt"):
                text = open(path, encoding="utf-8", errors="ignore").read()
            else:
                text = ocr_text(path)
                ocr_used = True
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            rec.update({"error": str(e)[:200]})
            records.append(rec)
            print(f"[lls-fapiao] ✗ {path}: {e}", file=sys.stderr)
            continue

        for field in ("invoice_no", "date", "total", "buyer", "kind"):
            if field == "kind":
                v, conf = first_match(text, "kind")
                rec[field] = {"value": v or "未识别", "confidence": 0.95 if v else 0.5}
            else:
                v, conf = first_match(text, field)
                if field == "date":
                    v = norm_date(v)
                if field == "total":
                    v = to_amount(v)
                rec[field] = {"value": v, "confidence": conf}
        rec["ocr_used"] = ocr_used

        # 查重（同号 = 重复报销风险）
        no = rec["invoice_no"]["value"]
        if no:
            if no in seen_nos:
                rec.setdefault("problems", []).append(f"发票号码重复：与 {seen_nos[no]} 相同（重复报销风险）")
            else:
                seen_nos[no] = rec["file"]
        rec["manual_review"] = [f for f in ("invoice_no", "date", "total", "buyer")
                                if rec[f]["value"] and rec[f]["confidence"] < 0.85]
        records.append(rec)
        flag = "（OCR）" if ocr_used else ""
        print(f"[lls-fapiao] ✓ {path}{flag}: 号码={no} 金额={rec['total']['value']}")

    with open(args.output, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    dup = sum(1 for r in records if any("重复" in p for p in r.get("problems", [])))
    print(f"[lls-fapiao] 批量完成 {len(records)} 个 → {args.output}（重复号码 {dup}，待人工核对 "
          f"{sum(1 for r in records if r.get('manual_review'))}）")


if __name__ == "__main__":
    main()
