from __future__ import annotations

import pandas as pd
from dash import Dash, Input, Output, dash_table, dcc, html

from src.data_processing import INDICATORS, load_dashboard_data
from src.visualization import make_heatmap

DATA = load_dashboard_data()

DISPLAY_INDICATORS = {
    "IP": "工业生产",
    "RG": "GDP",
    "RS": "零售销售",
}
TRANSFORMATION_LABELS = {
    "Year-on-Year": "同比（YoY）",
    "Quarter-on-Quarter": "环比（QoQ）",
}

INDICATOR_OPTIONS = [
    {"label": DISPLAY_INDICATORS[short_name], "value": short_name}
    for short_name in INDICATORS
]
TRANSFORMATION_OPTIONS = [
    {"label": "同比（YoY）", "value": "Year-on-Year"},
    {"label": "环比（QoQ）", "value": "Quarter-on-Quarter"},
]
COUNTRY_LABELS = {
    "United States": "美国",
    "United Kingdom": "英国",
    "China": "中国",
}
COUNTRY_OPTIONS = [
    {"label": label, "value": value}
    for value, label in COUNTRY_LABELS.items()
]
PERIOD_OPTIONS = [
    {"label": date.strftime("%Y Q") + str(date.quarter), "value": date.strftime("%Y-%m-%d")}
    for date in sorted(DATA["Time Period"].drop_duplicates())
]

app = Dash(__name__, title="MacroLens")
server = app.server


def control(label: str, component) -> html.Div:
    return html.Div(
        [html.Label(label, className="control-label"), component],
        className="control-block",
    )


app.layout = html.Div(
    [
        html.Header(
            [
                html.Div(
                    [
                        html.Div("MACROLENS", className="eyebrow"),
                        html.H1("全球宏观经济动能 Dashboard"),
                        html.P(
                            "比较美国、英国和中国的 GDP、零售销售与工业生产增长动能。",
                            className="subtitle",
                        ),
                    ],
                    className="header-copy",
                ),
                html.Div(
                    [
                        html.Span("2014–2023", className="metric-value"),
                        html.Span("季度视图", className="metric-label"),
                    ],
                    className="header-metric",
                ),
            ],
            className="hero",
        ),
        html.Main(
            [
                html.Section(
                    [
                        html.Div(
                            [
                                html.H2("探索数据"),
                                html.P(
                                    "颜色表示当前视图中的相对分位区间；单元格文字保留原始增长率。",
                                    className="section-note",
                                ),
                            ],
                            className="section-heading",
                        ),
                        html.Div(
                            [
                                control(
                                    "国家",
                                    dcc.Dropdown(
                                        id="country-dropdown",
                                        options=COUNTRY_OPTIONS,
                                        value=["United States", "United Kingdom", "China"],
                                        multi=True,
                                        clearable=False,
                                    ),
                                ),
                                control(
                                    "指标",
                                    dcc.Dropdown(
                                        id="indicator-dropdown",
                                        options=INDICATOR_OPTIONS,
                                        value="RG",
                                        clearable=False,
                                    ),
                                ),
                                control(
                                    "增长率口径",
                                    dcc.Dropdown(
                                        id="transformation-dropdown",
                                        options=TRANSFORMATION_OPTIONS,
                                        value="Year-on-Year",
                                        clearable=False,
                                    ),
                                ),
                                control(
                                    "结束季度",
                                    dcc.Dropdown(
                                        id="end-period-dropdown",
                                        options=PERIOD_OPTIONS,
                                        value=PERIOD_OPTIONS[-1]["value"],
                                        clearable=False,
                                    ),
                                ),
                                control(
                                    "回溯季度",
                                    dcc.Dropdown(
                                        id="lookback-dropdown",
                                        options=[
                                            {"label": label, "value": value}
                                            for label, value in [
                                                ("4 个季度", 4),
                                                ("8 个季度", 8),
                                                ("12 个季度", 12),
                                                ("20 个季度", 20),
                                                ("全部可用季度", 40),
                                            ]
                                        ],
                                        value=12,
                                        clearable=False,
                                    ),
                                ),
                                control(
                                    "分位区间",
                                    dcc.Dropdown(
                                        id="quantiles-dropdown",
                                        options=[
                                            {"label": "3 个区间", "value": 3},
                                            {"label": "5 个区间", "value": 5},
                                        ],
                                        value=5,
                                        clearable=False,
                                    ),
                                ),
                            ],
                            className="control-grid",
                        ),
                    ],
                    className="card controls-card",
                ),
                html.Section(
                    [
                        html.Div(id="view-summary", className="view-summary"),
                        html.Div(
                            dcc.Graph(
                                id="heatmap-graph",
                                config={"displayModeBar": False, "responsive": False},
                            ),
                            className="heatmap-scroll",
                        ),
                    ],
                    className="card chart-card",
                ),
                html.Section(
                    [
                        html.Div(
                            [
                                html.H2("底层观测数据"),
                                html.P(
                                    "下表与 Heatmap 使用完全相同的筛选条件。",
                                    className="section-note",
                                ),
                            ],
                            className="section-heading",
                        ),
                        dash_table.DataTable(
                            id="data-table",
                            columns=[
                                {"name": "国家", "id": "Country"},
                                {"name": "季度", "id": "Quarter"},
                                {"name": "增长率", "id": "Growth"},
                            ],
                            page_size=15,
                            sort_action="native",
                            style_as_list_view=True,
                            style_cell={
                                "padding": "12px 16px",
                                "fontFamily": "Inter, Arial, sans-serif",
                                "fontSize": "14px",
                                "textAlign": "left",
                                "border": "none",
                            },
                            style_header={
                                "fontWeight": 600,
                                "backgroundColor": "#F9FAFB",
                                "borderBottom": "1px solid #EAECF0",
                            },
                        ),
                    ],
                    className="card table-card",
                ),
                html.Footer(
                    "使用 Python、Pandas、Dash 与 Plotly 构建 · 数据来源：FRED、ONS、中国国家统计局 · AI 辅助开发，需求定义与结果验证由人完成。",
                    className="footer",
                ),
            ],
            className="content",
        ),
    ],
    className="page-shell",
)


