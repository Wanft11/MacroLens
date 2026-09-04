# 数据来源与口径说明

## 1. 数据范围

MacroLens 使用原项目保存的 **2013 Q1–2023 Q4** 历史数据快照。Dashboard 主要展示 YoY / QoQ 增长率，其中 YoY 需要与四个季度前的数据比较，因此第一组完整同比结果从 **2014 Q1** 开始。

例如：

```text
2014 Q1 YoY = 2014 Q1 / 2013 Q1 - 1
```

因此，2013 年数据并没有被删除，而是作为计算 2014 年同比增长率的基期。

---

## 2. 官方数据来源

以下来源均来自原项目保存的数据来源记录。

| 市场 | Dashboard 指标 | 原始来源 | Series / 数据表 |
|---|---|---|---|
| 美国 | GDP | Federal Reserve Economic Data (FRED) | Real Gross Domestic Product — `GDPC1` |
| 美国 | 零售销售 | FRED | Retail Sales: Retail Trade — `MRTSSM44000USS` |
| 美国 | 工业生产 | FRED | Industrial Production: Total Index — `INDPRO` |
| 英国 | GDP | Office for National Statistics (ONS) | Gross Domestic Product: chained volume measures: Seasonally adjusted £m — `ABMI` |
| 英国 | 零售销售 | ONS | Retail Sales Index reference tables |
| 英国 | 工业生产 | ONS | Index of Production time series |
| 中国 | GDP | 国家统计局 | Gross Domestic Product, Current Quarter (100 million yuan) |
| 中国 | 零售销售 | 国家统计局 | Total Retail Sales of Consumer Goods, Current Period (100 million yuan) |
| 中国 | 工业生产 | 国家统计局 | Value-added of Industry, Current Quarter (100 million yuan) |

原始官方链接保存在仓库的 `reports/original-data-source-links.pdf` 中，便于追溯原项目的数据出处。

---

## 3. 为什么不把三国 GDP 都称为 “Real GDP”

三个市场的 GDP 原始来源名称并不完全一致：

- 美国：明确为 **Real Gross Domestic Product**；
- 英国：使用 **chained volume measures**；
- 中国：原始来源记录为 **Gross Domestic Product, Current Quarter (100 million yuan)**。

因此，作品集统一使用更保守的 **GDP / GDP 相关指标** 表述，而不声称三国使用完全相同定义的 Real GDP。

原始文件中的历史命名（例如 `China_Real GDP_2013Q1-2023Q4.csv`）属于原作业时期的文件命名，为保持历史可追溯性保留，不应被理解为对官方统计定义的重新命名。

---

## 4. Dashboard 中的转换逻辑

项目以已经整理为季度粒度的历史数据快照为输入，并计算：

```text
季度原始值
    ↓
按季度排序
    ↓
YoY = 当前季度 / 四个季度前 - 1
QoQ = 当前季度 / 上一季度 - 1
    ↓
按 Time Period 合并三类指标
    ↓
合并美国、英国、中国
    ↓
交互式 Dashboard
```

因此，Dashboard 主要比较的是**增长率变化与相对经济动能**，而不是三个国家的绝对经济规模。

---

## 5. 当前项目的口径边界

原始来源记录能够确认数据来自 FRED、ONS 与中国国家统计局，但没有完整保存当时所有中间处理细节，例如部分月度序列如何聚合为季度、具体季调选择、下载时间与版本等。

因此，本作品集不会声称：

- 三国所有指标的统计定义完全一致；
- 当前 raw CSV 由代码实时从官方 API 自动生成；
- 所有历史中间清洗步骤已经重新审计；
- 当前数据可以直接作为实时投资决策数据源。

更准确的项目定位是：

> **基于官方来源历史数据快照构建的跨市场宏观经济增长率可视化与 AI 协作开发案例。**

---

## 6. 如果扩展为 Production Data Pipeline

如果未来将项目做成持续更新的数据产品，我会优先补充：

1. 从 FRED / ONS / 国家统计局重新建立自动数据获取流程；
2. 为每个指标固定 series ID / table ID / query 配置；
3. 显式记录 frequency、unit、seasonal adjustment 和季度聚合方法；
4. 增加 missing value、schema、单位和时间范围校验；
5. 保存每次数据拉取时间与版本；
6. 在产品界面中直接标注跨国统计口径差异。
