# AI 协作案例说明

## 1. 我如何使用 AI

MacroLens 最初来自一个跨市场宏观经济 Dashboard 任务。在开发过程中，我没有把 ChatGPT 当作“一次性生成项目”的工具，而是把它作为 **coding、debugging 与 solution exploration copilot**：我负责定义需求、判断结果是否正确、提出新的约束并决定最终方案；AI 主要用于快速生成实现思路、解释报错、比较不同 API / 可视化方案。

回看整个过程，我认为最能概括这次协作的不是“用了多少 Prompt”，而是下面这条循环：

> **Define → Prompt → Validate → Diagnose → Iterate → Deliver**  
> 定义问题 → 让 AI 提供候选方案 → 实际运行验证 → 定位偏差 → 继续迭代 → 完成交付

关键点在于：**AI 输出能够运行，不代表它已经满足需求。**

---

## 2. 案例一：Heatmap 的“展示值”与“颜色编码”不是一回事

### 我的需求

我希望 heatmap 同时表达两层信息：

1. 每个格子直接显示真实的经济增长率；
2. 颜色不按照原始数值连续变化，而是按照用户选择的 quantile / bin 分组，同一区间使用同一种颜色。

换句话说，用户既要看到“这个季度具体增长了多少”，也要快速判断“它处于当前样本的哪个相对区间”。

### AI 协作中的问题

在多轮实现中，一个容易混淆的问题是 Plotly Heatmap 中不同字段的职责。如果仍然让原始值承担 `z` 的角色，Plotly 会继续根据原始数值进行颜色映射，即使已经计算了 bin，同一区间里的不同原始值仍可能出现不同深浅。

### 我如何验证

我没有只检查“图有没有成功显示”，而是回到需求本身观察：

> **属于同一个 bin 的格子，颜色是否真的完全一致？**

当结果不满足这个标准时，我继续追问并重新拆分问题，最终明确：颜色编码与展示值必须使用不同的数据通道。

### 最终逻辑

```python
z = binned_values        # 决定颜色
text = original_values   # 单元格展示真实增长率
customdata = original_values  # hover 展示真实增长率
```

这次迭代让我意识到，和 AI 协作时最重要的能力之一，是把“我觉得不对”进一步转化成**可观察、可验证的 acceptance criteria**。

---

## 3. 案例二：日期问题——从修复报错到重新定义输入方式

开发过程中，我曾遇到：

```text
TypeError: '>=' not supported between instances of 'str' and 'Timestamp'
```

表面上这是一个 Python 类型错误，但真正的问题来自 Dashboard 中日期表示方式不统一：原始 `Time Period`、用户输入以及 callback 内部比较使用了不同的数据类型。

AI 帮助我快速定位到 `str` 与 `Timestamp` 的比较问题，并探索 `pd.to_datetime()` 等处理方式。但我没有停留在“让报错消失”，而是继续调整交互设计：与其让用户自由输入日期，再不断处理非法输入和类型转换，不如把结束时间改成**季度 dropdown**，只提供数据中真正合法的季度选项。

这个过程对我很有启发：

> 有些 bug 不应该只靠增加 defensive code 解决，也可以通过重新设计用户输入，从源头减少无效状态。

AI 在这里帮助我解决技术问题，而最终“应该让用户如何选择时间”仍然是产品判断。

---

## 4. 案例三：Horizontal Scrollbar 与 Plotly Pan 的区别

随着 lookback period 增加，heatmap 会变得很宽。我希望用户能够像浏览宽表一样**横向滚动**，而不是拖动画布。

AI 协作过程中，我尝试过 Plotly axis 的 `fixedrange` 等配置，但实际运行后发现，这些设置解决的是 zoom / pan 行为，并不会产生浏览器层面的 horizontal scrollbar。

于是我重新明确需求：

> 我需要的是 **browser scroll**，不是 **chart pan**。

