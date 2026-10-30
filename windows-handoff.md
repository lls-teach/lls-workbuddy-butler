# Windows 兼容性后续工作交接（真机验证用）

> 交接时间：2026-10-29 首版；**2026-10-30 真机进展与剩余任务见本文末尾第七节 + `windows-test-materials/真机验证-进度与交接-2026-10-30.md`**。
> 交接对象：全库 37 支 skill 的 Windows 兼容性工作。
> 代码版本：本交接对应的修复已包含在本提交及之后版本中，克隆即得修复后代码。测试物料在 `windows-test-materials/`（见第六节）。

## 一、已完成（代码级，沙盒 Linux，无真机）

- 37 支全部做了 Windows 代码级审计（不是真机实测）：25 支兼容、2 支基本兼容、10 支需适配。
- 10 支需适配的代码级不兼容项已修完（见第二节），冒烟循环句 37/37 已补（”做冒烟测试直到问题解决”）。
- 完整测试报告：`~/workspace/skillhub-test/2026-10-29-skillhub-test-report.md`；各支证据：`~/workspace/skillhub-test/runs/<slug>/`。
- **2026-10-30 起真机实测已启动**：Windows 真机（win32 10.0.19045）已跑通 kanban 全链路（含浏览器渲染）、PaddleOCR 真实识别、convert/mdppt/jiaoan/jianli/lunwen/docx/xlsx/zimu/bangong 产物链路，并修掉 4 类真机暴露的兼容问题（详见第七节与测试报告真机章）。

## 二、10 支需适配（代码级已修，真机未验证）

| skill | 代码级已修的主要项 |
|---|---|
| lls-bangong 打工人四件套 | 路径、编码、外部工具调用 |
| lls-convert 格式转换大全 | 主要已知项（抽测 51 对全过；注意：结论不对矩阵宣称的 123 对背书） |
| lls-docpage 文档页生成 | docx 路线 2 处失败 |
| lls-reportp 图文报告页面 | PowerShell 与中文/空格路径相关项 |
| lls-fapiao 发票识别报销 | 文本提取、清单输出、依赖缺失提示 |
| lls-lunwen 论文排版 | 字体回退相关项 |
| lls-pdf PDF文档处理 | 代码与文档层面适配 |
| lls-pptx PPT演示文稿 | 3 处问题 |
| wb-open-platform-handbook 上架规范问答 | 文本层面适配 |
| wb-open-platform-handbook-pro 上架专家 | 文本层面 2 点 |

其余 27 支（25 兼容 + kanban、jiaoan 基本兼容）代码级已过，但仍需真机抽查关键链路（见第三节）。

## 三、Windows 真机验证清单（按支跑，记录通过/失败 + 报错原文）

### A. 必须在真机上验证的项

1. **Pro 上架专家**：按 `references/windows-smoke-test.md`，在 Windows 真机上跑 E-0 环境自举与 E 代上架全流程，反馈每一步结果与报错。
2. **bangong**：PowerShell 下跑一遍 venv + requirements 安装全流程；确认 LibreOffice 默认路径实际命中；确认微软雅黑/宋体在 reportlab 下的注册；确认 PaddleOCR 在 Windows 下的安装与模型下载；试一个含 Windows 保留字符的文件名并反馈报错表现。
3. **convert**：确认 Windows 默认路径探测是否真能找到你安装的 LibreOffice；确认 ffmpeg 是否在你的 PATH；确认 LibreOffice 在 Windows 下输出文件名大小写/扩展名是否与代码假定的 `base.tgt` 一致；试一条超长路径（旧版 260 字符限制）并反馈行为。
4. **reportp**：PowerShell 下用一条含中文与空格的路径跑一遍报告生成并反馈结果。
5. **zimu**：旧 GBK 终端跑一遍字幕清洗并反馈中文输出；双击 `.py` 确认文件关联与 shebang 表现；用个别老播放器打开 LF 换行字幕确认是否接受。
6. **jiaoan**：Windows 上跑一遍 `check`/`create` 全流程，并用 Word 打开生成的教案核对渲染。
7. **pptp**：真 Windows 上确认 Playwright 启动与回退候选命中、PowerShell/cmd 引号与旧控制台中文编码表现、超长路径行为、有无杀毒拦截，并反馈。
8. **mdppt**：Windows 上跑一遍 Markdown 转 PPT，并用 PowerPoint 打开核对。
9. **kanban**：Windows 上用浏览器打开生成的看板核对渲染；用一条含中文的长路径在旧版 cmd 下跑一遍并反馈。
10. **jianli**：在自己的机器上用 Word 打开 `runs/lls-jianli/resume.docx`，核对宋体/雅黑渲染是否与预期一致并反馈。
11. **naotu**：在装有 XMind、幕布或 FreeMind 的机器上导入 `runs/lls-naotu/out3/basic.mm`，核对层级与文字是否正确并反馈。
12. **lunwen**：用 Word 打开生成的论文排版产物核对渲染并反馈。
13. **docx**：在 Word/WPS 内打开转 PDF 后的渲染图人工核对；按引导做一次修订接受/拒绝并反馈裁决结果。
14. **xlsx**：打开重算后的工作簿，人工抽查一行公式结果是否正确并反馈。

### B. 其余 27 支：抽查关键链路

按各支 SKILL.md 的 SMOKE-TEST 协议跑一遍最小链路即可；重点看 PowerShell 下的 venv 安装、中文路径、输出文件是否正常生成。

## 四、Windows 上怎么跑（通用步骤）

