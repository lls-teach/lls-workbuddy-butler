---
name: lls-convert
display_name: 格式转换大全
display_name_en: Format Converter Butler
description: 本地格式转换：文档/表格/演示/图片/音视频/字幕/数据/字体/压缩包互转，PDF 与 Markdown 双中枢
description_zh: 本地格式转换大全：78 种主力格式互转，文件不离开设备；文档、表格、演示、图片、音视频、字幕、数据、字体、压缩包，一句话说清要什么格式直接转
description_en: "Local format conversion encyclopedia: documents, sheets, slides, images, audio/video, subtitles, data, fonts and archives converted locally. Files never leave the device."
version: 1.0.3
author: lhg
---

# 格式转换大全（lls-convert）

一句话说清要什么，这里直接转。全部本地运行，文件不上传、不离开设备。

## 何时用

用户要把文件换个格式：转 PDF、PDF 转 Word、表格转 JSON、视频提音频、图片换格式、字幕换格式、字体转 web 格式、压缩包换格式，或只说场景（「发微信用」「能上 Kindle」「要能编辑的版本」）。

## 怎么执行

引擎：`scripts/convert.py <输入文件> <目标扩展名> -o <输出目录>`，输出一行 JSON：`{"ok": true/false, "output": 路径, "route": 通道, "error": 信息}`。

1. 源格式看文件扩展名，不用问用户。
2. 目标格式：用户明说了就用；只说场景按下表推断，推断不唯一时只问一句。
3. 批量（≥2 个文件）逐个调用引擎；≥10 个先列清单让用户确认再跑（🔴 CHECKPOINT）。
4. 引擎返回 `ok:false` 且原因为 unsupported 时，如实告诉用户「X→Y 暂不支持」，并给出支持矩阵里的替代路径；**不许用别的方式硬凑一个坏文件充数**。
5. 转完报告：源→目标、通道、产物路径；是链式转换（如 PDF→docx 是文本重排版）要明示保真程度。

## 场景推断表

| 用户说 | 目标 |
|---|---|
| 发微信/发群里 | 图片→jpg，视频→mp4，文档→pdf |
| 打印 | pdf |
| Kindle 看 | epub（源是 pdf 时先提醒排版会变文本流） |
| 要能编辑/改 | docx / xlsx / pptx（按源类别） |
| 放进网页 | 图片→webp，字体→woff2，文档→html |
| 做字幕/剪辑用 | srt（B站/剪映）或 vtt（网页） |
| 给程序用/接口要 | 表格数据→json，文本→md |

## 支持范围（诚实清单，以测试全绿为准）

- 文档：doc/docx/odt/rtf/txt/md/html/pdf/epub 互转（pdf→docx 为文本重排，复杂版式会变）
- 数据：xls/xlsx/ods/csv/tsv/json/xml/yaml 互转 + 转 md/html/pdf
- 演示：ppt/pptx/odp 互转 + 转 pdf/png/jpg
- 图片：png/jpg/webp/bmp/tiff/ico/gif 互转 + 转 pdf；svg→png/pdf
- 音频：mp3/wav/flac/aac/ogg/m4a/wma/aiff/opus 互转
- 视频：mp4/mov/avi/mkv/webm/flv/wmv/m4v/3gp/mpeg 互转 + 提音频/抽帧/转 gif
- 字幕：srt/vtt/ass/ssa 互转（ssa 只作源）
- 字体：ttf/woff/woff2 与 otf(仅 CFF 源) 互转；**ttf↔otf 不支持**（换轮廓类型需 cu2qu 重画字形，引擎不做，会返回 unsupported 而不是产出改名的假文件）
- 压缩：zip/7z/tar.gz 互转（打包解包）
- 不支持：pages/key/numbers 转入（苹果专有，无本地引擎）、RAW 转入、带 DRM 的电子书转出、一切跨界无意义组合（如字体→视频）——遇到直接说明

完整逐对矩阵见 `references/supported-matrix.md`，由配套测试集全绿结果生成（测试档案存仓库 real-tests/convert）；测试不过的对不在矩阵内。

## 环境依赖（首次运行自检）

必需：LibreOffice（soffice）、ffmpeg/ffprobe、Python 包（Pillow、python-docx、openpyxl、pandas、python-pptx、pypdf、pdfplumber、PyMuPDF、fonttools、**brotli**（woff2 编解码依赖）、py7zr、markdown、markdownify、odfpy、xlrd）。缺哪样先补装再转，补不上就如实报缺哪样，不假装能转。命令：`python3 scripts/check_env.py`。

## 红线

- 不承诺未测过的转换对；宣传数字只用实测矩阵
- 不处理 DRM 绕过；azw3 等受保护格式只做合法说明
- 同名文件不覆盖：目标已存在时自动改名为 `名字-1.ext`，确认要覆盖才加 `--force`
