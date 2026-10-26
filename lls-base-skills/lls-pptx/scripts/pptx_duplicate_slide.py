#!/usr/bin/env python3
"""复制一张幻灯片（模板加页）——OOXML 包级手术，保留该页的全部元素与关系。

用法:
  python3 pptx_duplicate_slide.py 模板.pptx --slide 2 --times 3 -o 成片.pptx
      （把第 2 页复制 3 份追加到末尾，常用于"用模板页填充 N 个章节"）
  python3 pptx_duplicate_slide.py 模板.pptx --slide 2 --after 2 -o 成片.pptx
      （复制第 2 页并插到第 2 页之后）
"""
import argparse
import re
import shutil
import zipfile

from lls_pptx_utils import die

CT = "[Content_Types].xml"
PRES = "ppt/presentation.xml"
PRES_RELS = "ppt/_rels/presentation.xml.rels"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--slide", type=int, required=True, help="要复制的页码（1 基）")
    ap.add_argument("--times", type=int, default=1, help="复制几份（追加到末尾）")
    ap.add_argument("--after", type=int, help="插入到第 N 页之后（与 --times 二选一）")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if bool(args.times > 1) and args.after:
        die("--times 与 --after 二选一")

    src_zip = zipfile.ZipFile(args.input)
    names = src_zip.namelist()
    slide_re = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
    slide_nums = sorted(int(m.group(1)) for n in names if (m := slide_re.match(n)))
    if not slide_nums:
        die("包内没有幻灯片")
    if not (1 <= args.slide <= len(slide_nums)):
        die(f"页码越界: {args.slide}（共 {len(slide_nums)} 页）")

    src_num = slide_nums[args.slide - 1]
    copies = 1 if args.after else args.times
    if copies < 1:
        die("复制份数至少为 1")

    next_num = max(slide_nums) + 1
    copy_files: dict[str, bytes] = {}
    sld_ids = re.findall(r'<p:sldId[^>]*/>', src_zip.read(PRES).decode("utf-8"))
    max_rid = max((int(m) for n in names if n == PRES_RELS
                   for m in re.findall(r'Id="rId(\d+)"', src_zip.read(PRES_RELS).decode("utf-8"))), default=0)
    max_sldid = max((int(m) for s in sld_ids for m in re.findall(r'id="(\d+)"', s)), default=255)

    new_entries: list[tuple[int, int]] = []  # (sldId id, rId)
    rid = max_rid
    sid = max_sldid
    for k in range(copies):
        new_num = next_num + k
        # 1) 复制 slide XML 与其 rels
        for n in names:
            if n == f"ppt/slides/slide{src_num}.xml":
                copy_files[f"ppt/slides/slide{new_num}.xml"] = src_zip.read(n)
            elif n == f"ppt/slides/_rels/slide{src_num}.xml.rels":
                rels = src_zip.read(n).decode("utf-8")
                # 修正指向 slideN.xml 的内部引用（notesSlide 等重指向会导致冲突，直接剥离 notes 引用）
                rels = re.sub(r'<Relationship[^>]*Type="[^"]*notesSlide"[^>]*/>', "", rels)
                rels = re.sub(r'slide\d+\.xml', f"slide{new_num}.xml", rels)
                copy_files[f"ppt/slides/_rels/slide{new_num}.xml.rels"] = rels.encode("utf-8")
        # 2) 注册 Content-Type Override
        ct = copy_files.get("_ct") or src_zip.read(CT).decode("utf-8")
        override = (f'<Override PartName="/ppt/slides/slide{new_num}.xml" '
                    f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        ct = ct.replace("</Types>", override + "</Types>")
        copy_files["_ct"] = ct.encode("utf-8")
        # 3) presentation.xml.rels 加关系
        rels = copy_files.get("_prels") or src_zip.read(PRES_RELS).decode("utf-8")
        rid += 1
        rels = rels.replace("</Relationships>",
                            f'<Relationship Id="rId{rid}" '
                            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
                            f'Target="slides/slide{new_num}.xml"/></Relationships>')
        copy_files["_prels"] = rels.encode("utf-8")
        # 4) presentation.xml 的 sldIdLst 登记（--after 时插到第 N 个之后，否则追加）
        sid += 1
        pres = copy_files.get("_pres") or src_zip.read(PRES).decode("utf-8")
        entry = f'<p:sldId id="{sid}" r:id="rId{rid}"/>'
        m_lst = re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres, re.S)
        if not m_lst:
            die("presentation.xml 中找不到 <p:sldIdLst>")
        existing = re.findall(r"<p:sldId[^>]*/>", m_lst.group(1))
        pos = min(max(args.after, 1), len(existing)) if args.after else len(existing)
        existing.insert(pos, entry)
        pres = pres.replace(m_lst.group(0), "<p:sldIdLst>" + "".join(existing) + "</p:sldIdLst>")
        copy_files["_pres"] = pres.encode("utf-8")
        new_entries.append((sid, rid))

    # 重写包
    out_tmp = args.output + ".tmp"
    with zipfile.ZipFile(out_tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            if n in (CT, PRES, PRES_RELS):
                continue
            if re.match(r"^ppt/slides/slide\d+\.xml$", n) or re.match(r"^ppt/slides/_rels/slide\d+\.xml\.rels$", n):
                pass  # 原页照抄
            zout.writestr(n, src_zip.read(n))
        zout.writestr(CT, copy_files["_ct"])
        zout.writestr(PRES, copy_files["_pres"])
        zout.writestr(PRES_RELS, copy_files["_prels"])
        for path, data in copy_files.items():
            if path.startswith("ppt/slides/slide") or path.startswith("ppt/slides/_rels/"):
                zout.writestr(path, data)
    src_zip.close()
    shutil.move(out_tmp, args.output)
    action = f"插入到第 {args.after} 页后" if args.after else f"追加到末尾"
    print(f"[lls-pptx] 已复制第 {args.slide} 页 ×{copies}（{action}）→ {args.output}")
    print("[lls-pptx] 建议随后运行 pptx_check.py 验证包完整性")


if __name__ == "__main__":
    main()
