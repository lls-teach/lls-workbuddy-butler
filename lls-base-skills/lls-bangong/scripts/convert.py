#!/usr/bin/env python3
"""lls-convert engine: local format conversion with hub routing.
Usage: python3 convert.py <input_file> <target_ext> [-o outdir]
Exit codes: 0 ok, 2 unsupported pair, 3 conversion failed, 4 bad input.
Prints one JSON line: {"ok":bool, "output":path|null, "route":str, "error":str|null}
"""
import sys, os, json, subprocess, shutil, zipfile, tarfile, io, re

def out(ok, output=None, route="", error=None, code=0):
    print(json.dumps({"ok": ok, "output": output, "route": route, "error": error}, ensure_ascii=False))
    sys.exit(code)

def lo_available(): return shutil.which("soffice") is not None
def ff_available(): return shutil.which("ffmpeg") is not None

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300, **kw)

def via_libreoffice(src, tgt, outdir):
    # LibreOffice headless conversion; txt needs a filter hint for docs
    conv = tgt
    if tgt == "txt":
        conv = "txt:Text (encoded):UTF8"
    if tgt == "csv":
        conv = "csv:Text - txt - csv (StarCalc)"
    r = run(["soffice", "--headless", "--norestore", "--convert-to", conv, "--outdir", outdir, src])
    base = os.path.splitext(os.path.basename(src))[0]
    cand = os.path.join(outdir, base + "." + tgt)
    if os.path.exists(cand) and os.path.getsize(cand) > 0:
        return cand
    raise RuntimeError("libreoffice produced no output: " + (r.stderr or r.stdout)[-300:])

def via_ffmpeg(src, tgt, outdir, extra=None):
    base = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(outdir, base + "." + tgt)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src]
    if extra: cmd += extra
    cmd += [dst]
    r = run(cmd)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return dst
    raise RuntimeError("ffmpeg failed: " + (r.stderr or "")[-300:])

def via_pillow(src, tgt, outdir):
    from PIL import Image
    base = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(outdir, base + "." + tgt)
    im = Image.open(src)
    if tgt in ("jpg", "jpeg", "bmp") and im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGB")
    if tgt == "ico":
        im = im.copy(); im.thumbnail((256, 256))
    im.save(dst, format={"jpg": "JPEG", "jpeg": "JPEG", "tiff": "TIFF"}.get(tgt, tgt.upper()))
    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
        raise RuntimeError("pillow produced empty output")
    return dst

def images_to_pdf(srcs, outdir, name="merged"):
    from PIL import Image
    ims = []
    for s in srcs:
        im = Image.open(s)
        ims.append(im.convert("RGB") if im.mode != "RGB" else im)
    dst = os.path.join(outdir, name + ".pdf")
    ims[0].save(dst, save_all=True, append_images=ims[1:])
    return dst

def pdf_to_text(src):
    txt = ""
    try:
        import pdfplumber
        with pdfplumber.open(src) as pdf:
            txt = "\n".join((p.extract_text() or "") for p in pdf.pages)
    except Exception:
        from pypdf import PdfReader
        txt = "\n".join((p.extract_text() or "") for p in PdfReader(src).pages)
    return txt

def pdf_to_images(src, tgt, outdir):
    import fitz
    base = os.path.splitext(os.path.basename(src))[0]
    doc = fitz.open(src)
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    dst = os.path.join(outdir, base + "." + tgt)
    fmt = "jpeg" if tgt in ("jpg", "jpeg") else "png"
    with open(dst, "wb") as fh: fh.write(pix.tobytes(fmt))
    return dst

def pdf_merge(srcs, outdir, name="merged"):
    from pypdf import PdfWriter
    w = PdfWriter()
    for s in srcs: w.append(s)
    dst = os.path.join(outdir, name + ".pdf")
    with open(dst, "wb") as fh: w.write(fh)
    return dst

def read_text(p):
    with open(p, encoding="utf-8", errors="replace") as fh: return fh.read()

