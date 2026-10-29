#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const arg = process.argv[2];

if (arg === "--help" || arg === "-h") {
  console.log("Usage: node validate-echarts-dashboard.mjs path/to/dashboard.html");
  console.log("Checks an offline ECharts dashboard HTML file (KPI tiles, chart panels,");
  console.log("time controls, freshness indicator, Data Source modal, doctype first line");
  console.log("with a source comment in the file head). Exits 0 when all checks pass,");
  console.log("1 when any check fails, 2 when no file argument is given.");
  process.exit(0);
}

const file = arg;

if (!file) {
  console.error("Usage: node validate-echarts-dashboard.mjs path/to/dashboard.html");
  process.exit(2);
}

let html;
try {
  html = fs.readFileSync(file, "utf8");
} catch (error) {
  console.error(`error - cannot read ${file}: ${error.message}`);
  process.exit(1);
}
const visible = html.split('<div id="modalBackdrop"', 1)[0];
const checks = [];

function count(pattern) {
  const matches = html.match(pattern);
  return matches ? matches.length : 0;
}

function visibleCount(pattern) {
  const matches = visible.match(pattern);
  return matches ? matches.length : 0;
}

function check(condition, message) {
  checks.push({ ok: Boolean(condition), message });
}

const dashboardShells = visibleCount(/<main class="dashboard-shell"/g);
const kpiTiles = visibleCount(/<section class="kpi-tile"/g);
const chartPanels = visibleCount(/<section class="dashboard-panel chart-panel"/g);
const tablePanels = visibleCount(/<section class="dashboard-panel table-panel"/g);
const chartDivs = visibleCount(/<div class="chart" id="[^"]+"/g);
const chartFactories = count(/const chartFactories\s*=/g);
const runtimeCalls = count(/setupDashboardRuntime\s*\(/g);

check(html.includes("data-range-preset"), "has segmented time presets");
check(html.includes("rangeStart") && html.includes("rangeEnd"), "has explicit date range inputs");
check(html.includes("activeRangeLabel"), "has active range label");
check(html.includes("dataFreshness"), "has data freshness indicator");
check(html.includes("modalBackdrop"), "has Data Source modal");
check(runtimeCalls >= 1, "calls setupDashboardRuntime");
check(chartFactories >= 1, "declares chartFactories");
check(dashboardShells === 1, "has one dashboard shell");
check(kpiTiles >= 1, "has at least one KPI tile");
check(chartPanels >= 1, "has at least one chart panel");
check(chartDivs >= chartPanels, "chart panels have chart containers");
check(tablePanels >= 0, "table panel count is valid");
check(!html.includes("<nav class=\"toc-rail\""), "does not use report TOC rail");
check(!html.includes("<article class=\"report-card\""), "does not use report-card feed markup");
check(!html.includes("<header class=\"report-title\""), "does not use document report title header");
check(html.includes("View Data Source"), "has View Data Source action");
check(html.includes("toggleEdit"), "has Edit chart action");
check(!html.includes("toISOString().slice(0, 10)"), "does not format business dates through UTC");
check(!html.includes("[TITLE]"), "does not contain [TITLE] placeholder");
check(!html.includes("TODO"), "does not contain TODO placeholder");
// A comment before <!doctype html> would trigger quirks mode and can break
// layout, so the doctype must stay on line 1 and the source comment follows
// it in the file head instead. Lines are trimmed so a BOM or CRLF line ending
// (for example a file written on Windows) does not fail the check.
const withoutBom = html.replace(/^\uFEFF/, "");
const firstLine = withoutBom.split(/\r?\n/, 1)[0].trim();
const fileHead = withoutBom.split(/\r?\n/).slice(0, 20).join("\n");
check(firstLine.toLowerCase() === "<!doctype html>", "starts with doctype on line 1");
check(fileHead.includes("<!--") && fileHead.includes("-->"), "has source comment in file head");

const failed = checks.filter((item) => !item.ok);

for (const item of checks) {
  const prefix = item.ok ? "ok" : "fail";
  console.log(`${prefix} - ${item.message}`);
}

console.log(
  `summary - ${path.basename(file)}: ${kpiTiles} KPI tiles, ${chartPanels} chart panels, ${tablePanels} table panels`
);

if (failed.length) {
  process.exit(1);
}
