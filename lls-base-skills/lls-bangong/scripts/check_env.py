#!/usr/bin/env python3
import shutil, importlib, json
bins = {b: bool(shutil.which(b)) for b in ("soffice", "ffmpeg", "ffprobe")}
mods = {}
for m in ["PIL","docx","openpyxl","pandas","pptx","pypdf","pdfplumber","fitz","fontTools","py7zr","markdown","markdownify","odf","xlrd","yaml","tabulate"]:
    try: importlib.import_module(m); mods[m] = True
    except Exception: mods[m] = False
print(json.dumps({"binaries": bins, "python": mods, "ready": all(bins.values()) and all(mods.values())}, indent=2))