def write_text(p, s):
    with open(p, "w", encoding="utf-8") as fh: fh.write(s)
    return p

def dst_path(src, tgt, outdir):
    return os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + "." + tgt)

# ---------- data (pandas) ----------
DATA_EXTS = {"xlsx","xls","ods","csv","tsv","json","xml","yaml","yml"}
def via_pandas(src, sext, tgt, outdir):
    import pandas as pd
    dst = dst_path(src, tgt, outdir)
    if sext in ("xlsx","xls","ods"):
        df = pd.read_excel(src)
    elif sext == "csv": df = pd.read_csv(src)
    elif sext == "tsv": df = pd.read_csv(src, sep="\t")
    elif sext == "json": df = pd.read_json(src)
    elif sext == "xml": df = pd.read_xml(src)
    elif sext in ("yaml","yml"):
        import yaml
        data = yaml.safe_load(read_text(src))
        df = pd.DataFrame(data if isinstance(data, list) else [data])
    else: raise RuntimeError("pandas cannot read " + sext)
    if tgt == "xlsx": df.to_excel(dst, index=False)
    elif tgt == "csv": df.to_csv(dst, index=False)
    elif tgt == "tsv": df.to_csv(dst, index=False, sep="\t")
    elif tgt == "json": df.to_json(dst, orient="records", force_ascii=False, indent=2)
    elif tgt == "xml": df.to_xml(dst, index=False)
    elif tgt in ("yaml","yml"):
        import yaml
        write_text(dst, yaml.safe_dump(df.to_dict(orient="records"), allow_unicode=True))
    elif tgt == "html": write_text(dst, df.to_html(index=False))
    elif tgt == "md": write_text(dst, df.to_markdown(index=False))
    elif tgt == "ods": df.to_excel(dst, index=False, engine="odf")
    else: raise RuntimeError("pandas cannot write " + tgt)
    return dst

# ---------- epub ----------
def make_epub(title, paragraphs, dst):
    body = "\n".join(f"<p>{p}</p>" for p in paragraphs if p.strip())
    xhtml = f'<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>{title}</title></head><body><h1>{title}</h1>{body}</body></html>'
    opf = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bid" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:title>%s</dc:title><dc:language>zh-CN</dc:language><dc:identifier id="bid">urn:lls-convert:1</dc:identifier></metadata>
