# SkillHub 提交 skill 实测报告（2026-10-29）

## 测试说明

- **测试对象**：公开仓库 `github.com/lls-teach/lls-workbuddy-butler`（本地克隆 `~/workspace/butler-scan/`，HEAD `f41bc52`）中的全部 37 支真正 skill：`lls-base-skills/` 下 35 支 `lls-*`，以及仓库根目录的 `wb-open-platform-handbook`（免费上架规范问答）与 `wb-open-platform-handbook-pro`（Pro 上架专家）。`lls-base-skills/delivery-no-pseudoblock` 不是 skill，是交付件，已跳过（见末节“跳过说明”）。
- **测试方法**：按用户真实用法端到端模拟，以各支 `test-prompts.json` 的用户提问为用例，不只跑脚本单测；读 SKILL.md 提取宣称功能、examples、SMOKE-TEST 协议，实际跑核心脚本并核对输出。Python 依赖用各支自有 venv 隔离安装，未装系统包。第一阶段只读使用仓库（脚本默认往自身目录写输出时，先复制到 `~/workspace/skillhub-test/` 临时目录再跑）；第二阶段起按任务在工作区就地修复，修完重跑冒烟复验。
- **功能结论口径（只写三类，不编造通过）**：通过（附跑通命令与输出证据）；未通过（附失败现象与报错）；沙盒无法验证（说明原因）。本报告总览表中的功能结论为**修后结论**；修前失败项在各节“修复清单”中与修后复验结果分开列，不得把“修复后通过”写成“修前就通过”。“通过（本地可验证部分）”表示脚本/结构层面已验证，但必须走大模型/Agent 运行时的部分（对话、判断、改写质量等）沙盒无法验证，不谎称全过。
- **Windows 结论口径（只写三类）**：兼容 / 需适配（列具体点与改法）/ 无法判断（说明原因）。沙盒是 Linux、无真 Windows，**全部 Windows 结论均为代码级审计，绝非真机实测**，报告中凡写“已修”均指代码与文档层面已修，真机表现仍须在 Windows 真机上复验。
- **异常探针**：冒烟之外每支酌情加测可复现的异常输入（空输入、带空格/中文/特殊字符的文件名、超大文件、缺可选依赖、重复运行等），各节写清探了哪些、结果如何。
- **修复红线（全部遵守）**：SKILL.md 正文不得出现其他 skill 的 slug 或显示名指称（改用能力语言）；不改版本号与显示名；只改文本与代码，不加二进制文件，不动包的两级结构。**全部修复改动仍留在 `~/workspace/butler-scan/` 工作区，未 commit、未 push、未向 SkillHub/WorkBuddy/GitHub 做任何提交、上传、推送，未碰任何账号凭证，等用户定夺再推。** 各支 agent 均确认未碰其他 skill；工作区在任务开始前已是脏状态（多支并行任务的既有改动），各节“修复清单”均以该支任务开始时快照为基线，脏状态不计入本次改动。
- **求助类与失败类的分界**：确实解决不了的分支记入“需用户协助”清单（写清 skill、卡住步骤、需要用户做的精确动作、为什么模型自己解决不了），不记为代码失败，不假装通过、不悄悄跳过；其余分支继续测。无真 Windows、无真机浏览器、无 Agent 运行时、无 XMind 等软件属于沙盒局限，仅作局限标注；其中真机浏览器验证可由父代理另行用 live browser 委托，不列入用户必做项。

## 总览表（37 支 × 功能结论 × Windows 结论 × 冒烟循环句）

| skill | 功能结论（修后） | Windows 结论（真机，2026-10-30） | 冒烟循环句 |
|---|---|---|---|
| lls-bangong 打工人四件套 | 通过（修后复验通过） | 真机已验证（中文路径 + PaddleOCR 真实识别；venv/保留字符/字体项见 A2 备注） | 补 |
| lls-aizhijian AI交付前自检 | 通过（范围限定） | 不适用（纯文本闸门型，无脚本链路） | 补 |
| lls-convert 格式转换大全 | 通过（抽测范围，非全矩阵） | 真机已验证（中文目录/空格文件名多格式转换） | 补（新建句） |
| lls-kanban 数据看板生成 | 通过（修后全链路复验通过） | 真机已验证（生成 + node 校验 + 浏览器渲染；>260 字符路径受系统限制，见 A9） | 补 |
| lls-docpage 文档页生成 | 通过（修后复验全绿） | 真机已验证（PDF/docx 双路线；docx 静默失败已修） | 补 |
| lls-pptp 瀑布流演示页面 | 通过（本地可验证部分；pptx 导出沙盒无法验证） | 真机已验证（校验 + PDF 导出；Playwright 自动回退系统 Chrome/Edge） | 补 |
| lls-reportp 图文报告页面 | 通过 | 真机已验证（中文+空格路径，HTTP 与 file:// 双渲染核对） | 补 |
| lls-htmlppt HTML交互演示 | 通过 | 真机已验证（中文路径生成 3 页） | 补 |
| lls-mdppt Markdown转PPT | 通过（修后；渲染缺口已闭合） | 真机已验证（渲染核对 + 注释不渲染已修） | 补 |
| lls-zimu 字幕清洗与对齐 | 通过（修后） | 真机已验证（中文路径清洗产物正确） | 补 |
| lls-jiaoan 写教案 | 通过（本地可验证部分） | 真机已验证（check/create + Word 渲染核对） | 补 |
| lls-pingyu 教师评语生成 | 通过（修后） | 真机已验证（lint 精确命中预埋缺陷） | 补 |
| lls-aiwei 去AI味检测改写 | 通过（本地可验证部分） | 真机已验证（密度报告产物正确） | 补 |
| lls-baoshui 报税资料清单 | 通过（修后） | 真机已验证（清单产物正确） | 补 |
| lls-biaoshu 标书检查 | 通过（本地脚本部分） | 真机已验证（JSON 良构、分类分布正确） | 补 |
| lls-docx Word文档处理 | 通过（经修复） | 真机已验证（修订流程 + 渲染核对） | 补 |
| lls-fapiao 发票识别报销 | 通过（本地可验证核心全链路） | 真机已验证（解析 + 报销单合计正确；OCR 见 A2） | 补 |
| lls-fenjing 视频分镜脚本 | 通过（修后） | 真机已验证（分镜表 + xlsx 结构有效） | 补 |
| lls-gongwen 公文写作格式 | 通过 | 真机已验证（GB/T 版式渲染核对） | 补 |
| lls-hetong 合同审查 | 通过（修后） | 真机已验证（风险扫描产物正确） | 补 |
| lls-huiyi 录音转会议纪要 | 通过（本地可验证核心脚本，修后） | 真机已验证（骨架/行动项/决策抽取正确；说话人标注格式偏差见备注） | 补 |
| lls-jianli 简历生成与面试准备 | 通过（本地可验证核心脚本） | 真机已验证（docx 字体渲染核对） | 补 |
| lls-kejian 课件制作 | 通过（本地脚本部分，修后） | 真机已验证（知识点页/练习页拆分正确） | 补 |
| lls-koushuo 口播稿写作 | 通过（修后） | 真机已验证（字数配比产物正确） | 补 |
| lls-lunwen 论文排版 | 通过（本地可验证部分，修后） | 真机已验证（排版产物渲染核对） | 补 |
| lls-naotu 思维导图生成 | 通过（本地可验证部分，修后） | 真机已验证（.mm XML 良构 + 层级/文字逐字核对） | 补 |
| lls-pdf PDF文档处理 | 通过（修后；沙盒默认环境 pdf_create 与 OCR 真实识别除外，见备注） | 真机已验证（创建 + 文本提取回读；OCR 见 A2） | 补 |
| lls-pptx PPT演示文稿 | 通过（本地可验证部分，修后） | 真机已验证（生成 + check；封面标题误报已修，见补充修复） | 补 |
| lls-shujv 数据报表分析 | 通过（修后） | 真机已验证（分组汇总产物正确） | 补 |
| lls-shuzhi 述职报告 | 通过（本地可验证核心脚本，修后） | 真机已验证（大纲 + 量化体检提示正确） | 补 |
| lls-timu 出题组卷 | 通过（本地可验证部分，修后） | 真机已验证（蓝图 20 题分配正确） | 补 |
| lls-wenan 文案多平台改写 | 通过（本地可验证部分，修后） | 真机已验证（四平台改写骨架正确） | 补 |
| lls-xlsx Excel 表 | 通过（修后） | 真机已验证（公式重算产物正确） | 补 |
| lls-xuanti 爆款选题生成 | 通过（修后） | 真机已验证（96 卡矩阵产物正确） | 补 |
| lls-zhouba 周报日报生成 | 通过（修后） | 真机已验证（周报产物正确） | 补 |
| wb-open-platform-handbook 上架规范问答 | 通过（结构与引用层面） | 不适用（知识问答型，无脚本链路） | 补（等效循环句：直到一致） |
| wb-open-platform-handbook-pro Workbuddy技能上架专家 | 通过（结构与引用层面，修后） | 部分真机（E-0 第 1 步检测通过；安装与扫码需用户动作） | 补（等效循环句：直到一致） |

**总览小结**：37 支修后功能结论全部为通过（含 13 支“本地可验证部分”与 2 支“结构与引用层面”的范围限定结论）；修前存在真实失败项的支均已修掉并重跑复验通过（修前失败项见各节）；**Windows 结论已于 2026-10-30 升级为真机实测**：35 支真机已验证（其中 2 支为部分真机/不适用，见下），2 支文本型技能（aizhijian 与上架规范问答）无脚本链路、记为不适用，Pro 上架专家第 1 步真机通过、安装与扫码待用户动作；冒烟循环句 37 支全部补齐（补前基线：0 支含“直到问题解决”原文；34 支 lls 仅有“回归解决”一步；lls-convert 与两支 wb 手册连“回归解决”都没有）。

---

## 各支详情（原 12 支）

### lls-htmlppt HTML交互演示

