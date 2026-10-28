#!/usr/bin/env python3
"""向已有 PPT 的指定页添加原生图表（python-pptx 原生图表，可在 PowerPoint/WPS 中继续编辑）。

用法:
  python3 pptx_add_chart.py 输入.pptx --slide 5 --type bar --title "完课学员转化漏斗（%）" \
    --categories "实名认证,提交技能,通过审核,付费配置" --series "转化率=58,34,21,9" -o 输出.pptx
  多系列: --series "华东=10,20,30" --series "华北=5,15,25"
样式纪律: 单强调色、显示数值标签、网格线静音、单系列不显示图例。
"""
import argparse

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.util import Inches, Pt

from lls_pptx_utils import CN_FONT, die, ensure_parent, guard_overwrite

ACCENT = RGBColor(0x1F, 0x46, 0x9C)
TYPES = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED, "line": XL_CHART_TYPE.LINE_MARKERS, "pie": XL_CHART_TYPE.PIE}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--slide", type=int, required=True)
    ap.add_argument("--type", choices=list(TYPES), default="bar")
    ap.add_argument("--title", required=True)
    ap.add_argument("--categories", required=True, help="逗号分隔")
    ap.add_argument("--series", action="append", required=True, help="名称=v1,v2,... 可多次")
    ap.add_argument("--x", type=float, default=0.75)
    ap.add_argument("--y", type=float, default=1.7)
    ap.add_argument("--w", type=float, default=11.8)
    ap.add_argument("--h", type=float, default=4.4)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    prs = Presentation(args.input)
    if not (1 <= args.slide <= len(prs.slides)):
        die(f"页码越界: {args.slide}（共 {len(prs.slides)} 页）")

    data = CategoryChartData()
    data.categories = [c.strip() for c in args.categories.split(",")]
    for spec in args.series:
        name, _, values = spec.partition("=")
        data.add_series(name.strip(), [float(v) for v in values.split(",")])

    chart = prs.slides[args.slide - 1].shapes.add_chart(
        TYPES[args.type], Inches(args.x), Inches(args.y), Inches(args.w), Inches(args.h), data).chart
    chart.has_title = True
    chart.chart_title.text_frame.text = args.title
    for run in chart.chart_title.text_frame.paragraphs[0].runs:
        run.font.name = CN_FONT
        run.font.size = Pt(14)
    chart.has_legend = len(args.series) > 1
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False

    plot = chart.plots[0]
    plot.has_data_labels = True
    try:
        plot.data_labels.font.size = Pt(11)
        if args.type != "pie":
            plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    except Exception:  # pie 等类型不支持 OUTSIDE_END 时保持默认
        pass
    if args.type == "bar":
        plot.gap_width = 60
        plot.series[0].format.fill.solid()
        plot.series[0].format.fill.fore_color.rgb = ACCENT

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    prs.save(out)
    print(f"[lls-pptx] 已在第 {args.slide} 页添加{args.type}图表（{len(args.series)} 系列）→ {out}")
    print("[lls-pptx] 图表为原生对象，可在 PowerPoint/WPS 中继续编辑数据")


if __name__ == "__main__":
    main()
