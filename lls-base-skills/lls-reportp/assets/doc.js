(function () {
  const palette = {
    blue: "#2563eb",
    teal: "#0f766e",
    rose: "#b83f58",
    gold: "#b7791f",
    line: "#e6ebf0",
    axis: "#475569"
  };
  const chartColors = [palette.blue, palette.teal, palette.gold, palette.rose, "#64748b", "#7c3aed"];

  function readJson(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || "null");
    } catch (error) {
      console.warn("Invalid JSON block", id, error);
      return null;
    }
  }

  function pct(value) {
    return Number(value).toFixed(1) + "%";
  }

  function grid() {
    return { left: 58, right: 48, top: 52, bottom: 58, containLabel: true };
  }

  // ——— 图表数据契约 ————————————————————————————————————————————————
  // 数据块（data-data 指向的 <script type="application/json">）支持两种形态：
  //   A. 显式：{ "x": "类目字段", "xName": "横轴名", "data": [ ... ],
  //             "series": [{ "field", "name", "unit", "type", "axis", "color", "percent" }],
  //             "yAxes": [{ "name", "percent" }] }
  //   B. 纯数组：[{ "类目字段": "…", "数值字段A": 1, "数值字段B": 2 }]
  //      取第一个非数值键作类目，其余数值键作序列，图例名用字段名。
  // 图表族（data-chart，大小写不敏感）：
  //   trend | line | bar | market-trend（旧名）→ 多序列趋势，线/柱可切换
  //   share | ranking | composition | share-ranking（旧名）→ 占比环图或排行横条
  // 未登记的族按 data-type 降级（pie 走占比、其余走趋势）并在控制台提示一次，
  // 不再渲染空白图。
  const TREND_KINDS = new Set(["trend", "line", "bar", "market-trend"]);
  const SHARE_KINDS = new Set(["share", "ranking", "composition", "share-ranking"]);

  // 趋势图序列默认取色与前两色顺序保持一致，既有页面的配色不变
  const trendColors = [palette.blue, palette.gold, palette.teal, palette.rose, "#64748b", "#7c3aed"];

  // 旧数据（纯数组 year/sales_m/penetration）的显示名与单位映射，保证既有页面外观不变
  const LEGACY_FIELDS = {
    sales_m: { name: "销量", unit: "百万辆" },
    penetration: { name: "渗透率", percent: true, axis: 1 }
  };

  function isNumeric(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function formatNum(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return String(value === undefined || value === null ? "" : value);
    // 万级以上加千分位便于阅读，小数字保持原样以免改变既有页面观感
    return Math.abs(n) >= 10000 ? n.toLocaleString("zh-CN") : String(n);
  }

  function formatValue(value, series) {
    const n = Number(value);
    if (series && series.percent) {
      return (Number.isFinite(n) ? n.toFixed(1) : String(value)) + "%";
    }
    const text = Number.isFinite(n) ? formatNum(n) : String(value === undefined || value === null ? "" : value);
    return series && series.unit ? text + " " + series.unit : text;
  }

  function pickField(obj, keys) {
    for (const key of keys) {
      if (obj && obj[key] !== undefined && obj[key] !== null && obj[key] !== "") return obj[key];
    }
    return undefined;
  }

  function axisNameOf(members) {
    if (!members.length) return "";
    const first = members[0];
    if (first.name && first.unit) return first.name + " " + first.unit;
    return first.name || "";
  }

  function normalizeTrend(rows) {
    // 形态 A：显式声明
    if (!Array.isArray(rows) && rows && Array.isArray(rows.series)) {
      const data = Array.isArray(rows.data) ? rows.data : [];
      const xKey = rows.x || Object.keys(data[0] || {})[0] || "x";
      const series = rows.series
        .map((item) => ({
          field: item.field || item.key,
          name: item.name || item.field || item.key,
          unit: item.unit || "",
          percent: Boolean(item.percent || item.isPercent),
          axis: Number(item.axis) === 1 ? 1 : 0,
          type: item.type,
          color: item.color
        }))
        .filter((item) => Boolean(item.field));
      return { rows: data, xKey, xName: rows.xName || "", series, yAxes: rows.yAxes || null };
    }
    // 形态 B：纯数组自动推断
    const data = Array.isArray(rows) ? rows : [];
    const sample = data[0] || {};
    const keys = Object.keys(sample);
    const xKey = keys.find((key) => !isNumeric(sample[key])) || keys[0] || "x";
    const valueKeys = keys.filter((key) => key !== xKey && data.some((row) => isNumeric(row[key])));
    const series = valueKeys.map((key) => {
      const legacy = LEGACY_FIELDS[key] || {};
      return {
        field: key,
        name: legacy.name || key,
        unit: legacy.unit || "",
        percent: Boolean(legacy.percent),
        axis: legacy.axis === 1 ? 1 : 0
      };
    });
    return { rows: data, xKey, xName: "", series, yAxes: null };
  }

  function normalizeShare(rows) {
    const data = Array.isArray(rows) ? rows : rows && Array.isArray(rows.data) ? rows.data : [];
    const nameKeys = [(rows && rows.name) || "name", "name", "brand", "label", "category", "segment", "item"];
    const valueKeys = [(rows && rows.value) || "value", "value", "share", "amount", "count", "total"];
    const items = data.map((row) => ({
      name: String(pickField(row, nameKeys) || ""),
      value: Number(pickField(row, valueKeys) || 0),
      color: row.color
    }));
    const declared = rows && Number(rows.total);
    const sum = items.reduce((acc, item) => acc + (Number.isFinite(item.value) ? item.value : 0), 0);
    const total = Number.isFinite(declared) && declared > 0 ? declared : sum;
    // 各值之和约等于 100 时，说明数值本身即百分比，轴与标签按百分比呈现
    const valuesArePercent = total > 0 && Math.abs(total - 100) < 5;
    return { items, total, valuesArePercent };
  }

  function trendOption(spec, type) {
    const { rows, xKey, xName, series, yAxes } = spec;
    const xs = rows.map((row) => row[xKey]);
    const mainType = type === "bar" ? "bar" : "line";
    const hasSecond = series.some((item) => item.axis === 1);

    const groups = [{ index: 0, members: series.filter((item) => item.axis === 0) }];
    if (hasSecond) groups.push({ index: 1, members: series.filter((item) => item.axis === 1) });

    const yAxis = groups.map((group) => {
      const declared = Array.isArray(yAxes) ? yAxes[group.index] : null;
      const percent = declared
        ? Boolean(declared.percent)
        : group.members.some((item) => item.percent);
      const name = (declared && declared.name) || axisNameOf(group.members);
      return {
        type: "value",
        name,
        splitLine: { lineStyle: { color: palette.line } },
        axisLabel: percent ? { formatter: (value) => value + "%" } : { formatter: (value) => formatNum(value) }
      };
    });

    const chartSeries = series.map((item, index) => {
      const isSecond = item.axis === 1;
      const kind = isSecond ? "line" : mainType;
      const option = {
        name: item.name,
        type: kind,
        color: item.color || trendColors[index % trendColors.length],
        data: rows.map((row) => row[item.field])
      };
      if (isSecond) {
        option.yAxisIndex = 1;
        option.smooth = true;
        option.lineStyle = { width: 3, type: "dashed" };
      } else if (kind === "line") {
        option.smooth = true;
        option.lineStyle = { width: 3 };
      }
      return option;
    });

    return {
      animation: false,
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const list = Array.isArray(params) ? params : [params];
          if (!list.length) return "";
          const head = list[0].axisValueLabel === undefined ? list[0].name : list[0].axisValueLabel;
          const lines = list.map((param) => {
            const item = series[param.seriesIndex] || {};
            return param.marker + " " + param.seriesName + "：" + formatValue(param.value, item);
          });
          return [head].concat(lines).join("<br/>");
        }
      },
      legend: { top: 8 },
      grid: grid(),
      xAxis: { type: "category", data: xs, name: xName || undefined, nameLocation: "middle", nameGap: 30 },
      yAxis,
      series: chartSeries
    };
  }

  function shareOption(spec, type) {
    const { items, total, valuesArePercent } = spec;
    const shareOf = (value) => (total > 0 ? (value / total) * 100 : 0);
    const formatAxis = (value) => (valuesArePercent ? value + "%" : formatNum(value));

    if (type === "pie") {
      return {
        animation: false,
        color: chartColors,
        tooltip: {
          trigger: "item",
          formatter: (param) =>
            param.marker + " " + param.name + "：" + formatNum(param.value) + "（" + pct(param.percent) + "）"
        },
        legend: { bottom: 8, type: "scroll" },
        series: [
          {
            type: "pie",
            radius: ["42%", "70%"],
            center: ["50%", "42%"],
            data: items.map((item) =>
              item.color
                ? { name: item.name, value: item.value, itemStyle: { color: item.color } }
                : { name: item.name, value: item.value }
            ),
            label: { formatter: (param) => param.name + "\n" + pct(param.percent) }
          }
        ]
      };
    }

    // 排行横条：自上而下按传入顺序（ECharts 的类目轴自下而上，故反转）。
    // 配色按传入顺序分配后再反转，保证同一实体在不同图表里颜色一致。
    const ordered = items.map((item, index) => ({
      ...item,
      presetColor: item.color || chartColors[index % chartColors.length]
    }));
    const reversed = ordered.slice().reverse();
    return {
      animation: false,
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        formatter: (params) => {
          const list = Array.isArray(params) ? params : [params];
          if (!list.length) return "";
          const param = list[0];
          const item = reversed[param.dataIndex] || {};
          return (
            param.marker +
            " " +
            param.name +
            "：" +
            formatNum(param.value) +
            "（" +
            pct(shareOf(Number(item.value) || 0)) +
            "）"
          );
        }
      },
      grid: { left: 92, right: 42, top: 28, bottom: 24, containLabel: true },
      xAxis: {
        type: "value",
        axisLabel: { formatter: formatAxis },
        splitLine: { lineStyle: { color: palette.line } }
      },
      yAxis: { type: "category", data: reversed.map((item) => item.name) },
      series: [
        {
          name: "数值",
          type: "bar",
          data: reversed.map((item) => ({
            value: item.value,
            itemStyle: { color: item.presetColor }
          })),
          label: { show: true, position: "right", formatter: (param) => formatAxis(param.value) }
        }
      ]
    };
  }

  const warnedChartKinds = new Set();

  function buildOption(kind, rows, type) {
    const family = String(kind || "").trim().toLowerCase();
    if (SHARE_KINDS.has(family)) return shareOption(normalizeShare(rows), type);
    if (TREND_KINDS.has(family)) return trendOption(normalizeTrend(rows), type);
    // 未登记的族：按 data-type 降级，避免静默渲染空白图
    if (!warnedChartKinds.has(family)) {
      warnedChartKinds.add(family);
      console.warn(
        "doc.js: 未登记的 data-chart 族，已按 data-type 降级渲染：" + (kind || "(空)") +
          "；可用族见 assets/doc.js 顶部注释"
      );
    }
    return type === "pie" ? shareOption(normalizeShare(rows), type) : trendOption(normalizeTrend(rows), type);
  }

  function setupToc() {
    const nav = document.querySelector(".toc-rail");
    const page = document.querySelector(".doc-page");
    if (!nav || !page) {
      if (document.querySelector("header[id], section[id]")) {
        console.warn(
          "doc.js: 未找到 nav.toc-rail 或 article.doc-page，目录未生成；" +
            "请按 report-template.html 使用 toc-rail + doc-page，旧的 doc-toc/doc 类名不再被识别。"
        );
      }
      return;
    }

    const targets = Array.from(
      page.querySelectorAll("header[id], section[id]")
    ).filter((block) => block.querySelector("h1, h2"));

    const lines = document.createElement("div");
    const popup = document.createElement("div");
    lines.className = "toc-lines";
    popup.className = "toc-popup";

    targets.forEach((target) => {
      const heading = target.querySelector("h1, h2");
      const label = heading.textContent.trim();
      const line = document.createElement("a");
      const link = document.createElement("a");
      line.className = "toc-line";
      line.href = "#" + target.id;
      line.dataset.target = target.id;
      line.setAttribute("aria-label", label);
      link.href = "#" + target.id;
      link.dataset.target = target.id;
      link.textContent = label;
      lines.appendChild(line);
      popup.appendChild(link);
    });

    nav.replaceChildren(lines, popup);
    const links = Array.from(nav.querySelectorAll("a[data-target]"));
    function setActive(id) {
      links.forEach((link) => link.classList.toggle("active", link.dataset.target === id));
    }

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top))[0];
          if (visible) setActive(visible.target.id);
        },
        { rootMargin: "-22% 0px -62% 0px", threshold: 0.01 }
      );
      targets.forEach((target) => observer.observe(target));
    } else if (links[0]) {
      links[0].classList.add("active");
    }
  }

  function showChartFallback(block, message) {
    if (block.querySelector(".chart-fallback")) return;
    const note = document.createElement("p");
    note.className = "chart-fallback";
    note.textContent = message;
    block.appendChild(note);
  }

  function setupCharts() {
    const blocks = Array.from(document.querySelectorAll("[data-chart]"));
    if (!blocks.length) return;
    if (!window.echarts) {
      console.warn(
        "doc.js: 未找到 window.echarts，图表未渲染；" +
          "请确认 assets/echarts.min.js 已随页交付并在 doc.js 之前引入。"
      );
      blocks.forEach((block) =>
        showChartFallback(block, "图表未能加载：未找到 ECharts 资源，请确认 assets/echarts.min.js 已随页交付并在 doc.js 之前引入。")
      );
      return;
    }
    const instances = [];
    blocks.forEach((block) => {
      const canvas = block.querySelector(".chart-canvas");
      const dataId = block.getAttribute("data-data");
      const chartKind = block.getAttribute("data-chart");
      const initialType = block.getAttribute("data-type") || "line";
      const rows = readJson(dataId);
      if (!canvas || !rows) {
        console.warn("doc.js: 图表块缺少画布或数据，跳过渲染", {
          chart: chartKind,
          data: dataId,
          hasCanvas: Boolean(canvas),
          hasRows: Boolean(rows)
        });
        showChartFallback(block, "图表未能加载：请检查 data-data 指向的 JSON 数据块与 .chart-canvas 画布是否齐全。");
        return;
      }
      const chart = echarts.init(canvas, null, { renderer: "canvas" });
      function optionFor(type) {
        return buildOption(chartKind, rows, type);
      }
      chart.setOption(optionFor(initialType), true);
      instances.push(chart);

      block.querySelectorAll("[data-chart-type]").forEach((button) => {
        button.classList.toggle("active", button.dataset.chartType === initialType);
        button.addEventListener("click", () => {
          block
            .querySelectorAll("[data-chart-type]")
            .forEach((item) => item.classList.toggle("active", item === button));
          chart.setOption(optionFor(button.dataset.chartType), true);
        });
      });
    });

    window.addEventListener("resize", () => {
      instances.forEach((chart) => chart.resize());
    });
  }

  function setupMermaid() {
    if (!window.mermaid || !document.querySelector(".mermaid")) return;
    window.mermaid.initialize({
      startOnLoad: true,
      securityLevel: "loose",
      theme: "base",
      themeVariables: {
        fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, sans-serif",
        primaryColor: "#eef4ff",
        primaryBorderColor: "#b9cdfd",
        primaryTextColor: "#2f302d",
        lineColor: "#9aa1ad",
        textColor: "#2f302d",
        mainBkg: "#ffffff",
        clusterBkg: "#f7f8fa",
        clusterBorder: "#e6e8ec"
      },
      flowchart: {
        htmlLabels: true,
        curve: "basis",
        padding: 14,
        nodeSpacing: 42,
        rankSpacing: 58
      }
    });
  }

  const lucideIcons = {
    maximize2: [
      ["path", { d: "M15 3h6v6" }],
      ["path", { d: "m21 3-7 7" }],
      ["path", { d: "m3 21 7-7" }],
      ["path", { d: "M9 21H3v-6" }]
    ],
    x: [
      ["path", { d: "M18 6 6 18" }],
      ["path", { d: "m6 6 12 12" }]
    ]
  };

  function lucideIcon(name) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "lucide-icon");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    (lucideIcons[name] || []).forEach(([tag, attrs]) => {
      const child = document.createElementNS("http://www.w3.org/2000/svg", tag);
      Object.entries(attrs).forEach(([key, value]) => child.setAttribute(key, value));
      svg.appendChild(child);
    });
    return svg;
  }

  function setupDiagramZoom() {
    const frames = Array.from(document.querySelectorAll(".mermaid-frame"));
    if (!frames.length) return;

    const lightbox = document.createElement("div");
    const panel = document.createElement("div");
    const close = document.createElement("button");
    const content = document.createElement("div");
    lightbox.className = "diagram-lightbox";
    panel.className = "diagram-lightbox-panel";
    close.className = "diagram-lightbox-close";
    close.type = "button";
    close.title = "Close";
    close.setAttribute("aria-label", "Close enlarged diagram");
    close.appendChild(lucideIcon("x"));
    content.className = "diagram-lightbox-content";
    panel.append(close, content);
    lightbox.appendChild(panel);
    document.body.appendChild(lightbox);

    function closeLightbox() {
      lightbox.classList.remove("open");
      content.replaceChildren();
      document.body.style.overflow = "";
    }

    function openLightbox(frame) {
      const svg = frame.querySelector("svg");
      const mermaidSource = frame.querySelector(".mermaid");
      const clone = svg ? svg.cloneNode(true) : mermaidSource ? mermaidSource.cloneNode(true) : null;
      if (!clone) return;
      content.replaceChildren(clone);
      lightbox.classList.add("open");
      document.body.style.overflow = "hidden";
      close.focus();
    }

    close.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", (event) => {
      if (event.target === lightbox) closeLightbox();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && lightbox.classList.contains("open")) closeLightbox();
    });

    frames.forEach((frame) => {
      if (frame.querySelector(".diagram-zoom-trigger")) return;
      const button = document.createElement("button");
      button.className = "diagram-zoom-trigger";
      button.type = "button";
      button.title = "Enlarge";
      button.setAttribute("aria-label", "Enlarge diagram");
      button.appendChild(lucideIcon("maximize2"));
      button.addEventListener("click", () => openLightbox(frame));
      frame.appendChild(button);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    setupToc();
    setupMermaid();
    setupDiagramZoom();
    setupCharts();
  });
})();