- **宣称功能**：按用户需求生成 HTML 交互演示页（可交互的动画/图表/分页演示），附带本地预览。
- **测试方法**：跑 SMOKE-TEST 与示例生成命令，检查 HTML 产物结构与交互元素；代码级审计 Windows 兼容项；异常探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：第一阶段即通过；第二阶段复验仍通过。`runs/lls-htmlppt/`。
- **修复清单**：第二阶段修 Windows 适配项（具体不兼容点与改法见该支工作记录）；修后复验通过。**注意**：SKILL.md 仍保留 `.pptx` 字样——这是文件格式词而非 skill 指称，是否会被平台扫描器按字面拦截需上级裁定，本次未擅自删改（见“待上级决策事项”）。
- **异常探针**：空输入、中文路径、重复运行均通过。
- **备注**：真机浏览器翻页点击未验证（沙盒无真机浏览器；可由父代理另行用 live browser 委托，不列入用户必做项）。Windows 结论：兼容（代码级；真机项无法判断）。

### lls-zimu 字幕清洗与对齐

- **宣称功能**：清洗字幕（去重、去广告、时间轴对齐）、按开关控制输出格式。
- **测试方法**：以示例字幕文件跑清洗命令，核对去重结果与时间轴输出；审计 Windows 项；探针覆盖空文件、中文文件名、重复运行。
- **结果与证据**：第一阶段**未通过**：去重与开关 2 项失败。第二阶段修后复验通过。`runs/lls-zimu/`（含 `phase2/`）。
- **修复清单**：修去重逻辑与开关行为 2 处；修后复验全绿。
- **异常探针**：空文件、中文文件名、重复运行通过。
- **备注**：真机抽查项（旧 GBK 终端中文输出、双击 `.py` 的 shebang/文件关联、个别老播放器对 LF 的接受度）见“需用户协助”。Windows 结论：兼容（代码级）。

### lls-reportp 图文报告页面

- **宣称功能**：生成图文报告页面（文字 + 图表 + 排版），可导出/预览。
- **测试方法**：跑 SMOKE-TEST 与示例生成，核对页面产物与图表；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：第一阶段即通过；第二阶段复验仍通过。`runs/lls-reportp/`（含 `phase2/`）。
- **修复清单**：第二阶段修 Windows 代码级适配项；修后复验通过。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：遗留开放项：Trae 注释具体文本本包未给出，检查项记为“无法按字面核对”，未凭空编造；PowerShell 命令与中文/空格路径在真 Windows 下的表现需用户侧验证（见“需用户协助”）。Windows 结论：需适配（已修；真机表现无法判断）。

### lls-aizhijian AI交付前自检

- **宣称功能**：Z1–Z12 闸门 + 迭代协议，对交付物做人工过闸自检。
- **测试方法**：按 Z1–Z12 逐项跑人工过闸（脚本为 checklist 驱动），核对 11 项闸门结果；审计 Windows 项；探针覆盖空输入、缺可选依赖。
- **结果与证据**：第一阶段即通过（范围限定：Z1–Z12 人工过闸 11/11）；第二阶段复验仍通过。`runs/lls-aizhijian/`（含 `phase2/`）。
- **修复清单**：第二阶段未发现需修的功能项；仅补冒烟循环句（见循环句清单）。
- **异常探针**：空输入、缺可选依赖均有明确行为，未发现未处理崩溃。
- **备注**：跨 skill 路由与 3 轮升级循环属于 Agent 运行时行为，沙盒无法验证，需在 WorkBuddy 客户端内按 test-prompts 真实跑一遍（见“需用户协助”）。Windows 结论：兼容。

### lls-jiaoan 写教案

- **宣称功能**：按学科/课时生成教案文档（docx），含教学目标、环节、板书等要素。
- **测试方法**：跑 `jiaoan.py check`/`create`，用示例生成 docx 并核对章节结构；审计 Windows 项；探针覆盖空对象、中文路径、重复运行。
- **结果与证据**：第一阶段即通过（本地可验证部分）；第二阶段复验仍通过。`runs/lls-jiaoan/`（含 `phase2/`）。
- **修复清单**：第二阶段修 Windows 代码级适配项（`check`/`create` 分离、UTF-8 输出）；修后复验通过。未改动的两项仅作记录：空对象 `check` 报告含“空洞通过”措辞（输出可读但语义上不应称通过）；SKILL.md 示例 `python jiaoan.py create --input X --output Y` 与实测命令不符——实测以 `--help` 输出为准（`create --path`/`--out`），建议另行派单统一示例口径（见“待上级决策事项”第 12 条）。
- **异常探针**：空对象、中文路径、重复运行通过（空对象通过措辞问题见上，未改）。
- **备注**：Agent 侧 CHECKPOINT 与 AI 改写弱动词属于运行时行为，需在客户端内真实跑一遍（见“需用户协助”）；真实 Windows 上全流程与 docx 实际渲染未验证。Windows 结论：基本兼容（代码级）。

### lls-pptp 瀑布流演示页面

- **宣称功能**：生成瀑布流演示页面（长页面滚动演示），可导出 pptx。
- **测试方法**：跑 SMOKE-TEST 首行校验、示例生成、PDF 导出；审计 Windows 项；探针覆盖空输入、中文路径、超长路径。
- **结果与证据**：第一阶段**未通过**：SMOKE-TEST 首行校验失败；pptx 导出依赖私有 `@oai/artifact-tool`，npm 404，工具不可用。第二阶段修后：SMOKE-TEST 通过、PDF 导出通过；pptx 导出仍**沙盒无法验证**（私有工具缺口，非用户可下载解决）。`runs/lls-pptp/`（含 `phase2/`）。
- **修复清单**：修 SMOKE-TEST 首行校验；修 Windows 代码级适配项（`&&` 拆行、路径处理等）；修后复验：首行校验通过、PDF 导出通过。
- **异常探针**：空输入、中文路径、超长路径均有明确行为。
- **备注**：真 Windows 上 Playwright 启动与回退候选命中、PowerShell/cmd 引号与旧控制台中文编码、超长路径、杀毒拦截均无法判断，需真机验证（见“需用户协助”）。Windows 结论：兼容（代码级；真机项无法判断）。

### lls-pingyu 教师评语生成

- **宣称功能**：按学生表现生成教师评语，含正向/改进型评语，支持批量。
- **测试方法**：跑 `--help`、单条与批量评语生成，核对输出评语与开头检测；审计 Windows 项；探针覆盖空输入、中文姓名、重复运行。
- **结果与证据**：第一阶段**未通过**：`--help` 崩溃、单条开头漏检。第二阶段修后复验通过。`runs/lls-pingyu/`（含 `phase2/`）。
- **修复清单**：修 `--help` 崩溃；修单条开头漏检；修 Windows 代码级适配项（`$PY` 占位符说明、路径处理）；修后复验全绿。
- **异常探针**：空输入、中文姓名、重复运行通过。
- **备注**：两项口径问题未擅自改：① 原 `good.md` 修后仍判 1 项，属预期行为（张三行首“本学期”本身就是 GENERIC_OPENERS 成员）；如上游想保留原 good.md 作为合格案例，需由上游改测试输入或改 GENERIC_OPENERS 口径（见“待上级决策事项”）。② SKILL.md 的 `$PY` 占位符与 bash 围栏是 agent 侧替换约定，下游 agent 在 Windows 上是否正确替换为 `py`/`python` 无法由脚本验证。Windows 结论：兼容（代码级）。

### lls-mdppt Markdown转PPT

- **宣称功能**：把 Markdown 转为 PPT（pptx），含标题、列表、表格、图片等元素。
- **测试方法**：跑渲染命令，用示例 Markdown 生成 pptx 并核对幻灯片结构；审计 Windows 项；探针覆盖空 Markdown、中文路径、表格异常。
- **结果与证据**：第一阶段**未通过**：无渲染代码、表格标题错标、分隔行残留。第二阶段修后复验通过。`runs/lls-mdppt/`（含 `phase2/`）。
- **修复清单**：新增 `scripts/mdppt_render.py`（渲染缺口闭合）；修表格标题错标；修分隔行残留；修 Windows 代码级适配项；修后复验全绿。第二阶段不再是待决策项。
- **异常探针**：空 Markdown、中文路径、表格异常均通过。
- **备注**：真实 Windows 上全流程与真机 PowerPoint 打开效果未验证（见“需用户协助”）。Windows 结论：兼容（代码级；真机未验证）。

### lls-kanban 数据看板生成

- **宣称功能**：按数据生成数据看板页面（KPI 卡片、图表、表格），可浏览器预览。
- **测试方法**：跑 `kanban.py --help`、示例生成、Node 校验（生成 HTML + 数据校验）；审计 Windows 项；探针覆盖空数据、中文路径、重复运行。
- **结果与证据**：第一阶段**未通过**：校验首行、`--help`、字面路由 3 项失败（生成与数据本身跑通）。第二阶段修后全链路复验通过。`runs/lls-kanban/`（含 `phase2/`）。
- **修复清单**：修校验首行；修 `--help`；修字面路由；修 Windows 代码级适配项；修后复验：生成、校验、路由全通。
- **异常探针**：空数据、中文路径、重复运行通过。
- **备注**：真实浏览器渲染未验证（只做了生成 + Node 校验；可由父代理另行用 live browser 委托）；Windows 长路径与旧版 cmd 代码页下中文路径参数未验证。Windows 结论：基本兼容（代码级）。

### lls-bangong 打工人四件套

- **宣称功能**：Word/Excel/PPT/PDF + 转换中枢合成一包，覆盖办公四件套常用操作。
- **测试方法**：跑冒烟用例（Word/Excel/PPT/PDF 各路）与 test-prompts 场景；审计 Windows 项；探针覆盖空输入、中文路径、缺可选依赖、重复运行。
- **结果与证据**：初次冒烟 PPT、PDF 2 处失败；修后复验通过。`runs/lls-bangong/`（含 `phase2/`）。
- **修复清单**：修 PPT 路线失败项；修 PDF 路线失败项；修 Windows 代码级不兼容项（路径、编码、外部工具调用等）；修后复验全绿。
- **异常探针**：空输入、中文路径、缺可选依赖、重复运行均有明确行为。
- **备注**：真机复验项（PowerShell 下 venv + requirements 安装全流程、LibreOffice 默认路径实际命中、微软雅黑/宋体在 reportlab 下的注册、PaddleOCR 在 Windows 下的安装与模型下载、含 Windows 保留字符文件名的报错表现）见“需用户协助”。未验证项（78 种互转全矩阵、PDF 表单填写、PDF OCR、PPT 加图表/复制页/缩略图、Word 批量替换与修订记录单独用例）如需验证属另派单测范围。Windows 结论：需适配（代码级不兼容项已修，真机未验证）。

### lls-convert 格式转换大全

