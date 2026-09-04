import pandas as pd

from src.data_processing import build_combined_dataset, quarter_to_timestamp


def test_quarter_to_timestamp():
    result = quarter_to_timestamp(pd.Series(["2023 Q1", "2023 Q4"]))
    assert result[0] == pd.Timestamp("2023-01-01")
    assert result[1] == pd.Timestamp("2023-10-01")


def test_combined_dataset_shape_and_window():
    df = build_combined_dataset(save=False)
    assert len(df) == 120
    assert df["Country"].nunique() == 3
    assert df["Time Period"].min() == pd.Timestamp("2014-01-01")
    assert df["Time Period"].max() == pd.Timestamp("2023-10-01")
