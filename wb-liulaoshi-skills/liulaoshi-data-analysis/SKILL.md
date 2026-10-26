---
name: liulaoshi-data-analysis
description: 中文优先的表格数据分析技能。用户上传 Excel（.xlsx/.xls）或 CSV，想做统计、汇总、透视、筛选、多表连接、SQL 式查询，或把结果导出为 CSV/JSON/Markdown 时使用。触发词：分析数据、统计一下、做个透视表、帮我汇总、看 Top N、环比同比、多表关联。
description_zh: "中文优先的表格数据分析技能：Excel/CSV 上传后先做数据体检（行数、类型、缺失、异常），再按用户问题选择统计/透视/连接路径，输出带校验的结论与可复用的导出文件。"
description_en: "Chinese-first spreadsheet analysis skill: after receiving Excel/CSV files, run a data health check (rows, dtypes, missing values, outliers), then answer the user's question via aggregation, pivot, or join, and deliver verified conclusions plus reusable exports."
version: 1.0.0
author: 刘洪光
---

# 刘老师 · 表格数据分析

## 定位

拿到用户的表格文件，回答用户的数据问题。**结论必须算得出来、对得上账**：每个数字都能指回源数据的哪一行哪一列，算不出来的就明说。

## 第一步：数据体检（必做，先于任何分析）

用 pandas 读入后，先输出一张体检卡再动手：

| 检查项 | 怎么做 | 红旗 |
| --- | --- | --- |
| 规模 | `df.shape`、每个 sheet 的行列数 | 文件比用户描述的大/小一个量级，先确认 |
| 类型 | `df.dtypes` | 金额/日期被读成 object，必须先转 |
| 缺失 | `df.isna().sum()` 按列汇总 | 关键维度列缺失率 > 20% 时说明影响 |
| 重复 | `df.duplicated()` 计数 | 主键列有重复，问用户以哪条为准 |
| 样本 | `df.head(5)` | 列名含混、单位不明（万元还是元）直接问 |

多 sheet 工作簿：每个 sheet 都要过一遍体检，并弄清 sheet 之间的关联键。

## 第二步：把问题翻译成算式

用户的问题常常是模糊的（"帮我看看销售情况"）。先把它落成一个可计算的句式，向用户确认一次再跑：

- "销售情况" → 「按 [月份] 汇总 [销售额]，按 [产品线] 拆分，给出环比」
- "哪个渠道好" → 「按 [渠道] 分组，比较 [转化率] 与 [客单价]，排序取前 5」

确认成本只有一句话，算错方向重来的成本是整个分析。

## 第三步：选对工具路径

- **常规统计/透视/连接**：pandas（`groupby` / `pivot_table` / `merge`）
- **超大文件**（>500MB）：分块读 `chunksize`，或只读需要的列 `usecols`
- **用户明确要 SQL**：可以直接给 SQL 文本（SQLite 方言），并用 pandas `read_sql` 验证结果一致
- **多表连接**：先验证连接键唯一性和匹配率（`validate="m:1"` 等参数），匹配率低于 90% 时报告再继续

## 第四步：交付规范

1. **结论先行**：第一段直接回答用户的问题，不超过 3 句
2. **数字带口径**：「Q3 销售额 1,240 万（订单表 `amount` 字段求和，含退款前）」
3. **异常单列**：缺失、剔除的行、无法解释的跳动，写明处理方式
4. **导出物**：默认输出一份结果 CSV + 一段可复跑的 Python 片段；用户要报表时才做透视表样式的 Excel
5. **诚实边界**：数据无法支持的判断（因果、预测）明确说"这份数据推不出"

## 常见坑（内部清单，按需取用）

- 中文 CSV 编码：优先 `utf-8-sig`，乱码再试 `gbk`/`gb18030`
- Excel 日期序列数（如 45000+）要用 `pd.to_datetime(..., unit="D", origin="1899-12-30")` 转
- 合并单元格读入后只有左上角有值：先 `ffill()` 补齐再分组
- 环比/同比要写明对照窗口，环比跳变先查是否有促销/换算单位变化，再当业务现象报告
- 金额列做 `round(2)` 之前不要提前四舍五入，汇总完再格式化