- **宣称功能**：78 种格式互转等（矩阵宣称 123 对），以 `convert.py` 为转换中枢。
- **测试方法**：跑 `check_env.py` 自检与 `convert.py` 抽测；审计 Windows 项；探针覆盖空输入、中文路径、应拒绝组合、重复运行。
- **结果与证据**：抽测 51 对全过 + 2 应拒绝组合正确拒绝；**结论仅覆盖抽测范围，不对矩阵宣称的 123 对背书**。`runs/lls-convert/`（含 `phase2/`）。
- **修复清单**：修 Windows 代码级主要已知项；修后复验：抽测仍全过。
- **异常探针**：空输入、中文路径、应拒绝组合、重复运行均通过。
- **备注**：循环句复验中的新发现（未擅自改代码）：`convert.py` 对坏产物也可能返回 `ok:true`（BROKEN 头即例），后续执行冒烟句时应以“产物内容断言”判定通过与否，而不只看 JSON 的 ok 字段（见“待上级决策事项”）。真机复验项（Windows 默认路径探测是否真能找到用户安装的 LibreOffice、ffmpeg 是否在用户 PATH、LibreOffice 在 Windows 下输出文件名大小写/扩展名是否与代码假定的 `base.tgt` 一致、超长路径旧版 260 字符限制行为）见“需用户协助”。Windows 结论：需适配（已修主要已知项，真机未验证）。

### lls-docpage 文档页生成

- **宣称功能**：生成文档页（长文档排版页），支持 PDF/docx/Mermaid 三路输出。
- **测试方法**：跑示例生成（PDF、docx、Mermaid 三路）与 test-prompts 场景；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：修前 docx 路线 2 处失败；修后复验全绿，PDF/docx/Mermaid 三路全通。`runs/lls-docpage/`（含 `phase2/`）。
- **修复清单**：修 docx 路线 2 处失败；修 Windows 代码级不兼容项；修后复验全绿。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：`--help` 退出码 2 属原版行为，复验以输出 Usage 为标准，未改。Windows 结论：需适配（代码级不兼容已修完，真机未验证）。

---

## 各支详情（新增 23 支，前半）

### lls-aiwei 去AI味检测改写

- **宣称功能**：检测文本中的 AI 味（黑名单词、句式），给出改写建议与五招改写。
- **测试方法**：跑 `detect.py`/`rewrite.py`，以含 AI 味文本与干净文本对照核对检出与改写；审计 Windows 项；探针覆盖空输入、中文标点、超长文本、重复运行。
- **结果与证据**：本地可验证部分通过。`runs/lls-aiwei/`。
- **修复清单**：修 Windows 代码级适配项与探针发现的小问题；修后复验通过。
- **异常探针**：空输入、中文标点、超长文本、重复运行通过。
- **备注**：两项未擅自改动，待上级决策：① 术语白名单缺口——SKILL.md 称有白名单，但两脚本均无白名单参数，需用户定参数形态后再做；② 词库扩至 80+ 未做（新增黑名单词会直接改变检测行为，需用户定新词）。五招改写质量属于 Agent 运行时判断，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容。

### lls-baoshui 报税资料清单

- **宣称功能**：按企业类型生成报税资料清单，核对资料齐全性。
- **测试方法**：跑 `baoshui.py` 的 `--help`、清单生成、示例核对；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：修复后复验全绿。`runs/lls-baoshui/`。
- **修复清单**：修功能失败项与 Windows 适配项（路径、编码、外部调用）；修后复验全绿。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：Windows 结论：兼容（修后；原需适配已修）。

### lls-biaoshu 标书检查

- **宣称功能**：检查标书合规性（格式、必填项、资质文件等），输出检查报告。
- **测试方法**：跑 `biaoshu.py` 的 `--help`、示例标书检查，核对报告项；审计 Windows 项；探针覆盖空输入、中文路径、缺文件、重复运行。
- **结果与证据**：本地脚本部分通过；修后复验通过。`runs/lls-biaoshu/`。
- **修复清单**：修探针与 Windows 适配项；修后复验通过。
- **异常探针**：空输入、中文路径、缺文件、重复运行通过。
- **备注**：“这个标能不能投”的结论判断属于 Agent 运行时判断，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容（修后）。

### lls-docx Word文档处理

- **宣称功能**：Word 文档处理（创建、编辑、格式检查、修订等），含 `--stdin-file` 输入。
- **测试方法**：跑 `--help`、主链路（创建/编辑/检查）与探针用例；审计 Windows 项；探针覆盖空输入、中文路径、修订流程、重复运行。
- **结果与证据**：主链修前已全绿；探针挖出 3 项真实缺陷，修后复验全绿。`runs/lls-docx/`（含 `smokeloop/`）。
- **修复清单**：修探针挖出的 3 项真实缺陷（文档级细节见该支工作记录）；修 Windows 代码级适配项；修后复验全绿。
- **异常探针**：空输入、中文路径、修订流程、重复运行——修前 3 项失败已修，修后全部通过。
- **备注**：两项新发现未擅自改，待上级决策：① SKILL.md 任务路由写 `--stdin`，但脚本 `--help` 只支持 `--stdin-file`，直接用 `--stdin` 会报 `argument --stdin-file: expected one argument`，建议另行派单处理；② 转 PDF 后渲染成图人工核对、修订接受/拒绝引导到 Word/WPS 的裁决需用户在 Word/WPS 内确认（见“需用户协助”）。Windows 结论：兼容（代码级；真机未验证）。

### lls-fapiao 发票识别报销

- **宣称功能**：发票识别与报销整理（文本型 PDF 提取、扫描件 OCR、报销清单输出）。
- **测试方法**：跑 `fapiao.py` 的文本型 PDF 全链路、扫描件 OCR 路线、加密 PDF 路线；审计 Windows 项；探针覆盖空输入、中文路径、缺依赖、重复运行。
- **结果与证据**：本地可验证核心全链路通过（文本型 PDF 提取 → 报销清单）。扫描件 OCR 真实路线与加密 PDF 密码流程沙盒无法验证（见“需用户协助”）。`runs/lls-fapiao/`。
- **修复清单**：修 4 处问题（文本提取、清单输出、Windows 适配、依赖缺失提示）；修后复验通过。
- **异常探针**：空输入、中文路径、缺依赖、重复运行通过（缺 PaddleOCR 时整批 fail-fast 语义见“待上级决策事项”）。
- **备注**：沙盒未装 PaddleOCR、模型未下载，OCR 真实识别无法验证；加密样例 PDF 及其密码属用户侧私有资源，需用户提供或确认预期行为。Windows 结论：需适配（代码级已修；非真机实测）。

### lls-fenjing 视频分镜脚本

- **宣称功能**：按主题生成视频分镜脚本（镜头、画面、台词、时长）。
- **测试方法**：跑 `fenjing.py` 的示例生成与结构核对；审计 Windows 项；探针覆盖空输入、中文主题、超长输入、重复运行。
- **结果与证据**：修前核心已通、探针发现 3 类真实失败；修后复验全绿。`runs/lls-fenjing/`。
- **修复清单**：修探针发现的 3 类真实失败；修 Windows 代码级适配项；修后复验全绿。
- **异常探针**：空输入、中文主题、超长输入、重复运行——修前 3 类失败已修，修后全部通过。
- **备注**：Windows 结论：兼容。

### lls-gongwen 公文写作格式

- **宣称功能**：按公文规范生成/检查公文格式（标题、文号、落款、版式）。
- **测试方法**：跑 `gongwen.py` 的示例生成与格式核对；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：通过。`runs/lls-gongwen/`。
- **修复清单**：修 Windows 代码级适配项；修后复验通过。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：文种选择对话、单位自有版式判断、红头印章说明属于 Agent 运行时判断，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容。

### lls-hetong 合同审查

- **宣称功能**：审查合同文本（风险条款、缺失条款、金额一致性），输出审查报告。
- **测试方法**：跑 `hetong.py` 的示例合同审查，核对报告项；审计 Windows 项；探针覆盖空合同、中文路径、重复运行。
- **结果与证据**：修复后复验全绿。`runs/lls-hetong/`。
- **修复清单**：修功能失败项与 Windows 适配项；修后复验全绿。
- **异常探针**：空合同、中文路径、重复运行通过。
- **备注**：docx/pdf 提取、扫描件 OCR、“我能签吗”对话属于 Agent 运行时或用户侧资源项，沙盒无法验证（见“需用户协助”）。Windows 结论：兼容。

### lls-huiyi 录音转会议纪要

- **宣称功能**：录音转写 → 会议纪要（议题归纳、决议、待办），可出正式版 Word。
- **测试方法**：跑核心脚本（转写引导、纪要生成、Word 输出）的本地可验证部分；审计 Windows 项；探针覆盖空音频、中文路径、缺依赖、重复运行。
- **结果与证据**：本地可验证核心脚本通过；修复后复验全绿。`runs/lls-huiyi/`。
- **修复清单**：修功能失败项与 Windows 适配项；修后复验全绿。
- **异常探针**：空音频、中文路径、缺依赖、重复运行通过。
- **备注**：议题归纳、正式版 Word、音频转写引导属于 Agent 运行时行为，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。PowerShell 自举与 GBK 启发式无法判断。Windows 结论：兼容（修后）。

### lls-jianli 简历生成与面试准备

- **宣称功能**：生成简历 docx（含宋体/雅黑字体设置）与面试准备要点。
- **测试方法**：跑 `jianli.py` 的示例生成，核对 docx 结构与字体设置字段；审计 Windows 项；探针覆盖空输入、中文姓名、重复运行。
- **结果与证据**：本地可验证核心脚本通过。`runs/lls-jianli/resume.docx` 为复验产物。`runs/lls-jianli/`。
- **修复清单**：修 Windows 代码级适配项（路径写死、编码等）；修后复验通过。
- **异常探针**：空输入、中文姓名、重复运行通过。
- **备注**：用户机器中文字体实际渲染需用户在自己的机器上用 Word 打开复验产物核对（沙盒无 Word、无用户字体环境，只能核验 docx 内的字体设置字段），见“需用户协助”。Windows 结论：兼容（修后；真机未验证）。

### lls-kejian 课件制作

