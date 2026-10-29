#!/usr/bin/env python3
import shutil, importlib, json, os
def find_soffice():
    for p in (shutil.which("soffice"),
              "/Applications/LibreOffice.app/Contents/MacOS/soffice",
              "/usr/lib/libreoffice/program/soffice",
              "/opt/homebrew/bin/soffice"):
        if p and os.path.exists(p):
            return p
    return None
bins = {"soffice": bool(find_soffice()), "ffmpeg": bool(shutil.which("ffmpeg")), "ffprobe": bool(shutil.which("ffprobe"))}
mods = {}
# brotli 是 woff2 编解码的硬依赖，缺了 ttf->woff2 / woff2->ttf 直接报错
for m in ["PIL","docx","openpyxl","pandas","pptx","pypdf","pdfplumber","fitz","fontTools","py7zr","markdown","markdownify","odf","xlrd","yaml","tabulate","brotli"]:
    try: importlib.import_module(m); mods[m] = True
    except Exception: mods[m] = False
print(json.dumps({"binaries": bins, "python": mods, "ready": all(bins.values()) and all(mods.values())}, indent=2))
