#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);
const positional = args.filter((arg) => !arg.startsWith("--"));
const inputFile = positional[0];
const outputFile = positional[1];
const mmdcArg = readOption("--mmdc");
const puppeteerConfigArg = readOption("--puppeteer-config");
const theme = readOption("--theme") || "neutral";
const background = readOption("--backgroundColor") || "transparent";
const quiet = args.includes("--quiet");

if (!inputFile || !outputFile) {
  console.error([
    "Usage:",
    "  node render-mermaid-to-svg.mjs diagram.mmd diagram.svg [options]",
    "",
    "Options:",
    "  --mmdc=/path/to/mmdc              Use a specific Mermaid CLI executable.",
    "  --theme=neutral                  Mermaid theme: default, neutral, forest, dark, base.",
    "  --backgroundColor=transparent    SVG background color.",
  "  --puppeteer-config=config.json   Pass a puppeteer config file to mmdc (e.g. --no-sandbox on root/CI).",
    "  --quiet                          Print only the output path.",
    "",
    "Renders Mermaid source to SVG for insertion into Build Doc figures.",
  ].join("\n"));
  process.exit(2);
}

const inputPath = path.resolve(inputFile);
const outputPath = path.resolve(outputFile);

if (!fs.existsSync(inputPath)) {
  fail(`Input Mermaid file not found: ${inputPath}`);
}

const mmdc = mmdcArg || findExecutable("mmdc");
if (!mmdc) {
  fail([
    "Mermaid CLI (mmdc) was not found.",
    "Install it with: npm install -g @mermaid-js/mermaid-cli",
    "Then rerun this script, or pass --mmdc=/path/to/mmdc.",
  ].join("\n"));
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
// Windows 上 npm 安装的 mmdc 是 .cmd 垫片，不用 shell 无法直接启动。
const useShell = process.platform === "win32" && /\.cmd$/i.test(mmdc);
const mmdcArgs = [
  "-i", inputPath,
  "-o", outputPath,
  "--theme", theme,
  "--backgroundColor", background,
];
if (puppeteerConfigArg) mmdcArgs.push("-p", puppeteerConfigArg);
const result = spawnSync(mmdc, mmdcArgs, {
  encoding: "utf8",
  maxBuffer: 1024 * 1024 * 10,
  shell: useShell,
});

if (result.error) fail(`Failed to run mmdc: ${result.error.message}`);
if (result.status !== 0) {
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  process.exit(result.status || 1);
}

if (!quiet) {
  console.log(`Wrote SVG: ${outputPath}`);
} else {
  console.log(outputPath);
}

function readOption(name) {
  const prefix = `${name}=`;
  const found = args.find((arg) => arg.startsWith(prefix));
  return found ? found.slice(prefix.length) : "";
}

function findExecutable(command) {
  // Windows 上 npm 的本地可执行文件是 .cmd/.exe 垫片，无后缀的原名不存在。
  const suffixes = process.platform === "win32" ? ["", ".cmd", ".exe"] : [""];
  for (const base of [path.resolve("node_modules/.bin", command), path.join(os.homedir(), ".local/bin", command)]) {
    for (const suffix of suffixes) {
      if (fs.existsSync(base + suffix)) return base + suffix;
    }
  }
  // Windows 没有 Unix 的 `command -v`，用 where.exe 查找；否则查到的一律为空。
  if (process.platform === "win32") {
    const result = spawnSync("where", [command], { encoding: "utf8" });
    if (result.status === 0) return result.stdout.trim().split(/\r?\n/)[0];
    return "";
  }
  const result = spawnSync("command", ["-v", command], {
    encoding: "utf8",
    shell: true,
  });
  if (result.status === 0) return result.stdout.trim().split(/\r?\n/)[0];
  return "";
}

function fail(message) {
  console.error(message);
  process.exit(1);
}