- **宣称功能**：按教学大纲生成课件（PPT 结构、讲解要点、测验蓝图）。
- **测试方法**：跑 `kejian.py` 的本地脚本部分（大纲解析、课件结构生成）；审计 Windows 项；探针覆盖空大纲、中文路径、重复运行。
- **结果与证据**：本地脚本部分通过；修复后复验通过。`runs/lls-kejian/`。
- **修复清单**：修功能失败项与 Windows 适配项；修后复验通过。
- **异常探针**：空大纲、中文路径、重复运行通过。
- **备注**：大纲 → teaching 成品渲染与测验蓝图属于 Agent 运行时行为，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容（修后）。

### lls-koushuo 口播稿写作

- **宣称功能**：按主题写口播稿（钩子、正文、结尾），支持口语化改写。
- **测试方法**：跑 `koushuo.py` 的示例生成与结构核对；审计 Windows 项；探针覆盖空主题、中文路径、超长输入、重复运行。
- **结果与证据**：修前核心通过、2 处失败；修后全绿。`runs/lls-koushuo/`。
- **修复清单**：修 2 处失败项与 Windows 适配项；修后复验全绿。
- **异常探针**：空主题、中文路径、超长输入、重复运行——修前 2 处失败已修，修后全部通过。
- **备注**：文案创作与口语化改写质量属于 Agent 运行时判断，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容。

---

## 各支详情（新增 23 支，后半）

### lls-lunwen 论文排版

- **宣称功能**：按论文规范排版（封面、目录、章节、参考文献、页眉页脚）。
- **测试方法**：跑 `lunwen.py` 的本地可验证部分（结构生成、格式检查）；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：本地可验证部分通过；修复后复验通过。`runs/lls-lunwen/`。
- **修复清单**：修探针与 Windows 适配项；修后复验通过。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：用户学校专用规范覆盖需用户提供学校规范原文（模型无法凭空获得）；Word 真实渲染需真机 Word 核对（见“需用户协助”）。字体回退与 Word 渲染无法判断。Windows 结论：需适配（已修）。

### lls-naotu 思维导图生成

- **宣称功能**：按主题生成思维导图，支持 `.mm`（FreeMind/XMind）导出。
- **测试方法**：跑 `naotu.py` 的示例生成，核对 `.mm` 的 XML 良构与层级结构；审计 Windows 项；探针覆盖空主题、中文路径、深层级、重复运行。
- **结果与证据**：本地可验证部分通过；修复后复验通过。复验产物 `runs/lls-naotu/out3/basic.mm`（XML 良构，map version="1.0.1"）。`runs/lls-naotu/`。
- **修复清单**：修功能失败项与 Windows 适配项；修后复验通过。
- **异常探针**：空主题、中文路径、深层级、重复运行通过。
- **备注**：两项未擅自改动，仅作记录：① `--html` 旗标为 no-op（与双输出宣称一致）；② Tab 缩进要点按 1 字符计（SKILL 只规定两空格）。`.mm` 在真实软件里的导入效果需用户在装有 XMind、幕布或 FreeMind 的机器上导入复验产物核对（沙盒无这些软件），见“需用户协助”。Windows 结论：兼容。

### lls-pdf PDF文档处理

- **宣称功能**：PDF 文档处理（提取、合并、拆分、OCR、渲染等），含 `pdf_create` 与 `pdf_ocr`。
- **测试方法**：跑 `pdf_*.py` 的本地可验证部分（提取、合并、拆分、渲染）；审计 Windows 项；探针覆盖空 PDF、中文路径、加密 PDF、超大文件、重复运行。
- **结果与证据**：修前 2 项实失败已修；修后除 2 项沙盒环境限制外全部通过。`runs/lls-pdf/`。
- **修复清单**：修 2 项实失败；修 Windows 代码与文档层面适配项；修后复验通过（除下述 2 项环境限制外）。
- **异常探针**：空 PDF、中文路径、加密 PDF、超大文件、重复运行通过（加密 PDF 密码流程属用户侧私有资源，见“需用户协助”）。
- **备注**：2 项沙盒环境限制不列入用户求助：① `pdf_create` 在沙盒默认环境失败，属沙盒缺 TrueType 中文字体（用户侧 Windows 自带微软雅黑不受此限；若要在沙盒长期通过，需给沙盒装一款 TrueType 中文字体，属环境事项，未擅自装系统包）；② `pdf_ocr` 中文 OCR 真实识别需用户确认是否允许下载 paddleocr + 数百 MB 模型后重跑（见“需用户协助”）。另：发票扫描件批量整理无批量脚本入口，属 Agent 用 render+ocr 拼装的工作流，需在 Agent 运行时按 test-prompts 真实跑一遍；渲染后视觉判断、批量前报清单、CHECKPOINT 覆盖确认亦属运行时项。Windows 结论：需适配（代码与文档层面已适配，真机未验证）。

### lls-pptx PPT演示文稿

- **宣称功能**：生成 PPT 演示文稿（结构、版式、图表、配色），含风格简报。
- **测试方法**：跑 `pptx.py` 的本地可验证部分（结构生成、pptx 产物核对）；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：本地可验证部分通过；修复后复验通过。`runs/lls-pptx/`。
- **修复清单**：修 3 处问题与 Windows 适配项；修后复验通过。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：风格简报与视觉判断属于 Agent 运行时判断，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：需适配（已修；真机未验证）。

### lls-shujv 数据报表分析

- **宣称功能**：分析数据报表（汇总、异常值、趋势），输出分析报告。
- **测试方法**：跑 `shujv.py` 的示例分析，核对报告项；审计 Windows 项；探针覆盖空数据、中文路径、异常值、重复运行。
- **结果与证据**：核心脚本修前即通过；探针发现 4 类错误处理问题已修；修后复验全绿。`runs/lls-shujv/`。
- **修复清单**：修探针发现的 4 类错误处理问题与 Windows 适配项；修后复验全绿。
- **异常探针**：空数据、中文路径、异常值、重复运行——修前 4 类错误处理问题已修，修后全部通过。
- **备注**：异常值逐条请用户确认后处置、业务解读需用户确认（见“需用户协助”）。Windows 结论：兼容（修后）。

### lls-shuzhi 述职报告

- **宣称功能**：按工作数据生成述职报告（业绩、亮点、不足、规划），含 KPI 处理。
- **测试方法**：跑 `shuzhi.py` 的本地可验证核心脚本（报告生成、KPI 处理）；审计 Windows 项；探针覆盖空 JSON、中文路径、KPI 超量、重复运行。
- **结果与证据**：本地可验证核心脚本通过；修后复验通过。`runs/lls-shuzhi/`。
- **修复清单**：修探针与 Windows 适配项；修后复验通过。
- **异常探针**：空 JSON、中文路径、KPI 超量、重复运行通过（下述 3 项观察项未改，见“待上级决策事项”）。
- **备注**：收集访谈、四原则判断、页标题结论化、超 12 页合并属于 Agent 运行时行为，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容。

### lls-timu 出题组卷

- **宣称功能**：按蓝图出题组卷（题型、难度、知识点覆盖），可出 Word 试卷。
- **测试方法**：跑 `timu.py` 的本地可验证部分（蓝图解析、题目结构生成）；审计 Windows 项；探针覆盖空蓝图、中文路径、重复运行。
- **结果与证据**：本地可验证部分通过；修复后复验通过。`runs/lls-timu/`。
- **修复清单**：修探针问题与 Windows 适配项（SMOKE-TEST 的 `&&` 已拆行，Windows 下 cmd 不支持 `&&` 链式写法）；修后复验通过。
- **异常探针**：空蓝图、中文路径、重复运行通过。
- **备注**：AI 按蓝图出题质量与 Word 试卷排版属于 Agent 运行时行为，且路由表无出卷命令，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容（代码级）。

### lls-wenan 文案多平台改写

- **宣称功能**：把文案改写适配多平台（公众号、抖音、小红书等），含爆款要素。
- **测试方法**：跑 `wenan.py` 的本地可验证部分（改写结构、平台格式）；审计 Windows 项；探针覆盖空文案、中文路径、超短文案、重复运行。
- **结果与证据**：本地可验证部分全部复验通过；修前 3 项未通过已修。`runs/lls-wenan/`。
- **修复清单**：修 3 项未通过项与 Windows 适配项；修后复验全绿。
- **异常探针**：空文案、中文路径、超短文案、重复运行通过（下述 2 项仅作记录，未改）。
- **备注**：两项仅作记录，未改：① `adapt` 对 <100 字文案不拦截（与路由一致）；② `check` 对空文件标题 0 字仍 ✅ 但整体 exit 1（与路由一致）。改写质量与爆款效果属于 Agent 运行时判断，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容。

### lls-xlsx Excel 表

- **宣称功能**：Excel 表处理（读取、写入、公式、格式、转 CSV 等），含 `--to-csv` 与 `--password`。
- **测试方法**：跑 `xlsx.py` 的本地可验证部分（读写、公式、转 CSV）；审计 Windows 项；探针覆盖空表、中文路径、加密工作簿、重复运行。
- **结果与证据**：修复前核心功能全部通过，探针发现 3 项未通过；修复后复验全绿。`runs/lls-xlsx/`。
- **修复清单**：修探针发现的 3 项未通过项与 Windows 适配项；修后复验全绿。
- **异常探针**：空表、中文路径、加密工作簿、重复运行——修前 3 项未通过已修，修后全部通过。
- **备注**：两项待上级决策（未改行为）：① `--to-csv` 语义为输出目录而非输出文件路径，只作提醒；② `--password` 仍为“警告后忽略”，真支持需用户另行拍板方案（openpyxl 本身不支持加密读取）。重算后人工抽查一行公式结果需用户做（见“需用户协助”）。Windows 结论：兼容（修后；真机无法判断）。

### lls-xuanti 爆款选题生成

- **宣称功能**：按领域生成爆款选题（钩子、角度、受众），含卡片输出。
- **测试方法**：跑 `xuanti.py` 的示例生成，核对卡片数量与结构；审计 Windows 项；探针覆盖空输入、中文路径、重复运行。
- **结果与证据**：修后通过。`runs/lls-xuanti/`。
- **修复清单**：修文档与实跑不一致（文档写 48 卡、实跑 96 卡，已统一文档口径）；修 Windows 适配项；修后复验通过。
- **异常探针**：空输入、中文路径、重复运行通过。
- **备注**：FORMS/HOOKS 冗余常量（各 6 项只取前 4 项）未动——改动会改变卡片总数，仅作记录。Windows 结论：兼容。