<manifest><item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/><item id="c1" href="c1.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine toc="ncx"><itemref idref="c1"/></spine></package>''' % title
    ncx = '''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head></head><docTitle><text>%s</text></docTitle>
<navMap><navPoint id="n1" playOrder="1"><navLabel><text>%s</text></navLabel><content src="c1.xhtml"/></navPoint></navMap></ncx>''' % (title, title)
    container = '''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
    with zipfile.ZipFile(dst, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/toc.ncx", ncx)
        z.writestr("OEBPS/c1.xhtml", xhtml)
    return dst

def epub_to_paragraphs(src):
    import xml.etree.ElementTree as ET
    paras = []
    with zipfile.ZipFile(src) as z:
        for name in z.namelist():
            if name.endswith((".xhtml", ".html")):
                raw = z.read(name).decode("utf-8", errors="replace")
                text = re.sub(r"<[^>]+>", "\n", raw)
                paras += [t.strip() for t in text.split("\n") if t.strip()]
    return paras

# ---------- subtitles ----------
def parse_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        if len(lines) >= 2 and "-->" in lines[1 if lines[0].strip().isdigit() else 0]:
            ti = 1 if lines[0].strip().isdigit() else 0
            start, end = [t.strip().replace(",", ".") for t in lines[ti].split("-->")]
            cues.append((start, end, "\n".join(lines[ti+1:])))
    return cues

def srt_to_vtt(cues):
    return "WEBVTT\n\n" + "\n\n".join(f"{s} --> {e}\n{t}" for s, e, t in cues) + "\n"

def cues_to_srt(cues):
    return "\n\n".join(f"{i+1}\n{s.replace('.', ',')} --> {e.replace('.', ',')}\n{t}" for i, (s, e, t) in enumerate(cues)) + "\n"

def cues_to_ass(cues):
    def ts(t):
        h, m, rest = t.split(":"); s = float(rest)
        return f"{int(h)}:{int(m):02d}:{s:05.2f}"
    ev = "\n".join(f"Dialogue: 0,{ts(s)},{ts(e)},Default,,0,0,0,,{t}" for s, e, t in cues)
    return "[Script Info]\nTitle: lls-convert\nScriptType: v4.00+\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,20,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + ev + "\n"

def parse_vtt(text):
    return parse_srt(text.replace("WEBVTT", "").strip())

def parse_ass(text):
    cues = []
    for line in text.splitlines():
        if line.startswith("Dialogue:"):
            parts = line.split(",", 9)
            if len(parts) == 10:
                cues.append((parts[1].strip(), parts[2].strip(), parts[9].replace("\\N", "\n")))
    return cues

# ---------- archives ----------
def archive_convert(src, sext, tgt, outdir):
    dst = dst_path(src, tgt if not tgt.startswith("tar") else "tar.gz", outdir)
    if tgt == "tar.gz": dst = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + ".tar.gz")
    tmp = dst + ".tmpdir"; os.makedirs(tmp, exist_ok=True)
    if sext == "zip":
        with zipfile.ZipFile(src) as z: z.extractall(tmp)
    elif sext in ("tar", "tar.gz", "tgz"):
        with tarfile.open(src) as t: t.extractall(tmp)
    elif sext == "7z":
        import py7zr
        with py7zr.SevenZipFile(src) as z: z.extractall(tmp)
    else: raise RuntimeError("cannot unpack " + sext)
    if tgt == "zip":
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(tmp):
                for f in files:
                    fp = os.path.join(root, f); z.write(fp, os.path.relpath(fp, tmp))
    elif tgt == "tar.gz":
        with tarfile.open(dst, "w:gz") as t: t.add(tmp, arcname=".")
    elif tgt == "7z":
        import py7zr
        with py7zr.SevenZipFile(dst, "w") as z: z.writeall(tmp, ".")
    else: raise RuntimeError("cannot pack " + tgt)
    import shutil as sh; sh.rmtree(tmp, ignore_errors=True)
    return dst

# ---------- fonts ----------
def via_fonttools(src, tgt, outdir):
    from fontTools.ttLib import TTFont
    dst = dst_path(src, tgt, outdir)
    f = TTFont(src)
    if tgt in ("woff", "woff2"): f.flavor = tgt
    f.save(dst)
    return dst

# ---------- extra handlers ----------
def text_to_docx(paras, dst, title=""):
    from docx import Document
    d = Document()
    if title: d.add_heading(title, level=1)
    for p in paras:
        if p.strip(): d.add_paragraph(p)
    d.save(dst); return dst

def md_to_html(md_text):
    import markdown
    return "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>" + markdown.markdown(md_text) + "</body></html>"

def html_to_md(html_text):
    from markdownify import markdownify
    return markdownify(html_text)

def strip_tags(html_text):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html_text, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    return "\n".join(l.strip() for l in t.split("\n") if l.strip())

LO_SRC = {"doc","docx","odt","rtf","html","htm","txt","xls","xlsx","ods","csv","ppt","pptx","odp","svg"}
LO_TGT = {"pdf","docx","odt","rtf","html","txt","xlsx","ods","csv","pptx","odp"}
IMG_EXTS = {"png","jpg","jpeg","gif","webp","bmp","tiff","ico"}
AUD_EXTS = {"mp3","wav","flac","aac","ogg","m4a","wma","aiff","opus"}
VID_EXTS = {"mp4","mov","avi","mkv","webm","flv","wmv","m4v","3gp","mpeg"}
SUB_SRC = {"srt","vtt","ass","ssa"}; SUB_TGT = {"srt","vtt","ass"}
ARC_EXTS = {"zip","7z"}  # plus tar.gz handled specially

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    outdir = "."
    if "-o" in sys.argv:
        outdir = sys.argv[sys.argv.index("-o") + 1]
    if len(args) < 2: out(False, error="usage: convert.py <input> <target_ext> [-o outdir]", code=4)
    src, tgt = args[0], args[1].lower().lstrip(".")
    if not os.path.exists(src): out(False, error="input not found", code=4)
    os.makedirs(outdir, exist_ok=True)
    base = os.path.basename(src)
    if base.endswith(".tar.gz"): sext = "tar.gz"
    else: sext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    if sext == tgt: out(False, error="same format", code=2)
    route = ""
    try:
        # archives
        if sext in ("zip","7z","tar.gz") and tgt in ("zip","7z","tar.gz"):
            return out(True, archive_convert(src, sext, tgt, outdir), "archive")
        # fonts
        if sext in ("ttf","otf","woff","woff2") and tgt in ("ttf","otf","woff","woff2"):
            return out(True, via_fonttools(src, tgt, outdir), "fonttools")
        # subtitles
        if sext in SUB_SRC and tgt in SUB_TGT:
            text = read_text(src)
            cues = parse_ass(text) if sext in ("ass","ssa") else (parse_vtt(text) if sext == "vtt" else parse_srt(text))
            if not cues: raise RuntimeError("no cues parsed")
            body = cues_to_srt(cues) if tgt == "srt" else (srt_to_vtt(cues) if tgt == "vtt" else cues_to_ass(cues))
            return out(True, write_text(dst_path(src, tgt, outdir), body), "subtitle-script")
        # images
        if sext in IMG_EXTS | {"psd"} and tgt in IMG_EXTS:
            return out(True, via_pillow(src, tgt, outdir), "pillow")
        if sext in IMG_EXTS and tgt == "pdf":
            return out(True, images_to_pdf([src], outdir, os.path.splitext(base)[0]), "pillow-pdf")
        if sext == "svg" and tgt in ("png","pdf"):
            return out(True, via_libreoffice(src, tgt, outdir), "libreoffice-svg")
        # audio / video
        if sext in AUD_EXTS and tgt in AUD_EXTS:
            return out(True, via_ffmpeg(src, tgt, outdir), "ffmpeg")
        if sext in VID_EXTS and tgt in VID_EXTS:
            return out(True, via_ffmpeg(src, tgt, outdir), "ffmpeg")
        if sext in VID_EXTS and tgt in AUD_EXTS:
            return out(True, via_ffmpeg(src, tgt, outdir, ["-vn"]), "ffmpeg-extract-audio")
        if sext in VID_EXTS and tgt == "gif":
            return out(True, via_ffmpeg(src, tgt, outdir, ["-t","3","-vf","fps=10,scale=320:-1"]), "ffmpeg-gif")
        if sext in VID_EXTS and tgt in ("png","jpg"):
            return out(True, via_ffmpeg(src, tgt, outdir, ["-frames:v","1"]), "ffmpeg-frame")
        # pdf source
        if sext == "pdf":
            if tgt == "txt":
                return out(True, write_text(dst_path(src, tgt, outdir), pdf_to_text(src)), "pdf-text")
            if tgt == "md":
                return out(True, write_text(dst_path(src, tgt, outdir), pdf_to_text(src)), "pdf-text-md")
            if tgt in ("png","jpg"):
                return out(True, pdf_to_images(src, tgt, outdir), "pdf-render")
            if tgt == "docx":
                paras = [l for l in pdf_to_text(src).split("\n")]
                return out(True, text_to_docx(paras, dst_path(src, tgt, outdir)), "pdf-text-docx")
            out(False, error=f"unsupported: pdf -> {tgt}", code=2)
        # data via pandas
        if sext in DATA_EXTS and tgt in ("xlsx","csv","tsv","json","xml","yaml","html","md","ods"):
            return out(True, via_pandas(src, sext, tgt, outdir), "pandas")
        # text family
        if sext in ("txt","md") and tgt in ("txt","md"):
            return out(True, write_text(dst_path(src, tgt, outdir), read_text(src)), "text-copy")
        if sext == "md" and tgt == "html":
            return out(True, write_text(dst_path(src, tgt, outdir), md_to_html(read_text(src))), "markdown")
        if sext == "html" and tgt == "md":
            return out(True, write_text(dst_path(src, tgt, outdir), html_to_md(read_text(src))), "markdownify")
        if sext == "html" and tgt == "txt":
            return out(True, write_text(dst_path(src, tgt, outdir), strip_tags(read_text(src))), "html-strip")
        if sext == "docx" and tgt == "md":
            tmp = via_libreoffice(src, "html", outdir)
            md = html_to_md(read_text(tmp)); os.remove(tmp)
            return out(True, write_text(dst_path(src, tgt, outdir), md), "docx-html-md")
        if sext == "md" and tgt == "epub":
            paras = read_text(src).split("\n")
            title = next((l.lstrip("# ").strip() for l in paras if l.startswith("#")), "Untitled")
            return out(True, make_epub(title, paras, dst_path(src, tgt, outdir)), "epub-build")
        if sext == "epub":
            paras = epub_to_paragraphs(src)
            if tgt == "txt": return out(True, write_text(dst_path(src, tgt, outdir), "\n".join(paras)), "epub-text")
            if tgt == "md": return out(True, write_text(dst_path(src, tgt, outdir), "\n\n".join(paras)), "epub-text-md")
            if tgt == "docx": return out(True, text_to_docx(paras, dst_path(src, tgt, outdir)), "epub-docx")
        # slides to image via pdf chain
        if sext in ("ppt","pptx","odp") and tgt in ("png","jpg"):
            tmp_pdf = via_libreoffice(src, "pdf", outdir)
            dst = pdf_to_images(tmp_pdf, tgt, outdir); os.remove(tmp_pdf)
            return out(True, dst, "slides-pdf-render")
        if sext in ("html", "htm") and tgt == "docx":
            md = html_to_md(read_text(src))
            paras = [l.strip() for l in md.split("\n")]
            return out(True, text_to_docx(paras, dst_path(src, tgt, outdir)), "html-md-docx")
        # libreoffice direct
        if sext in LO_SRC and tgt in LO_TGT:
            return out(True, via_libreoffice(src, tgt, outdir), "libreoffice")
        if sext == "md" and tgt == "docx":
            from docx import Document
            d = Document()
            for line in read_text(src).split("\n"):
                t = line.strip()
                if not t: continue
                t = t.replace("**", "").replace("`", "")
                if t.startswith("## "): d.add_heading(t[3:], level=2)
                elif t.startswith("# "): d.add_heading(t[2:], level=1)
                elif t.startswith("- ") or t.startswith("* "): d.add_paragraph(t[2:], style="List Bullet")
                else: d.add_paragraph(t)
            dst = dst_path(src, tgt, outdir); d.save(dst)
            return out(True, dst, "md-docx-direct")
        # md -> pdf/odt via html chain through libreoffice
        if sext == "md" and tgt in ("pdf","odt"):
            tmp = write_text(os.path.join(outdir, "tmp_chain.html"), md_to_html(read_text(src)))
            dst = via_libreoffice(tmp, tgt, outdir)
            os.remove(tmp)
            final = dst_path(src, tgt, outdir)
            if dst != final: os.rename(dst, final)
            return out(True, final, "md-html-lo")
        if sext == "epub" and tgt == "pdf":
            tmp = text_to_docx(epub_to_paragraphs(src), os.path.join(outdir, "tmp_chain.docx"))
            dst = via_libreoffice(tmp, "pdf", outdir)
            os.remove(tmp)
            final = dst_path(src, tgt, outdir)
            if dst != final: os.rename(dst, final)
            return out(True, final, "epub-docx-lo")
        out(False, error=f"unsupported: {sext} -> {tgt}", code=2)
    except SystemExit:
        raise
    except Exception as e:
        out(False, error=str(e)[:400], route=route, code=3)

if __name__ == "__main__":
    main()