最终思路变成：让 figure 宽度大于外层容器，并由外层 `Div` 使用 CSS `overflow-x` 承担滚动。

这个案例让我进一步形成一个习惯：**在问 AI “怎么实现”之前，先把交互行为描述到足够具体。**“能左右移动”与“有横向滚动条”在自然语言里很接近，但在实现层面完全不是同一个需求。

---

## 5. 其他真实迭代

开发过程中还出现过一些更细的 AI 协作与验证：

| 场景 | AI 帮助 | 我的判断 / 验证 |
|---|---|---|
| `dcc.Input(type='date')` 与当前 Dash 版本不兼容 | 探索替代输入方式 | 最终改用更受约束的季度选择方式 |
| `lookback_periods` 可能为 `None` | 提供 callback 防御性处理方案 | 增加默认值并减少无效状态 |
| `px.imshow(..., text=...)` 在当前 Plotly 版本报错 | 探索其他 text API | 改为通过 trace 更新文字，并继续检查版本兼容性 |
| Quantile / equal-width binning | 比较 `np.linspace`、`np.percentile`、`pd.cut`、`np.digitize` 等方案 | 根据“颜色表达相对位置还是绝对区间”的目标选择方案 |
| Colorbar 标签 | 探索 tick API | 决定 legend 应显示用户能理解的原始增长率区间，而不是内部 bin ID |

这些经历让我逐渐从“把报错发给 AI”转向“先描述 expected behavior、actual behavior 和约束，再让 AI 协助定位”。

---

## 6. 我与 AI 的职责边界

| 环节 | 我的职责 | AI 的职责 |
|---|---|---|
| Problem framing | 明确 Dashboard 要解决的问题 | 帮助拆解可能的实现路径 |
| Data logic | 选择指标、定义 YoY / QoQ 和时间逻辑 | 提供 Pandas 实现建议 |
| Interaction | 决定用户应该如何选择国家、指标、时间窗口 | 提供 Dash callback / component 草稿 |
| Visualization | 定义“文字”和“颜色”分别表达什么 | 探索 Plotly API、binning 与 colorscale 方案 |
| Debugging | 判断实际结果是否符合需求 | 快速解释报错并提出候选修复方案 |
| Validation | 建立验收标准并实际检查输出 | 辅助分析潜在原因 |
| Final decision | 决定采用哪个方案并承担结果 | 提供方案空间，不替代最终判断 |

---

## 7. 关于数据口径的进一步反思

在整理作品集时，我重新检查了原始数据来源，也意识到“统一展示”与“统计口径完全一致”是两件不同的事。

美国 GDP 使用 FRED 的 Real GDP 系列，英国 GDP 使用 ONS chained volume measures，而中国原始来源记录为 `Gross Domestic Product, Current Quarter (100 million yuan)`。因此，我不会把这个项目表述成“完全标准化了三国 Real GDP”，而会更准确地说：

> **将不同官方来源的宏观序列整理为统一的季度增长率交互视图，用于观察跨市场经济动能。**

这也扩展了我对“验证”的理解：验证 AI 输出不仅是看代码是否报错，还包括检查数据定义是否真的支持我要表达的结论。

---

## 8. 最终收获

这次项目让我形成了三个比较稳定的 AI 协作原则：

**第一，先定义验收标准，再让 AI 生成方案。**  
如果自己都没有定义什么叫“正确”，就很难判断 AI 的输出是否真的可用。

**第二，把 AI 当作候选方案生成器，而不是答案来源。**  
它非常适合加速 API 探索、debugging 和实现比较，但最终结果仍需要实际运行和验证。

**第三，当 AI 连续给出不理想方案时，优先检查问题定义。**  
很多时候继续要求“再改一次”不如重新描述 expected behavior、actual behavior 和约束条件。

因此，我现在更倾向于把 AI 协作理解为：

> **AI 提高探索速度，我负责定义问题、验证结果，并对最终决策负责。**