1. 拿到代码（推后克隆，或直接拷工作区，见文首版本注意）。
2. PowerShell，Python 3.x（用 `py` 启动器或 `python`）。
3. 按各支 SKILL.md 第 0 步建 venv 并装 requirements（Windows 下：`py -m venv .venv`，`.venv\Scripts\Activate.ps1`，`pip install -r scripts/requirements.txt`）。
4. 转换类另需系统工具：LibreOffice（soffice 进 PATH）、ffmpeg/ffprobe；字体用 Windows 自带的微软雅黑/宋体。
5. 跑各支 SMOKE-TEST 与 test-prompts.json 用例；执行冒烟循环句：不过就定位、修复、重跑，直到通过。
6. 记录结果：每支通过/失败 + 失败报错原文 + 产物截图或文件，反馈回来。

## 五、Windows 常见坑位（验证时留意）

- cmd 不支持 `&&` 链式写法（代码级已拆行，真机复核是否还有残留）。
- PowerShell 与 cmd 引号规则不同；旧控制台 GBK 中文编码。
- 260 字符长路径限制（旧版 Windows）。
- 杀毒软件拦截脚本或 Playwright 启动。
- 双击 `.py` 的文件关联与 shebang 表现。
- LF 换行在老播放器/老工具里的接受度。
- LibreOffice 输出文件名大小写/扩展名与代码假定是否一致。
- PaddleOCR 模型下载（数百 MB，需联网并确认）。

## 六、后续要做的事（按顺序）

1. **代码版本（已定）**：修复已随本提交推送到 GitHub，Windows 上直接克隆最新 main 即可，不用再拷工作区。
2. **Windows 真机验证**：按第三节清单逐支跑，记录结果反馈回来。
3. **反馈后修复**：真机失败项再做代码级修复 → 再推 → 再验，直到真机全过。
4. **结论升级**：真机全过后，测试报告里的 Windows 结论从”代码级”升级为”真机已验证”，并更新质量框架交付记录。
5. **不阻塞 Windows 线的其他事**：13 条待决策事项（convert 的 ok:true 误判、docx 的 --stdin 路由不符、jiaoan 示例命令不符、Pro 案例库旧 slug 是否改等）另行拍板；四件套 WorkBuddy 提交等明日限额恢复后下令提交。

## 七、真机实测进展（2026-10-30，Windows 本机）

> 详细逐项结论与证据：`windows-test-materials/TEST-REPORT-2026-10-29.md` 文末「Windows 真机验证进展」章；
> 剩余任务的完整操作协议：`windows-test-materials/真机验证-进度与交接-2026-10-30.md`；
> 物证归档：`lls-base-skills/real-tests/<skill>/windows-real/` 与 `real-tests/windows-real-render/`（见 `windows-real-README.md`）。

**已真机跑通**：lls-kanban（中文+空格路径生成 → node 校验全绿 → 浏览器渲染正常，KPI 与源数据逐项吻合）、lls-mdppt、lls-jiaoan、lls-jianli、lls-lunwen、lls-docx、lls-xlsx、lls-zimu、lls-convert（中文目录/空格文件名）、lls-bangong（含 PaddleOCR 真实识别）。

**真机暴露并已修复的 4 类问题**（提交 `4bc3df6`，已推 GitHub）：

1. PaddleOCR 在 paddlepaddle 3.x 上 oneDNN/PIR 推理崩溃（`NotImplementedError: ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`）→ win32 下 `enable_mkldnn=False`。修复后真机复跑识别正确。
2. paddleocr 2.x / 3.x 接口不兼容（3.x 的 `.ocr()` 不收 `cls`、移除 `show_log`）→ 抽 `ocr_lines()` 统一两版调用，`fapiao_batch.py` 同步。
3. Windows 保留字符/设备名只在保存阶段报裸 `OSError` → `guard_overwrite()` 在 win32 下提前校验并给可读错误（bangong 的 docx/pdf/pptx/xlsx 四支）。
4. lls-mdppt 把转换脚本写入的 AI 标注注释渲染成了幻灯片内容 → `parse_md` 跳过整行 HTML 注释。

另补 `lls-jiaoan/scripts/requirements.txt`（python-docx）。

**剩余任务（按序）**：① A9 超长中文路径 cmd 测试（深路径基座已就绪，**外层 shell 严禁 cd 进深路径**，协议见进度交接文件）；② A4 reportp 的 PowerShell 中文+空格路径；③ A7 pptp 的 Playwright 启动/引号编码/长路径；④ A1 Pro 上架专家 E-0 自举；⑤ A11 naotu 的 .mm 结构核对；⑥ 其余 27 支抽查关键链路；⑦ 全绿后把各支 Windows 结论从”代码级”升级为”真机已验证”。

**真机测试自身的一条硬教训**：Windows 上做超长路径测试时，测试工具自身的 cwd 一旦进入超 260 字符路径，进程将无法启动（本次实测导致会话 shell 全灭）。正确姿势是外层 shell 始终留在短路径，进深路径一律用 `cmd /c “cd /d <深路径> && <命令>”` 子进程。

## 七、参考

- 测试报告：`~/workspace/skillhub-test/2026-10-29-skillhub-test-report.md`
- 各支证据：`~/workspace/skillhub-test/runs/<slug>/`（第二阶段 `phase2/`，循环句 `smokeloop/`）
- 复验产物：`runs/lls-jianli/resume.docx`、`runs/lls-naotu/out3/basic.mm`
- 质量框架：`~/workspace/butler-scan/skill-quality-framework.md`
- GitHub 仓库：https://github.com/lls-teach/lls-workbuddy-butler（main 分支，本提交及之后版本含全部修复与测试物料）