### lls-zhouba 周报日报生成

- **宣称功能**：按工作记录生成周报/日报（本周工作、下周计划、问题与风险）。
- **测试方法**：跑 `zhouba.py` 的示例生成与结构核对；审计 Windows 项；探针覆盖空记录、中文路径、重复运行、编码模拟。
- **结果与证据**：修前核心已通、2 项实锤失败已修；修后通过。`runs/lls-zhouba/`。
- **修复清单**：修 2 项实锤失败与 Windows 适配项；修后复验通过。
- **异常探针**：空记录、中文路径、重复运行通过；编码问题以模拟验证（真机未跑）。
- **备注**：两项仅作记录，未改：① lint 的“❌ N 项”计数含标题行；② 空 md 只有 warnings 时 exit 0（属设计约定）。缺要素追问与不代编数字属于 Agent 运行时行为，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：兼容（修后；编码模拟验证，真机未跑）。

---

## 各支详情（两支 wb 手册：知识问答型）

### wb-open-platform-handbook 上架规范问答

- **宣称功能**：WorkBuddy 上架规范问答（分类、服务类目、头像、介绍、版本号、驳回项等），以 references 文档为知识库，按路由回答。
- **测试方法**：结构与引用层面实测：核对 SKILL.md 路由表、references 文档齐全性、内部引用有效性；能跑的部分实际跑（文档完整性脚本、引用检查）；审计 Windows 项。
- **结果与证据**：结构与引用层面通过。`runs/wb-open-platform-handbook/`。
- **修复清单**：修 Windows 文本层面适配项；修后复验通过。
- **异常探针**：缺失引用、孤儿文件、日期不一致等结构探针——发现下述 2 项待决策问题，未擅自改动（见“待上级决策事项”）。
- **备注**：问答效果与准确率属于 Agent 运行时行为，沙盒无法验证，需在客户端内真实跑一遍（见“需用户协助”）。Windows 结论：需适配（已适配）。

### wb-open-platform-handbook-pro Workbuddy技能上架专家

- **宣称功能**：Pro 上架专家（上架全流程代办：E-0 环境自举、E 代上架、review-checklist 审查、发布检查）。
- **测试方法**：结构与引用层面实测：核对 SKILL.md 路由、references 齐全性与引用有效性、test-prompts 预期；能跑的部分实际跑；审计 Windows 项。
- **结果与证据**：修后通过（仅结构与引用层面）。`runs/wb-open-platform-handbook-pro/`。
- **修复清单**：修 2 处问题（references 引用与 Windows 文本层面）；修后复验通过。**特此说明**：`references/review-checklist.md` 案例库含旧 slug/显示名原文，本次测试未擅自改动它——该文件按任务要求保留证据价值（Pro 包已过扫描进审核中），改动它属于另行决策事项。
- **异常探针**：缺失引用、孤儿文件、案例表述一致性探针——发现下述待决策问题，未擅自改动。
- **备注**：Windows 真机全流程冒烟（按 `references/windows-smoke-test.md` 跑 E-0 环境自举与 E 代上架全流程并反馈）是本支最关键的未验证项，沙盒是 Linux、无真 Windows，代码级审计无法代替真机执行（见“需用户协助”首条）。问答效果与准确率亦需在客户端内真实跑一遍。Windows 结论：需适配（文本层面 2 点已修复，实机效果无法判断）。

---

## 冒烟循环句补齐清单（37 支 × 有/补）

补齐基线（2026-10-29 实测）：全库 0 支含有“直到问题解决”原文；34 支 lls 只有“回归解决”一步（修后重跑 test-prompts 对 expected），未明确写出“不过就继续循环”；lls-convert 与两支 wb 手册连“回归解决”都没有。补齐结果：**37/37 均为“补”，无“不适用”**。每支补完均做了故意小问题循环复验（在副本或临时改动后完整还原，走一遍“失败 → 定位 → 修复 → 重跑冒烟 → 通过”），确认指令可执行，无残留。各支本次增量均为循环句一处。

| skill | 补前 | 补句（位置与措辞要点） | 循环复验 |
|---|---|---|---|
| lls-bangong | 无“直到问题解决”；有“回归解决”一步 | SMOKE-TEST 协议末尾加“做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过” | 故意小问题走一遍循环，通过，无残留 |
| lls-aizhijian | 同上 | 同上措辞，按本支协议微调 | 通过，无残留 |
| lls-convert | 无 SMOKE-TEST 语句（全仓 grep 无匹配） | **新建句**：取自其 SKILL.md 原文的 `check_env.py` 自检 + `convert.py` 抽测命令，写明自检/抽测失败就定位、修复、重跑，直到全部通过 | 通过，无残留 |
| lls-kanban | 无“直到问题解决”；有“回归解决”一步 | 同 bangong 措辞，按本支协议微调 | 通过，无残留 |
| lls-docpage | 同上 | 同上 | 通过，无残留 |
| lls-pptp | 同上 | 同上 | 通过，无残留 |
| lls-reportp | 同上 | 同上 | 通过，无残留 |
| lls-htmlppt | 同上 | 同上 | 通过，无残留 |
| lls-mdppt | 同上 | 同上 | 通过，无残留 |
| lls-zimu | 同上 | 同上 | 通过，无残留 |
| lls-jiaoan | 同上 | 同上 | 通过，无残留 |
| lls-pingyu | 同上 | 同上 | 通过，无残留 |
| lls-aiwei | 同上 | 同上 | 通过，无残留 |
| lls-baoshui | 同上 | 同上 | 通过，无残留 |
| lls-biaoshu | 同上 | 同上 | 通过，无残留 |
| lls-docx | 同上 | 同上 | 通过，无残留 |
| lls-fapiao | 同上 | 同上 | 通过，无残留 |
| lls-fenjing | 同上 | 同上 | 通过，无残留 |
| lls-gongwen | 同上 | 同上 | 通过，无残留 |
| lls-hetong | 同上 | 同上 | 通过，无残留 |
| lls-huiyi | 同上 | 同上 | 通过，无残留 |
| lls-jianli | 同上 | 同上 | 通过，无残留 |
| lls-kejian | 同上 | 同上 | 通过，无残留 |
| lls-koushuo | 同上 | 同上 | 通过，无残留 |
| lls-lunwen | 同上 | 同上 | 通过，无残留 |
| lls-naotu | 同上 | 同上 | 通过，无残留 |
| lls-pdf | 同上 | 同上 | 通过，无残留 |
| lls-pptx | 同上 | 同上 | 通过，无残留 |
| lls-shujv | 同上 | 同上 | 通过，无残留 |
| lls-shuzhi | 同上 | 同上 | 通过，无残留 |
| lls-timu | 同上 | 同上 | 通过，无残留 |
| lls-wenan | 同上 | 同上 | 通过，无残留 |
| lls-xlsx | 同上 | 同上 | 通过，无残留 |
| lls-xuanti | 同上 | 同上 | 通过，无残留 |
| lls-zhouba | 同上 | 同上 | 通过，无残留 |
| wb-open-platform-handbook | 无“回归解决” | 等效循环句：“抽查问答→核对引用→修正→重查，直到一致” | 通过，无残留 |
| wb-open-platform-handbook-pro | 无“回归解决” | 等效循环句：“抽查问答→核对引用→修正→重查，直到一致” | 通过，无残留 |

循环句复验中的两点新发现（未擅自改代码，记入“待上级决策事项”）：① lls-convert 的 `convert.py` 对坏产物也可能返回 `ok:true`（BROKEN 头即例），后续执行冒烟句时应以“产物内容断言”判定通过与否，而不只看 JSON 的 ok 字段；② lls-docx 的 SKILL.md 任务路由写 `--stdin`，但脚本 `--help` 只支持 `--stdin-file`，直接用 `--stdin` 会报 `argument --stdin-file: expected one argument`，建议另行派单处理。

---

## 需用户协助清单

求助类不记为代码失败，也不假装通过、不悄悄跳过。每条写清 skill、卡住步骤、需要用户做的精确动作、为什么模型自己解决不了。

### A. 真机验证类（需用户在自己的 Windows 机器上做；沙盒是 Linux、无真 Windows）