@app.callback(
    Output("heatmap-graph", "figure"),
    Output("data-table", "data"),
    Output("view-summary", "children"),
    Input("country-dropdown", "value"),
    Input("indicator-dropdown", "value"),
    Input("transformation-dropdown", "value"),
    Input("end-period-dropdown", "value"),
    Input("lookback-dropdown", "value"),
    Input("quantiles-dropdown", "value"),
)
def update_view(
    selected_countries: list[str],
    indicator: str,
    transformation: str,
    end_period: str,
    lookback: int,
    quantiles: int,
):
    selected_countries = selected_countries or ["United States"]
    column = f"{indicator} {transformation}"
    end = pd.Timestamp(end_period)
    start = end - pd.DateOffset(months=3 * (int(lookback) - 1))

    filtered = DATA[
        DATA["Country"].isin(selected_countries)
        & DATA["Time Period"].between(start, end)
    ][["Country", "Time Period", column]].copy()
    filtered = filtered.rename(columns={column: "Growth"})

    # Pivot only after filtering, so the visual matrix stays aligned to the selected view.
    matrix = filtered.pivot(index="Country", columns="Time Period", values="Growth")
    country_order = [c for c in ["United States", "United Kingdom", "China"] if c in matrix.index]
    matrix = matrix.reindex(country_order)
    matrix.index = [COUNTRY_LABELS.get(c, c) for c in matrix.index]
    matrix.columns = [pd.Timestamp(c).strftime("%Y Q") + str(pd.Timestamp(c).quarter) for c in matrix.columns]

    fig = make_heatmap(
        matrix,
        quantiles=quantiles,
        indicator_label=DISPLAY_INDICATORS[indicator],
        transformation_label=TRANSFORMATION_LABELS[transformation],
    )

    table = filtered.sort_values(["Time Period", "Country"], ascending=[False, True]).copy()
    table["Quarter"] = table["Time Period"].dt.to_period("Q").astype(str)
    table["Growth"] = table["Growth"].map(lambda x: f"{x:.2%}")
    table["Country"] = table["Country"].map(COUNTRY_LABELS).fillna(table["Country"])
    table = table[["Country", "Quarter", "Growth"]]

    min_date = filtered["Time Period"].min().to_period("Q")
    max_date = filtered["Time Period"].max().to_period("Q")
    summary = [
        html.Span(f"{len(selected_countries)} 个市场", className="pill"),
        html.Span(f"{min_date} → {max_date}", className="pill"),
        html.Span(f"{quantiles} 个分位区间", className="pill"),
    ]
    return fig, table.to_dict("records"), summary


if __name__ == "__main__":
    app.run(debug=True)
