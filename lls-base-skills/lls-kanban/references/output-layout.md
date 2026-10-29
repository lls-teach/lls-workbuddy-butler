# Output Layout Reference

Use this reference when creating or organizing dashboard deliverables.

## One Dashboard, One Folder

Every dashboard should live in its own folder. The folder is the deliverable bundle and should be named with a readable, filesystem-safe dashboard slug.

Recommended layout:

```text
dashboard-slug/
  index.html
  dashboard_data.json
  dashboard.py
  dashboard_runtime.js
  echarts.min.js
  data/
    source-file.xlsx
    snapshots/
      2026-06-25.json
      2026-06-26.jsonl
```

For simple dashboards, source data may sit beside `dashboard.py`, but recurring automation outputs should live under `data/snapshots/`. Do not scatter dashboard outputs in the workspace root.

## File Roles

- `index.html`: final single-file dashboard opened by the user.
- `dashboard_data.json`: generated payload for review/debugging and reproducibility.
- `dashboard.py`: copied and adapted generator from `assets/dashboard_template.py`. It locates `echarts.min.js` and `dashboard_runtime.js` in its own folder, so all three files must be copied together — copying `dashboard.py` alone fails with a missing-file error.
- `dashboard_runtime.js`: copied shared browser runtime used during generation and inlined into `index.html`.
- `echarts.min.js`: copied chart runtime used during generation and inlined into `index.html`.
- `data/`: reviewed source data or small local copies needed to reproduce the dashboard.
- `data/snapshots/`: immutable daily source snapshots produced by automation.

## Naming

Use lowercase, hyphenated or underscore-separated slugs. Prefer concrete names such as `daily-revenue-dashboard/`, `finance-command-center/`, or `customer-health-dashboard/`.

Windows notes: keep slug and asset filenames in their exact lowercase spelling (`dashboard.py`, `echarts.min.js`, `dashboard_runtime.js`) — Windows filesystems are case-insensitive and will mask a case typo that then fails on Linux/macOS. Do not use Windows reserved names (`CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`) or characters `< > : " / \ | ? *` in a slug.

Inside the folder, prefer stable filenames: `index.html`, `dashboard_data.json`, and `dashboard.py`. The dashboard title belongs inside the HTML, not in every filename.

## Trae Rendering Contract

The generated `index.html` must start with `<!doctype html>` on line 1, followed by a source comment in the file head (line 2). Do not put any comment before the doctype: a comment before it triggers quirks mode and can break dashboard layout. The final assistant response must include the `index.html` path with a `computer://` prefix so Trae can render the dashboard.

Keep the visible dashboard self-contained. `index.html` should inline the copied ECharts and dashboard runtime scripts; any supporting data or automation files must stay inside the dashboard folder.

## Validation

Run validation against the folder's final HTML:

```bash
node <SKILL_ROOT>/scripts/validate-echarts-dashboard.mjs dashboard-slug/index.html
```