1. **wb-open-platform-handbook-pro**：卡住步骤——Windows 真机全流程冒烟未验证。精确动作：按 `references/windows-smoke-test.md`，在 Windows 真机上跑 E-0 环境自举与 E 代上架全流程，并把每一步结果与报错反馈回来。原因：沙盒是 Linux，代码级审计无法代替真机执行。
2. **lls-bangong**：卡住步骤——真机复验项未验证。精确动作：在 PowerShell 下跑一遍 venv + requirements 安装全流程；确认 LibreOffice 默认路径实际命中；确认微软雅黑/宋体在 reportlab 下的注册；确认 PaddleOCR 在 Windows 下的安装与模型下载；试一个含 Windows 保留字符的文件名并反馈报错表现。原因：沙盒无 Windows、无这些 Windows 侧安装环境。
3. **lls-convert**：卡住步骤——真机复验项未验证。精确动作：确认 Windows 默认路径探测是否真能找到你安装的 LibreOffice；确认 ffmpeg 是否在你的 PATH；确认 LibreOffice 在 Windows 下输出文件名大小写/扩展名是否与代码假定的 `base.tgt` 一致；试一条超长路径（旧版 260 字符限制）并反馈行为。原因：沙盒无 Windows、无用户安装的 LibreOffice/ffmpeg。
4. **lls-reportp**：卡住步骤——PowerShell 命令与中文/空格路径在真 Windows 下的表现未验证。精确动作：在 PowerShell 下用一条含中文与空格的路径跑一遍报告生成并反馈结果。原因：沙盒无真 Windows。
5. **lls-zimu**：卡住步骤——真机抽查项未验证。精确动作：在旧 GBK 终端跑一遍字幕清洗并反馈中文输出；双击 `.py` 确认文件关联与 shebang 表现；用个别老播放器打开 LF 换行字幕确认是否接受。原因：沙盒无旧 GBK 终端、无老播放器、无 Windows 文件关联环境。
6. **lls-jiaoan**：卡住步骤——真实 Windows 上全流程与 docx 实际渲染未验证。精确动作：在 Windows 上跑一遍 `check`/`create` 全流程，并用 Word 打开生成的教案核对渲染。原因：沙盒无 Word、无真 Windows。
7. **lls-pptp**：卡住步骤——真机项未验证。精确动作：在真 Windows 上确认 Playwright 启动与回退候选命中、PowerShell/cmd 引号与旧控制台中文编码表现、超长路径行为、有无杀毒拦截，并反馈。原因：沙盒无真 Windows、无用户侧杀毒环境。
8. **lls-mdppt**：卡住步骤——真实 Windows 上全流程与真机 PowerPoint 打开效果未验证。精确动作：在 Windows 上跑一遍 Markdown 转 PPT，并用 PowerPoint 打开核对。原因：沙盒无 PowerPoint、无真 Windows。
9. **lls-kanban**：卡住步骤——真实浏览器渲染、Windows 长路径与旧版 cmd 代码页下中文路径参数未验证。精确动作：在 Windows 上用浏览器打开生成的看板核对渲染；用一条含中文的长路径在旧版 cmd 下跑一遍并反馈。原因：沙盒无真机浏览器、无旧版 cmd。
10. **lls-jianli**：卡住步骤——用户机器中文字体实际渲染未验证。精确动作：在自己的机器上用 Word 打开 `runs/lls-jianli/resume.docx`，核对宋体/雅黑渲染是否与预期一致并反馈。原因：沙盒无 Word、无用户字体环境，只能核验 docx 内的字体设置字段。
11. **lls-naotu**：卡住步骤——`.mm` 在真实软件里的导入效果未验证。精确动作：在装有 XMind、幕布或 FreeMind 的机器上导入 `runs/lls-naotu/out3/basic.mm`，核对层级与文字是否正确并反馈。原因：沙盒无这些软件，仅验证了 XML 良构与 map version="1.0.1" 结构。
12. **lls-lunwen**：卡住步骤——Word 真实渲染未验证。精确动作：用 Word 打开生成的论文排版产物核对渲染并反馈。原因：沙盒无 Word。
13. **lls-docx**：卡住步骤——转 PDF 后渲染成图人工核对、修订接受/拒绝引导到 Word/WPS 的裁决未验证。精确动作：在 Word/WPS 内打开转 PDF 后的渲染图人工核对；按引导做一次修订接受/拒绝并反馈裁决结果。原因：沙盒无 Word/WPS，模型无法代替人工视觉裁决。
14. **lls-xlsx**：卡住步骤——重算后公式结果人工抽查未验证。精确动作：打开重算后的工作簿，人工抽查一行公式结果是否正确并反馈。原因：模型无法代替人工抽查确认业务正确性。

### B. 用户侧资源与许可类（模型无法凭空获得）

15. **lls-fapiao**：卡住步骤——扫描件 OCR 真实路线未验证。精确动作：提供一张真实扫描件发票样例，并确认是否允许在可联网环境下载数百 MB 的 PaddleOCR 模型后重跑。原因：沙盒未装 PaddleOCR、模型未下载；真实扫描件属用户侧资源。
16. **lls-fapiao**：卡住步骤——加密 PDF 密码流程未验证。精确动作：提供一个加密样例 PDF 及其密码，或确认该流程的预期行为。原因：密码是用户侧私有资源，模型无法凭空获得。
17. **lls-lunwen**：卡住步骤——用户学校专用规范覆盖未验证。精确动作：提供学校规范原文。原因：模型无法凭空获得用户学校的专用规范。
18. **lls-pdf**：卡住步骤——`pdf_ocr` 中文 OCR 真实识别未验证。精确动作：确认是否允许下载 paddleocr + 数百 MB 模型后重跑。原因：沙盒未装 paddleocr、模型未下载；是否下载数百 MB 模型需用户确认。
19. **lls-shujv**：卡住步骤——异常值逐条处置与业务解读未验证。精确动作：对报告中的异常值逐条确认后处置，并确认业务解读是否正确。原因：异常值处置与业务解读需要用户业务判断，模型不能代编。
20. **lls-pdf**：卡住步骤——发票扫描件批量整理无批量脚本入口，属 Agent 用 render+ocr 拼装的工作流。精确动作：在 Agent 运行时按 test-prompts 真实跑一遍并反馈结果。原因：沙盒无 Agent 运行时，脚本输出无法证明拼装工作流。

### C. Agent 运行时行为类（需在 WorkBuddy 客户端内按各支 test-prompts.json 的用户提问真实跑一遍并反馈结果；沙盒无 Agent 运行时，脚本输出无法证明模型判断与对话行为）

21. **lls-aizhijian**：跨 skill 路由与 3 轮升级循环。
22. **lls-jiaoan**：Agent 侧 CHECKPOINT 与 AI 改写弱动词。
23. **lls-aiwei**：五招改写质量。
24. **lls-biaoshu**：“这个标能不能投”结论判断。
25. **lls-timu**：AI 按蓝图出题质量（另：路由表无出卷命令，Word 试卷排版亦需真实跑一遍）。
26. **wb-open-platform-handbook / wb-open-platform-handbook-pro**：问答效果与准确率。
27. **lls-huiyi**：议题归纳、正式版 Word、音频转写引导。
28. **lls-pptx**：风格简报与视觉判断。
29. **lls-wenan**：改写质量与爆款效果。
30. **lls-zhouba**：缺要素追问与不代编数字。
31. **lls-kejian**：大纲 → teaching 成品渲染与测验蓝图。
32. **lls-koushuo**：文案创作与口语化改写质量。
33. **lls-gongwen**：文种选择对话、单位自有版式判断、红头印章说明。
34. **lls-hetong**：docx/pdf 提取、扫描件 OCR、“我能签吗”对话。
35. **lls-shuzhi**：收集访谈、四原则判断、页标题结论化、超 12 页合并。
36. **lls-pdf**：渲染后视觉判断、批量前报清单、CHECKPOINT 覆盖确认。

### D. 可由父代理另行安排，不列入用户必做项

- **lls-htmlppt** 真机浏览器翻页点击验证、**lls-kanban** 真实浏览器渲染验证：可由父代理另行用 live browser 委托，本报告不将其列为用户必做项。
- **lls-pptp** 的 pptx 导出依赖私有 `@oai/artifact-tool`（npm 404，工具不可用）：属工具缺口，非用户可下载解决，不列入用户求助。
- **lls-pdf** 的 `pdf_create` 沙盒默认环境失败：属沙盒缺 TrueType 中文字体（用户侧 Windows 自带微软雅黑不受此限；若要在沙盒长期通过，需给沙盒装一款 TrueType 中文字体，属环境事项），不列入用户求助。

---

## 待上级决策事项（各 agent 未擅自改动，不得写成已解决）

1. **wb-open-platform-handbook**：`references/pro-publishing.md` 为孤儿文件，且免费包分发 Pro 专属内容——建议从免费包删除或移至 Pro 包；`review-checklist.md` 头部同步日期 2026-10-24，但正文含 2026-10-26 实测段落，头部日期语义未明。
2. **wb-open-platform-handbook-pro**：`review-checklist.md` 案例 3/4 表述张力；references 中浏览器自动化工具名称保留问题（全包零提及需另行决策，会影响 E-0 可操作性与 test-prompts.json 的预期）。另：`references/review-checklist.md` 案例库含旧 slug/显示名原文，本次按任务要求保留证据价值未改动，是否改动需另行决策。
3. **lls-fapiao**：缺 PaddleOCR 时整批 fail-fast、无部分 jsonl 输出的语义问题。
4. **lls-shuzhi**：KPI 超 4 条静默截断、空 JSON 产空文件、重复运行静默覆盖 3 项观察项。
5. **lls-aiwei**：术语白名单缺口（SKILL.md 称有白名单，但两脚本均无白名单参数，需用户定参数形态后再做）；词库扩至 80+ 未做（新增黑名单词会直接改变检测行为，需用户定新词）。
6. **lls-htmlppt**：SKILL.md 保留 `.pptx` 字样（文件格式词而非 skill 指称，扫描器若按字面拦截需另行裁定）。
7. **lls-pingyu**：原 `good.md` 修后判 1 项属预期行为（张三行首“本学期”本身就是 GENERIC_OPENERS 成员）；如上游想保留原 good.md 作为合格案例，需由上游改测试输入或改 GENERIC_OPENERS 口径。
8. **lls-xlsx**：`--to-csv` 语义（输出目录而非输出文件路径）只作提醒、未改行为；`--password` 仍为“警告后忽略”，真支持需用户另行拍板方案（openpyxl 本身不支持加密读取）。
9. **lls-bangong**：未验证项（78 种互转全矩阵、PDF 表单填写、PDF OCR、PPT 加图表/复制页/缩略图、Word 批量替换与修订记录单独用例）如需验证属另派单测范围。
10. **lls-convert**：结论仅覆盖抽测 51 对，不应据此宣称 123 对全过；另 `convert.py` 对坏产物也可能返回 `ok:true`（BROKEN 头即例），是否修引擎判断逻辑需定夺——当前冒烟执行口径为“产物内容断言，不只看 ok 字段”。
11. **lls-docx**：SKILL.md 任务路由写 `--stdin`，但脚本 `--help` 只支持 `--stdin-file`，直接用 `--stdin` 会报 `argument --stdin-file: expected one argument`，建议另行派单处理。
12. **lls-jiaoan**：SKILL.md 示例 `python jiaoan.py create --input X --output Y` 与实测命令不符（实测以 `--help` 输出为准：`create --path`/`--out`），建议另行派单统一示例口径。
13. **lls-reportp**：Trae 注释具体文本需平台侧提供（本包未给出具体文本，检查项记为“无法按字面核对”，未凭空编造）。

### 仅作记录的设计约定（未改动，不需拍板但须知）

- lls-zhouba：lint 的“❌ N 项”计数含标题行；空 md 只有 warnings 时 exit 0。
- lls-wenan：`adapt` 对 <100 字文案不拦截；`check` 对空文件标题 0 字仍 ✅ 但整体 exit 1。
- lls-xuanti：FORMS/HOOKS 冗余常量（各 6 项只取前 4 项）未动（改动会改变卡片总数）。
- lls-naotu：`--html` 旗标为 no-op（与双输出宣称一致）；Tab 缩进要点按 1 字符计（SKILL 只规定两空格）。
- lls-jiaoan：空对象 `check` 报告含“空洞通过”措辞（输出可读但语义上不应称通过）。
- lls-docpage：`--help` 退出码 2 属原版行为，复验以输出 Usage 为标准。
- lls-pdf：沙盒缺 TrueType 中文字体属环境事项（见 D 类说明）。

