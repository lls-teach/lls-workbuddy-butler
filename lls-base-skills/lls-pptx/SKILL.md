---
name: lls-pptx
slug: lls-pptx
display_name: PPT演示文稿
displayName: "PPT演示文稿"
display_name_en: "PPT Slides Toolkit"
description: 从一句话需求到可编辑 .pptx 成片：做 PPT，做美观、有审美的 PPT。发牌定美术方向（治 AI 默认审美）、六套风格成片、按槽位指派版式、渲染质检；也支持从参考图提炼视觉系统，优化已有 PPT 的层级、信息密度、字体、间距与构图。
description_zh: "做 PPT，做美观、有审美的 PPT：发牌定方向、版式指派、渲染质检，一句话出可编辑 .pptx。"
description_en: "Make PPTs — beautiful, tasteful ones: deal an art direction, assign layouts per slot, render-QC, one sentence to an editable .pptx."
examples_zh:
  - 用咨询研报风格，做一页数据对比 PPT
  - 按这张参考图，提炼一套可复用的视觉系统
  - 把这份 PPT 的层级和信息密度优化一下
examples_en:
  - Build a data-comparison slide in the consulting research style
  - Distill a reusable visual system from this reference image
  - Improve the hierarchy and density of this deck
version: 2.10.1
---

# 精美 PPT

担任演示文稿的视觉总监。给出清晰的审美判断和可复用设计系统，同时允许模型根据当前环境选择合适的创建工具。

## 与演示文稿工作流配合

1. 如果当前环境提供演示文稿创建、编辑、引用或质量检查规范，先遵循相关规范。
2. 把用户提供的 PPT 和图片视为视觉证据。除非用户明确要求重设计，否则保留既有模板的身份特征。
3. 创建全新、可编辑的 `.pptx` 时，优先考虑 PptxGenJS，尤其适合重复版式、原生图表、表格、模板和程序化检查。使用这条路线时读取 [PptxGenJS 实现指引](references/pptxgenjs-implementation.md)。
4. 用户需要可复用模板时，尽量让图表、表格、文字和形状保持可编辑。
5. 在 PptxGenJS 中，序号、日期、百分比、金额、页码和短代码应使用实现指引中的单行文本保护组件。

## 选择实现路线

- 从零创建 PowerPoint、批量生成相关页面、编码可复用设计系统或保持常见商务内容可编辑时，优先考虑 PptxGenJS。
- 需要忠实保留已有母版、占位符或复杂继承关系时，优先使用能够原生编辑现有 PPT 的工具。
- 交付物明确为 Google Slides 时，使用对应原生工具。
- 浏览器动画、交互或网页交付是核心需求时，可选择 HTML 演示文稿路线。
- 以上是建议，不是限制。由交付物、内容和可用环境决定最终实现方式。

## 指导视觉系统

1. 先明确沟通任务：受众、需要促成的判断或行动、内容类型、展示场景和情绪基调。
2. 排版前写一份紧凑的风格简报：三个形容词、一个设计张力、密度、配色逻辑、字体逻辑、图片行为和空间节奏。
3. 每套 PPT 都读取 [视觉基础](references/foundations.md)。
4. 只读取最接近任务的一份风格配方：
   - 咨询或研究报告：[咨询研报](references/consulting-research.md)
   - 正式管理或工作汇报：[正式工作汇报](references/formal-work-report.md)
   - 中国社区、党建或 civic 活动：[社区党建](references/civic-community.md)
   - 高饱和艺术市集或创意海报：[艺术市集](references/art-market.md)
   - 编辑、文化或画廊类演示：[编辑画册](references/editorial-gallery.md)
   - 历史教学、博物馆教育或时代叙事：[历史教学](references/historical-education.md)
5. 没有完全匹配的配方时，使用 [风格简报模板](references/style-brief-template.md) 创造新风格，或有意识地组合两种风格。

## 审美门禁（做 PPT 前必做）

先读 [审美门禁](references/taste-aesthetics.md)，再读风格配方。必做的六件事：

1. 按 [设计简报模板](references/taste-brief-template.md) 写主题清单（8–12 条，竞品写不出来）、
   逐页论点（顺序＝论点顺序，打破八股）、idea 句（过竞争者测试）。
