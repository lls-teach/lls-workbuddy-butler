# Output Layout Reference

Use this reference when creating or organizing page deliverables.

## One Page, One Folder

Every page should live in its own folder. The folder is the deliverable bundle and should be named with a readable, filesystem-safe page slug.

Default layout:

```text
page-slug/
  index.html
  assets/
    doc.css
    doc.js
    mermaid.min.js        # only when Mermaid diagrams are used
    echarts.min.js        # only when quantitative charts are used
  data/
  images/
```

For simple pages, keep source notes directly in `index.html` or in `data/` when a local source file is useful. Do not scatter page outputs in the workspace root.

For narrative, research, product, technical, or memo pages that do not need repeatable calculations, it is acceptable for the folder to contain only `index.html` and optional assets/images. Do not add Python or chart runtime files just to assemble prose.

## File Roles

- `index.html`: final editable static page opened by the user.
- `assets/doc.css`: shared page styling.
- `assets/doc.js`: shared TOC, lightweight interaction, Mermaid initialization, and optional chart initialization.
- `assets/mermaid.min.js`: diagram runtime for pages with Mermaid workflow, architecture, sequence, state, or decision diagrams.
- `assets/echarts.min.js`: chart runtime for pages with ECharts quantitative figures.
- `data/`: reviewed source data or small local copies needed to reproduce specific claims or charts.
- `images/`: optional local visual evidence, screenshots, logos, diagrams, or other page assets.

## Naming

Use lowercase, hyphenated or underscore-separated slugs. Prefer concrete names such as `tesla-2026-brief/`, `product-launch-memo/`, `ai-agent-architecture-note/`, or `may-budget-review/`.

Windows 安全 slug 补充：slug 中禁用 `< > : " / \ | ? *`；禁用保留名 `CON`、`PRN`、`AUX`、`NUL`、`COM1`–`COM9`、`LPT1`–`LPT9`（不分大小写）；末尾禁用空格与句点；不要只靠大小写区分两个目录（Windows 同盘不区分大小写，`Report/` 与 `report/` 是同一目录）；中文或含空格的 slug 在浏览器里能打开，但发链接、打包解压时易被转码或截断，优先用小写英文连字符 slug；目录嵌套过深时注意 Windows 传统路径长度限制，保持路径短。

Inside the folder, prefer stable filenames: `index.html`, `assets/doc.css`, `assets/doc.js`, optional `assets/mermaid.min.js`, and optional `assets/echarts.min.js`. The page title belongs inside the HTML, not in every filename.

## Trae Rendering Contract


For pages with dependencies, keep every dependency inside the page folder and reference it with relative paths only. Do not use absolute local paths, `file://` URLs, remote CDNs, or workspace-global asset folders in the final HTML.

注意：本包内未给出该渲染注释的具体文本（模板与各 reference 均无此文本），静态检查中“页首有 Trae 渲染注释”一项在拿到平台现行文本前只能记为“无法按字面核对”，不要凭空编造一条注释冒充平台要求。

## Static Checks

For default static pages, run lightweight checks:

- `index.html` starts with the required Trae rendering comment（具体文本以平台现行要求为准；本包未规定文本时该项记为无法按字面核对，见 Trae Rendering Contract 一节）；
- local CSS and JS paths resolve;
- local image paths resolve;
- local Mermaid runtime exists and Mermaid blocks remain readable in `index.html` when diagrams are present;
- ECharts runtime exists and chart JSON blocks parse when quantitative charts are present;
- source links are present for material claims when relevant;
- dates are explicit for current or time-sensitive topics;
- headings populate the table of contents behavior;
- no placeholder text, stale sample titles, visible debug labels, or broken anchors remain.
