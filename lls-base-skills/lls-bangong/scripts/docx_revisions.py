#!/usr/bin/env python3
"""检测 Word 文档中的修订痕迹（tracked changes）——只读报告，不做接受/拒绝裁决。

用法: python3 docx_revisions.py 输入.docx
说明: 扫描 word/document.xml 的 w:ins（插入）与 w:del（删除）标记。
      能检测与列作者，不能代为接受/拒绝——裁决属于人的决策。
"""
import argparse
import re
import zipfile

from lls_docx_utils import die

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    args = ap.parse_args()

    try:
        with zipfile.ZipFile(args.input) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    except FileNotFoundError:
        die(f"文件不存在: {args.input}")
    except KeyError:
        die("不是有效的 docx（缺少 word/document.xml）")
    except Exception as e:  # noqa: BLE001
        die(f"无法读取: {e}")

    def block_stat(tag: str) -> tuple[int, set[str], list[str]]:
        blocks = re.findall(rf"<w:{tag}\b[^>]*>.*?</w:{tag}>", xml, re.S)
        authors = set()
        samples = []
        for b in blocks:
            a = re.search(r'w:author="([^"]*)"', b)
            if a:
                authors.add(a.group(1))
            text = "".join(re.findall(r"<w:[^>]*t(?:[^>]*)>([^<]*)<", b)) or \
                   "".join(re.findall(r"<w:delText[^>]*>([^<]*)<", b))
            if text.strip() and len(samples) < 5:
                samples.append(text.strip()[:40])
        return len(blocks), authors, samples

    ins_n, ins_authors, ins_samples = block_stat("ins")
    del_n, del_authors, del_samples = block_stat("del")
    comments = xml.count("<w:comment ")

    if ins_n == 0 and del_n == 0:
        print(f"[lls-docx] ✅ 无修订痕迹（{comments} 条批注）")
        return

    print(f"[lls-docx] ⚠️ 文档含未处理的修订：插入 {ins_n} 处，删除 {del_n} 处，批注 {comments} 条")
    if ins_authors | del_authors:
        print(f"[lls-docx] 修订作者: {sorted(ins_authors | del_authors)}")
    if ins_samples:
        print("[lls-docx] 插入示例:", ins_samples[:3])
    if del_samples:
        print("[lls-docx] 删除示例:", del_samples[:3])
    print("[lls-docx] 边界说明：本技能可检测修订，接受/拒绝请由文档所有者在 Word/WPS 中裁决后另存。")


if __name__ == "__main__":
    main()
