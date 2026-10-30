# Windows 真机验证证据归档（2026-10-30）

> 来源：Windows 真机实测（win32 10.0.19045，Python 3.14 venv + Python 3.12 Paddle venv）。
> 用途：作为「Windows 真机已验证」的物证留存，供后续复核与回归对照。
> 详细结论见 `windows-test-materials/TEST-REPORT-2026-10-29.md` 文末「Windows 真机验证进展」章。

## 目录约定

- `real-tests/<skill>/windows-real/` — 该 skill 真机跑出的产物（沿用各支既有 `out/` 风格，用 `windows-real` 区分于 Linux 沙盒产物）。
- `real-tests/windows-real-render/` — LibreOffice headless 转 PDF 后出的渲染图与 PDF（跨 skill 的渲染核对物证集中存放）。

## 已归档的验证内容

| skill | 产物 | 验证点 |
|---|---|---|
| lls-kanban | `中文 看 板/销售看板/index.html`、`dashboard_data.json`、`data/snapshots/revenue.csv` | 中文+空格路径生成、node 校验全绿、浏览器渲染正常（KPI 与 CSV 逐项吻合，中文 segment 正常显示） |
| lls-convert | `中文 目录 测试/`（演 示.pdf/pptx、音 频.mp3） | 中文目录 + 空格文件名下的多格式转换 |
| lls-mdppt | 渲染 产物.pptx、演示 产物.pptx、演示 复验.pptx、input.md、大纲.md | Markdown 转 PPT（含注释不渲染的修复验证） |
| lls-jiaoan | 教案 中文 产物.docx、预检报告 中文.md、教学设计.json | check/create 全流程 + 中文路径 |
| lls-jianli | 张三 简历.docx、简历数据.json | 简历 docx 生成（宋体/雅黑设置） |
| lls-lunwen | 论文 排版产物.docx、预检报告 中文.md、论文正文.md | 论文排版结构生成 |
| lls-docx | 合同 修订版.docx | docx 修订流程产物 |
| lls-xlsx | 公式表.xlsx | 公式写入与重算链路 |
| lls-bangong | 中文 测试.pdf、tiny.pdf、t.csv、OCR 输出.txt | 中文文件名 + PaddleOCR 真机识别（产物内容正确） |
| lls-zimu | `中文 路径 测试/`（输入 文件.srt、输出 清洗.srt） | 中文字幕路径下的清洗 |

渲染图（`windows-real-render/`）：docx_rev_p1、jianli_p1、jiaoan_p1/p2、lunwen_p1、mdppt_p1/p2、mdppt_fixed_p2 各 PNG，以及 合同 修订版.pdf、张三 简历.pdf、教案 中文 产物.pdf、演示 产物.pdf、演示 复验.pdf、论文 排版产物.pdf。

## 第二轮新增（2026-10-30 续测：A9 收尾 + A4/A7/A11 + B 组 21 支）

| skill | 产物 | 验证点 |
|---|---|---|
| lls-kanban | `a9-超长路径测试-日志.txt` | 308 字符深路径逐层测试：cmd cd 边界（239 通过/262 失败）、CreateProcess 超长 cwd（WinError 267）、python 普通路径与 `\\?\` 前缀对比、216 字符目录正向全链路（index.html 1,072,296 字节 + node 22 项全绿） |
| lls-reportp | `中文 报告 页面/index.html`、`截图-http协议.png`、`截图-file协议.png` | 中文+空格路径；HTTP 与 file:// 双渲染；doc.js 目录轨 6 锚点；ECharts 双线图与中文表格 |
| lls-pptp | `季度复盘.html`、`幻灯片-01/02.png`、`a7-真机测试日志.txt` | 校验 + PDF 导出（Playwright 回退系统 Chrome/Edge）；超长路径导出失败原文；pptx 私有包限制 |
| lls-naotu | `课程大纲.md`、`课程导图.mm`、`课程导图.html`、`截图-导图html.png` | .mm XML 良构/无 BOM、32 节点逐字一致、最大深度 3；HTML 树渲染 |
| lls-docpage | `中文 测试/`（主题冒烟.html/.pdf/.docx/.clean.html） | PDF 导出（--chrome 系统 Chrome）；docx 静默失败修复后导出成功 36,674 字节 |
| lls-aiwei / lls-baoshui / lls-biaoshu / lls-fenjing / lls-hetong / lls-htmlppt / lls-huiyi / lls-kejian / lls-koushuo / lls-pingyu / lls-shuzhi / lls-timu / lls-wenan / lls-xuanti / lls-zhouba / lls-shujv / lls-gongwen / lls-pdf / lls-pptx / lls-fapiao | 各支 `windows-real/中文 测试/` 下 1–4 个产物 | 中文+空格路径最小链路：产物生成、JSON 良构、xlsx/pptx/docx 结构有效、Office 产物经 LibreOffice 转 PDF 人眼核对 |

逐支命令、退出码与结论见 `windows-real-b-抽查日志.txt`。


## 归档说明

- **未归档**：`lls-kanban` 的 `echarts.min.js`（1MB，随技能包自带，无需重复入库）、`lls-kanban` 的 `dashboard.py`（技能自带模板）、`.venv` 与 `node_modules`（环境文件）；超长路径测试目录已在 A9 测完后删除（结论与日志见 `lls-kanban/windows-real/a9-超长路径测试-日志.txt`），不再留盘以免后续会话误入。
- 产物文件名保留中文与空格原样——这正是被测兼容性的一部分（Windows 保留字符、设备名、GBK 控制台编码问题都与此相关）。
