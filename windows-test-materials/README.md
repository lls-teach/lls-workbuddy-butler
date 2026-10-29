# Windows 真机验证测试物料

> 来源：2026-10-29 全库 37 支 skill 实测（Linux 沙盒）中用过的测试输入与复验产物。
> 用途：Windows 真机验证时直接用这些物料跑，不用重新造。

## 包含什么

- `lls-convert/inputs/`、`lls-aizhijian/inputs/`、`lls-fapiao/inputs/`、`lls-aiwei/inputs/`、
  `lls-biaoshu/inputs/`、`lls-huiyi/inputs/`、`lls-timu/inputs/`、`lls-wenan/inputs/`、
  `lls-htmlppt/inputs/`：各支实测用过的测试输入（含中文文件名、空格与特殊字符、
  空文件、CRLF/BOM、超大文件等边缘探针输入，Windows 验证时重点跑这些）。
- `lls-zimu/input.srt`、`lls-mdppt/input.md`、`lls-shuzhi/input.json`：三支的测试输入。
- `lls-jianli/resume.docx`：简历复验产物，Windows 上用 Word 打开核对宋体/雅黑渲染。
- `lls-naotu/basic.mm`：思维导图复验产物，Windows 上用 XMind、幕布或 FreeMind 导入核对。
- `TEST-REPORT-2026-10-29.md`：全库实测报告（含每支结论、修复清单、需用户协助清单、待决策事项），
  Windows 验证按报告里的“需用户协助”清单逐项跑。

## 故意没放进来的东西

- `~/workspace/skillhub-test/runs/` 全量证据（3.0GB、11 万多个文件）：大头是 venv、
  node_modules、浏览器与字体等环境文件，以及跑出来的过程输出，Windows 上跑冒烟会自己重新生成，
  不需要也不应该进仓库。
- 仓库里已有的样本库 `lls-base-skills/real-tests/`（已入库，克隆即得），不在此重复放。

## Windows 上怎么用

1. 克隆本仓库，见 `windows-handoff.md`。
2. 按 `windows-handoff.md` 第三节清单逐支跑；跑某支时若需测试输入，先到本目录对应 skill 下取。
3. 跑出来的输出与 Linux 侧产物逐项比对关键点（不是逐字节比对）；失败项记录报错原文反馈回来。