2. 发牌定美术方向：跑 `python scripts/taste_cards.py --deal 3 --out ./deal/` 亮三张牌面图给用户看，
   请用户选一张（可附一句话推荐，但绝不代选）；亮牌后主动说"不满意说'重发'，再来三张"。
   用户选定后跑 `python scripts/taste_deal.py --palette <id>` 打印方向单，直接使用。
   颜色按牌走，版式仍按风格配方走（比例按配方）。玩法见 [发牌指引](references/taste-deal.md)。
   版式指派：`python scripts/taste_layouts.py --assign --pages <N> --seed <S>` 给每页指派版式牌
   （同构图一 deck 最多 2 次），结果写进简报。重抽规则：一次只换一个槽位——
   `taste_deal.py --redraw palette` 换配色、`taste_layouts.py --redraw-layout <页> --current <id>` 换某页版式，
   必须一句话理由写进简报；禁止"看着不顺眼"重抽。
3. 按主题契合度选一套风格配方并写一句话理由；不混搭（本条取代"有意识地组合两种风格"）。
4. 生成前逐项过门禁清单（【数据】有研究支撑，【品味】是审美决定；tells 详见 [tells 注册表](references/taste-tells.md)），
   并跑 `python scripts/taste_lint.py --scan-js <构建脚本>` 过文案：
   标题不超两行【数据】、无眉标【数据】、无编号标签【品味】、无细线【品味】、无渐变【数据】、
   无静止阴影【数据】、无助手配色【数据】、无小号大写标签【数据】、无图标卡片阵【数据】、
   无玻璃/emoji/装饰形【数据】、标题无花式强调【品味】、一页三种干活字号【数据】、特大与常规比拉开【数据】。
   检查分 PASS/WARN/FAIL：FAIL 全修；WARN 修掉或写一句话辩护进交付报告。
5. 渲染后先跑 `python scripts/taste_inspect.py --pages "<渲染图>" --palette <牌id>` 做程序化测量
   （画幅比/空洞/贴边/跑出配色），再按 [十三遍看图法](references/taste-critique.md) 看图，
   改最严重的三个问题，最多三轮；删了装饰却什么都没补的页叫空，不叫干净。
6. 交付附 [设计报告](references/taste-report-template.md)：方向＋种子、idea 句、重抽理由、
   检查结果、没跑过的检查一个不落。

## 先构图，再按风险验证

1. 每页只设一个主要结论，并选择能表达它的页面轮廓：证据网格、对比、时间线、表格、满版图片、海报构图或综合结论。
2. 先建立页面的垂直结构：页眉、标题、标题与正文的间距、主体内容区、结论或来源区、页脚安全区。
3. 有意识地控制密度。先通过分组、对齐和证据结构增加信息密度，再考虑缩小字号。
4. 在字体、外边距、颜色角色、线条和页脚规则一致的前提下，变化页面轮廓。
5. 默认只做一次最终渲染。先看缩略图总览，再检查封面、信息最密页、特殊媒体或图表页、结束页及总览中的异常页。
6. 保留低成本结构检查，如文件完整性、未解析占位符、讲者备注和程序化溢出检测。
7. 仅在高风险、异常密集、明显不一致或工作流明确要求时逐页全尺寸检查。
8. 仅在新视觉系统、长文档重复版式或布局行为不确定时，先渲染代表页。
9. 只有用户要求跨应用交付，或字体、裁剪、图表和媒体存在已知风险时，才进行 PowerPoint、LibreOffice 或 Google Slides 交叉渲染。
10. 修改到页面从标题到页脚都被有意占用，同时不显拥挤；没有相关变化时，不重复相同验证。

## 把配方当作提示，而不是牢笼

- 将字号、间距和颜色范围视为起点，不视为机械验收规则。
- 当意外变化能加强沟通效果时，保留它。
- 混合风格时声明主风格和辅助风格，避免把两种风格平均成平庸折中。
- 当证据、受众或展示场景提出更强要求时，让内容覆盖配方。
- 成功的新风格可以沿用现有字段记录为新的配方。