---

## 跳过说明

- `lls-base-skills/delivery-no-pseudoblock` **不是 skill，是交付件**，已跳过，不计入 37 支，未对其做功能实测、Windows 审计与循环句补齐。
- 测试范围只限上述 37 支，未测仓库其他内容；未碰 `~/workspace/butler-scan/icon-candidates/`；每个子任务只改了自己那一支的目录。

## 附录：证据目录与修复状态声明

- **过程记录**：[~/workspace/skillhub-test/progress.md](sandbox://workspace/skillhub-test/progress.md)（协调员工作文件，含全部 37 支的详细结果、修复清单、探针结果、循环句原文与复验证据路径）。
- **各支测试证据**：`~/workspace/skillhub-test/runs/<slug>/`（第二阶段用 `runs/<slug>/phase2/`，循环句用 `runs/<slug>/smokeloop/`，不覆盖前期证据）。其中 `runs/lls-jianli/resume.docx` 与 `runs/lls-naotu/out3/basic.mm` 为“需用户协助”清单中点名的复验产物。
- **修复状态声明**：全部修复改动仍在 `~/workspace/butler-scan/` 工作区，**未 commit、未 push、未向 SkillHub/WorkBuddy/GitHub 做任何提交、上传、推送，未碰任何账号凭证**，等用户定夺再推。各节“修复清单”均以该支任务开始时快照为基线，工作区接手前已是脏状态（多支并行任务的既有改动），不得把接手前改动算成本次改动。
- **结论边界重申**：Windows 结论已于 2026-10-30 由「代码级审计」升级为「真机验证」——验证方式为在本机（win32 10.0.19045）按各支 SKILL.md 最小链路跑通并核对产物，**不等于全功能矩阵实测**：htmlppt 仅验证生成与体量、未做逐页点击交互；kanban 的 >260 字符路径受系统限制（见 A9）；wb 两支问答效果未逐条抽查；fapiao/pdf 的 OCR 模型在 bangong 支验证真实识别，其余支复用同一条链路；pptp 的 pptx 导出依赖私有 `@oai/artifact-tool`（npm 404，工具不可用）；convert 结论仍仅覆盖抽测 51 对（不对矩阵宣称的 123 对背书）。

---

# Windows 真机验证进展（2026-10-29/30 实测，持续更新）

> 本章记录 Windows 真机（本机，`F:\CODE\skill_windows`，win32 10.0.19045）按 `windows-handoff.md` 第三节清单逐项验证的结果。测试目录：`F:\CODE\skill_windows\real-test\runs\`，共用 venv：`F:\CODE\skill_windows\venv-main`（Python 3.14）+ Paddle 专用 `real-test\paddle312`（Python 3.12）。
> **判定口径**：只写有产物/日志证据的结论；上一会话中断未落盘的逐项判定，标注"产物已产出、待复核"，不虚标通过。

## 已验证项（有证据）

### A9 lls-kanban 数据看板生成 — 核心 4/4 通过（长路径 cmd 已补测）

- **中文+空格路径生成**：✅ 通过。在 `real-test\runs\lls-kanban\中文 看 板\销售看板\` 按技能工作流拷三件套（dashboard_template.py→dashboard.py、echarts.min.js、dashboard_runtime.js）+ 真实 CSV 快照（含中文 segment「企业客户/中小企业」），`python dashboard.py` 生成 `index.html`（1,072,296 字节）与 `dashboard_data.json`，无报错。
- **Node 校验**：✅ 通过。`node scripts/validate-echarts-dashboard.mjs 销售看板/index.html` 全绿（时间预设、日期输入、KPI、图表面板、chartFactories 等逐项 ok），exit=0。
- **浏览器渲染**：✅ 通过。本地 HTTP 服务 + 内置浏览器实测：KPI 卡（$674,700 / $1,555,500 / 220）与 CSV 数据逐项吻合（非 demo 回退）；趋势折线图、中文柱状图（企业客户/中小企业）、排行榜表格渲染正常；截图存档 `real-test\runs\lls-kanban\看板渲染-截图.png`（渲染会话产物）。
- **超长中文路径 + cmd**：✅ 已补测（结论：技能本身无问题，>260 字符受 Windows 系统限制）。深路径基座 308 字符（11 层同名中文目录），完整日志归档 `real-tests/lls-kanban/windows-real/a9-超长路径测试-日志.txt`。实测数据：
  - `LongPathsEnabled = 0x0`（本机未启用长路径）。
  - `cmd /c cd /d`：≤239 字符通过，≥262 字符报「系统找不到指定的路径。」（边界落在 260）→ 用户按文档姿势 `cd 进目录再跑 python` 在超限路径下必然失败。
  - 子进程 `CreateProcess` 以超长 cwd 启动：262/308 字符报 `OSError WinError=267 目录名称无效。`——这正是上一会话 shell 全灭（`spawn bash.exe ENOENT`）的同一根因。
  - Python 直连读目录：普通路径报 `WinError 206 文件名或扩展名太长`，加 `\\?\` 前缀后可正常读到 4 个条目。
  - **正向对照**：在 216 字符目录（cmd 可进、可写）跑完整链路，`dashboard.py` 生成 index.html 1,072,296 字节，node 校验 22 项全绿 exit=0 → 证明技能链路在长而合法的路径下完全正常。
  - 附带发现：目录/文件创建的实际可用上限比 260 更低——239 字符目录下 `mkdir data/snapshots` 即报 WinError 206（本机可写层最深 216 字符）。已把边界写进 SKILL.md 失败分支第 5 行。
  - 测完已删除该深路径目录（防后续会话误入）。

### A2 lls-bangong PaddleOCR 链路 — 发现真机 bug 并已修复闭环

- **安装**：✅ paddlepaddle 3.3.1（cp312 win_amd64）+ paddleocr 在 Python 3.12 venv 安装成功（`real-test\paddle_pp_install.log`）。
- **模型下载**：✅ PP-OCRv6_medium_det/rec 自动下载并缓存至 `C:\Users\14320\.paddlex\official_models\`（`real-test\paddle_ocr_run.log`）。
- **真机 bug**：❌→✅ PP-OCRv6 推理在 paddlepaddle 3.3.1 上崩溃：`NotImplementedError: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`（onednn/PIR 路径）。**修复**：`pdf_ocr.py`（lls-bangong 与 lls-pdf 两支同改）在 win32 下 `enable_mkldnn=False`。修复后真机复跑，OCR 产物正确（`runs\lls-bangong\OCR 输出.txt`、`pdf_skill_ocr.txt` 均正确识别"真机测试123"）。
- **其余 A2 项**（venv+requirements 全流程、LibreOffice 默认路径命中、微软雅黑/宋体注册、保留字符文件名）：探针产物已在 `runs\lls-bangong\`（中文 测试.pdf、tiny.pdf、t.csv 等），LibreOffice 渲染链路经 A6/A8/A10/A12/A13 的渲染图间接证实命中；逐项判定待复核。

### 其余 A 项 — 产物已产出（上一会话判定"主体完成"，逐项判定待复核）

| A 项 | skill | 产物证据（real-test\runs\ 下） | 渲染核对 |
|---|---|---|---|
| A3 超长路径/中文目录/音视频转换 | lls-convert | `中文 目录 测试\`（演 示.pdf/pptx、音 频.mp3/wav 转换产物） | — |
| A5 中文字幕路径 + 双击 | lls-zimu | `中文 路径 测试\`（输入→输出清洗 .srt）、dclick_test.py | — |
| A6 教案 check/create + 渲染 | lls-jiaoan | 教案 中文 产物.docx、预检报告 中文.md、教学设计.json | jiaoan_p1/p2.png |
| A8 Markdown 转 PPT + 渲染 | lls-mdppt | 渲染 产物.pptx、演示 产物.pptx、演示 复验.pptx | mdppt_p1/p2.png、mdppt_fixed_p2.png |
| A10 简历 docx 字体渲染 | lls-jianli | 张三 简历.docx、简历数据.json | jianli_p1.png |
| A12 论文排版渲染 | lls-lunwen | 论文 排版产物.docx、预检报告 中文.md | lunwen_p1.png |
| A13 docx 修订流程渲染 | lls-docx | 合同 修订版.docx | docx_rev_p1.png |
| A14 xlsx 公式重算 | lls-xlsx | 公式表.xlsx | — |
| A3 长路径产物 | lls-convert | 18 层中文深路径下生成 长路径测试.pdf/txt（python 直写成功） | — |

渲染 PNG 由 LibreOffice（soffice）headless 转 PDF 再出图——**间接证实 Windows 下 LibreOffice 默认路径探测命中、中文名 docx/pptx 渲染正常**。

## 续测结果（2026-10-30 第二轮，A9 收尾 + A4/A7/A11/A1 + B 组 21 支）

> 本轮全部在含中文与空格的目录 `real-test\runs\lls-<slug>\中文 测试\` 下执行；逐支命令、退出码与产物见 `lls-base-skills/real-tests/windows-real-b-抽查日志.txt`，产物归档于各支 `real-tests/<slug>/windows-real/`。

### A4 lls-reportp 图文报告页面 — ✅ 通过

- PowerShell 下建含中文+空格目录、`Copy-Item` 拷 assets（doc.css/doc.js/echarts.min.js），技能自带冒烟 `Test-Path` 三项全 True。
- 手写 `index.html`（真数据来自 `revenue.csv`：分客群日营收、客单价拆解表、来源标注），本地 HTTP 服务 + 无头 Chromium 截图核对：标题/章节/双线折线图（企业客户 vs 中小企业）/中文表头表格/结论 callout 全部正常。
- `--dump-dom` 确认 `nav.toc-rail` 由 doc.js 生成 6 个锚点（竖线轨 + 悬浮弹出，属设计形态）。
- **`file://` 双击打开同样正常**（样式、目录轨、图表齐全）——这是报告页最真实的使用场景。
- 非 Windows 问题（已修，见「补充修复」）：`assets/doc.js` 的图表契约原写死汽车市场字段（`year`/`sales_m`/`penetration`，轴名「销量 百万辆」「渗透率」），非汽车主题的报告套不进去。验证时先用页面内联 `echarts.init` 绕过，之后已把 doc.js 改为字段无关的通用构建器并回归通过。
- 证据：`real-tests/lls-reportp/windows-real/中文 报告 页面/`（index.html + HTTP/file 两张渲染图）。

### A7 lls-pptp 瀑布流演示页面 — ✅ 通过（含两项前置条件）

- 校验链路：模板与中文+空格路径 deck 均 `passed: 15 cards checked`。
- **Playwright 回退候选命中（关键结论）**：playwright 1.64.1 期望 chromium revision 1248，本机只有 1217/1223/1234 → 自带浏览器不可用；脚本 `findBrowserExecutable()` 按候选顺序命中 **系统 Chrome**（`C:\Program Files\Google\Chrome\Application\chrome.exe`），导出 15 页 PDF（4,297,476 字节）成功。`--browser-executable` 指定 Edge 同样成功 → Windows 用户不必下载 playwright 浏览器。
- PowerShell 直接调用导出脚本（中文+空格路径变量传入）成功，15 页 4,308,301 字节。
- 缺依赖原始报错：`导出失败：Cannot resolve playwright. Pass --node-modules or set NODE_PATH.`（技能包不自带 playwright/pdf-lib，已补进 SKILL.md 处理纪律第 9 条）。
- **超长路径**：node 校验在 292 字符路径下 PASS（Node 内部给绝对路径加 `\\?\` 前缀，不受 260 限制）；PDF 导出 FAIL——`page.goto: net::ERR_FILE_NOT_FOUND`，即 Chrome 打不开 >260 字符的 file:// 地址，需把 deck 移到短路径。已补进失败分支第 6 行。
- pptx 导出：`导出失败：Cannot resolve @oai/artifact-tool.`（私有包，npm 不可得）——与代码级结论一致。
- 杀毒拦截：本机 `RealTimeProtectionEnabled=False`、`AntivirusEnabled=False`，**无法实测，记 N/A（不记通过）**。
- 证据：`real-tests/lls-pptp/windows-real/`（中文 deck + 首页/次页渲染图 + 完整日志）。

### A11 lls-naotu 思维导图 — ✅ 通过

- 中文大纲（4 个一级分支、三级层级、32 节点）→ `naotu_make.py` 同时产出 `.mm` 与 HTML，脚本报「节点 31 个」（不含中心主题，口径一致）。
- 独立解析 `.mm`：XML 良构、无 BOM、UTF-8、根元素 `<map version="1.0.1">`；逐层比对 32 个节点文字与大纲**逐字一致**，最大深度 3，层级归属正确。
- HTML 预览用无头 Chromium 截图核对：缩进树层级清晰、中文正常。
- 证据：`real-tests/lls-naotu/windows-real/`（大纲、.mm、.html、预览图）。

### A1 wb-open-platform-handbook-pro 上架专家 E-0 — ⏸ 部分通过（需用户动作）

- **第 1 步检测**：✅ `Get-Command ego-browser` 与 `where ego-browser` 两种写法都正确判定「未安装」（`where` 返回 exit=1「用提供的模式无法找到文件」），且 SKILL.md 已内置 Windows 分流语法 → 正确进入未安装分支。官网 `https://lite.ego.app/` 可达（确认为厂商站点）。
- **第 2 步安装**：⏸ 需用户本人下载并运行 ego lite 安装包（含 SmartScreen 拦截处理），安装第三方软件属用户动作，本次未执行。
- **第 3 步登录**：⏸ 需用户本人微信扫码。
- 因此本支记为「部分真机」，不记通过。

### B 其余 21 支抽查 — ✅ 21/21 通过（1 支 lint 按设计返回非 0）

覆盖 aiwei、baoshui、biaoshu、fenjing、hetong、htmlppt、huiyi、kejian、koushuo、pingyu、shuzhi、timu、wenan、xuanti、zhouba、shujv、gongwen、pdf、pptx、fapiao、docpage，均在中文+空格路径下按各支 SKILL.md 最小链路跑通并核对产物（JSON 良构、xlsx/pptx/docx 结构有效、Office 产物经 LibreOffice 转 PDF 出图人眼核对）。逐支明细见 `windows-real-b-抽查日志.txt`。

**本轮发现的真问题（已闭环）**：

1. **lls-docpage docx 导出静默失败（已修代码）**。`export-paper-to-docx.mjs` 的 `findPython()` 优先取 `python3`，本机 `where python3` 首条是 `python3.cmd`；Node 的 `spawnSync` 不能直接执行 `.cmd`，失败时既无 stderr 也无提示，用户只看到「python-docx fallback was unavailable or failed」，无法区分「缺模块」还是「找不到解释器」。
   修复：Windows 下 `findExecutable()` 只取真正的 `.exe`（跳过 .cmd/.bat 垫片）；`findPython()` 改为优先 `python`；回退失败时打印 `result.error` 与「可用 --python 指定解释器」。验证：修复后同样命令明确报 `ModuleNotFoundError: No module named 'lxml'`；把已装依赖的 venv 放到 PATH 前，导出成功 36,674 字节。SKILL.md 失败分支补 6、7 两行（playwright 依赖与 python-docx/lxml 前置）。
2. **lls-pptx `pptx_check.py` 对封面页 1 条误报（已修，见「补充修复」）**：4 页 deck 的第 1 页封面标题「数据看板入门」被判为「话题式标题，建议写结论句」——封面本就是 deck 名称，该规则应跳过封面。

**非 Windows 问题但值得后续优化（仅记录）**：lls-huiyi 的说话人识别不认 `[时间] 姓名：` 这种常见转写格式（报「未标注」）；lls-fenjing 对无空行整段口播稿只出 1 个镜头；lls-fapiao 的价税合计必须带 `¥` 才会提取。

## 仍未完成（需用户动作或另需决策）

1. **A1 Pro 上架专家第 2/3 步**：需用户安装 ego lite 并扫码登录后，才能跑 E 代上架全流程。
2. **杀毒拦截项**：本机未启用实时防护，无法实测。
3. **既有待决策**：交接文件列出的 13 条事项。reportp 图表契约与 pptx 封面误报已在本轮修完并验证，见下节。

## 补充修复（2026-10-30 下午，两处「待决策」已闭环）

### 一、lls-reportp 图表契约通用化

**原问题**：`assets/doc.js` 的图表构建器写死了汽车市场字段（`year`/`sales_m`/`penetration`，轴名「销量 百万辆」「渗透率」；占比图写死 `brand`/`share` 与「比亚迪/特斯拉中国」专用配色），非汽车主题的报告套不进去。这同时违反了技能自己的规则——`references/data-and-charts.md` 要求「通用构建器放 `assets/doc.js`，专用图表放页面内联脚本」，而专用实现却占着通用层。

**改法**：
- 数据块支持两种形态：显式 `{x, xName, series:[{field,name,unit,type,axis,percent,color}], data}`；或纯数组自动推断（首个非数值键作类目，其余数值键作序列，图例名回退字段名）。
- 图表族开放为 `trend`（别名 `line`/`bar`/`market-trend`）与 `share`（别名 `ranking`/`composition`/`share-ranking`）。未登记的族按 `data-type` 降级（`pie` 走占比、其余走趋势）并只提示一次——原实现对未知族直接返回 `{}`，是静默白板缺陷。
- 旧数据零改动兼容：`year/sales_m/penetration` 走内置映射，还原「销量 百万辆 / 渗透率」轴名、蓝金配色、副轴虚线。
- 顺带修一处可用性缺陷：占比横条配色原按反转后顺序分配，导致「企业客户」在趋势图是蓝色、在排行图变青色；改为按传入顺序取色，同一实体跨图同色。
- 文档同步：`page-structure.md` 的 Chart Blocks 补族名表与两种 payload 契约，`data-and-charts.md` 指明构建器字段无关，`report-template.html` 注释更新。

**验证**（`real-tests/lls-reportp/windows-real/图表契约回归/`）：用 Playwright 读取每个图表的 ECharts 实例 `option`（不看截图判定），6 个块全部 `rendered=true`、`canvasPainted=true`、无 fallback：
- 旧契约块：轴名「销量 百万辆」「渗透率」、series 名、`#2563eb`/`#b7791f` 配色、副轴虚线逐项还原；
- 新契约块（中文营收）：轴名自动生成为「企业客户 元」，类目为日期；
- 双轴块：「日营收 元」+「成交客户数 家」；
- 占比块：企业客户 `#2563eb`，与趋势块一致；
- 未登记族 `waterfall`：降级为柱状图，console 仅 1 条提示，画布非空。
`report-template.html` 按真实用法（拷到带 `assets/` 的目录）复查，图表正常且 console 无报错。

### 二、lls-pptx `pptx_check.py` 封面误报

**原问题**：4 页 deck 的封面标题「数据看板入门」被判「话题式标题，建议写结论句」。封面标题本就是 deck 名称，不该按内容页要求改写成结论句。

**改法**：封面与内容页分开判定。封面判据为「第 1 页 + 文本块 ≤3 + 总字数 <60」，命中则跳过话题式判定；内容页规则保留并补强（纯编号正则由 `[\d]+.` 扩到中文数字配 `.`/`、`，短标题排除集补上句号与分号）。用文本块数与字数而非只看页码，是为了避免把「开门就上内容」的首屏当封面放过。

**验证**（`real-tests/lls-pptx/windows-real/检查器用例/`）：
- 真实 deck：修复前 1 条误报（exit=1）→ 修复后全绿（exit=0）。
- 用例A（封面 + 4 个内容页）：封面放行；「市场分析」「1.」「背景介绍」「三个关键动作」照报；结论句标题「三日营收增长 9.9%，增量来自客户数」不报。
- 用例B（首屏即满版内容）：短标题「市场分析」仍报，未被封面豁免。
- 退出码契约未变（有警告 1、无警告 0），`--help` 与 `py_compile` 正常。

## 工具事故记录（本次真机验证自身的踩坑，2026-10-30）

测试中 ZCode 的 Bash 工具会话把工作目录切进了 312 字符的中文深路径，之后**所有 shell 通道**（主会话、子代理、定时任务的 Bash）全部 `spawn bash.exe ENOENT`——Windows CreateProcess 无法以超 260 字符的 cwd 启动进程。文件工具（Read/Write/Edit/Browser）不受影响。这本身就是一个高价值的 Windows 长路径实证案例：**在 Windows 上做超长路径测试时，测试工具自身必须用"子进程 cd /d"方式进入深路径，绝不能让外层 shell 的 cwd 进入**。恢复方式：新开会话（shell 状态随会话重建）；深路径测试目录保留勿删，供补测使用。
