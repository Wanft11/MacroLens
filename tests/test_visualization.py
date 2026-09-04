import pandas as pd

from src.visualization import quantile_encode


def test_quantile_encoding_preserves_shape_and_bin_range():
    matrix = pd.DataFrame(
        [[-0.05, 0.00, 0.02], [0.03, 0.05, 0.10]],
        index=["A", "B"],
        columns=["Q1", "Q2", "Q3"],
    )
    encoding = quantile_encode(matrix, quantiles=3)
    assert encoding.bins.shape == matrix.shape
    assert encoding.bins.min().min() >= 0
    assert encoding.bins.max().max() <= 2
    assert len(encoding.labels) == 3
