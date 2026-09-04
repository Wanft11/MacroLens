from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import plotly.graph_objects as go

DEFAULT_COLORS = ["#B42318", "#F97066", "#F2F4F7", "#84CAFF", "#175CD3"]


@dataclass(frozen=True)
class QuantileEncoding:
    bins: pd.DataFrame
    edges: np.ndarray
    labels: list[str]
    colors: list[str]


def _format_range(low: float, high: float) -> str:
    return f"{low:.1%} – {high:.1%}"


def quantile_encode(values: pd.DataFrame, quantiles: int) -> QuantileEncoding:
    """Map original values to quantile-bin indices while retaining original values for display.

    The key separation is intentional:
    - bin indices control cell color;
    - original values remain available for text and hover.
    """
    if quantiles not in {3, 5}:
        raise ValueError("quantiles must be either 3 or 5")

    arr = values.to_numpy(dtype=float)
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        raise ValueError("No numeric values are available for the selected view.")

    edges = np.quantile(valid, np.linspace(0, 1, quantiles + 1))

    # Quantile edges can coincide when many observations are tied. A tiny monotonic
    # adjustment keeps the bin definition valid without changing displayed values.
    edges = edges.astype(float)
    for i in range(1, len(edges)):
        if edges[i] <= edges[i - 1]:
            edges[i] = np.nextafter(edges[i - 1], np.inf)

    encoded = np.full(arr.shape, np.nan, dtype=float)
    mask = np.isfinite(arr)
    # np.digitize against internal boundaries gives integer bins 0..q-1.
    encoded[mask] = np.digitize(arr[mask], edges[1:-1], right=True)

    bins = pd.DataFrame(encoded, index=values.index, columns=values.columns)
    labels = [_format_range(edges[i], edges[i + 1]) for i in range(quantiles)]

    if quantiles == 3:
        colors = [DEFAULT_COLORS[0], DEFAULT_COLORS[2], DEFAULT_COLORS[4]]
    else:
        colors = DEFAULT_COLORS.copy()

    return QuantileEncoding(bins=bins, edges=edges, labels=labels, colors=colors)


def discrete_colorscale(colors: Sequence[str]) -> list[list[float | str]]:
    """Build a stepwise Plotly colorscale with one exact color per bin."""
    n = len(colors)
    scale: list[list[float | str]] = []
    for i, color in enumerate(colors):
        left = i / n
        right = (i + 1) / n
        scale.append([left, color])
        scale.append([right, color])
    return scale


def make_heatmap(
    matrix: pd.DataFrame,
    quantiles: int,
    indicator_label: str,
    transformation_label: str,
) -> go.Figure:
    encoding = quantile_encode(matrix, quantiles)

    fig = go.Figure(
        data=go.Heatmap(
            x=matrix.columns.tolist(),
            y=matrix.index.tolist(),
            z=encoding.bins.to_numpy(),
            text=matrix.to_numpy(),
            customdata=matrix.to_numpy(),
            zmin=-0.5,
            zmax=quantiles - 0.5,
            colorscale=discrete_colorscale(encoding.colors),
            colorbar=dict(
                title=dict(text="增长率区间"),
                tickmode="array",
                tickvals=list(range(quantiles)),
                ticktext=encoding.labels,
                thickness=16,
                len=0.82,
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "季度：%{x}<br>"
                "增长率：%{customdata:.2%}<extra></extra>"
            ),
            texttemplate="%{text:.1%}",
            textfont=dict(size=11),
            xgap=2,
            ygap=2,
            showscale=True,
        )
    )

    # Keep approximately 90 px per quarter so longer lookbacks scroll horizontally.
    width = max(980, 260 + 90 * len(matrix.columns))
    fig.update_layout(
        title=dict(
            text=f"{indicator_label} · {transformation_label}",
            x=0.01,
            xanchor="left",
            font=dict(size=19),
        ),
        width=width,
        height=max(360, 180 + 90 * len(matrix.index)),
        margin=dict(l=80, r=60, t=70, b=70),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, PingFang SC, Microsoft YaHei, Arial, sans-serif", color="#101828"),
        xaxis=dict(
            title="季度",
            type="category",
            tickangle=0,
            fixedrange=True,
            showgrid=False,
        ),
        yaxis=dict(
            title="国家",
            type="category",
            fixedrange=True,
            autorange="reversed",
            showgrid=False,
        ),
        dragmode=False,
    )
    return fig
