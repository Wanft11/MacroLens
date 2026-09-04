"""Historical forecasting extension from the original 2024 assignment.

This script is intentionally separated from the dashboard because the dataset has only
~40 usable quarterly observations per country. The Random Forest exercise is kept as an
exploratory prototype, not presented as a production-grade forecasting model.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "economic_growth.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "legacy_forecast_2025_output.csv"


def forecast_country(df: pd.DataFrame, country: str) -> pd.DataFrame:
    series = (
        df.loc[df["Country"].eq(country), ["Time Period", "RG Year-on-Year"]]
        .sort_values("Time Period")
        .set_index("Time Period")
    )
    series["Quarter"] = series.index.quarter
    series["Year"] = series.index.year
    series["Lag_1"] = series["RG Year-on-Year"].shift(1)
    series["Lag_2"] = series["RG Year-on-Year"].shift(2)
    model_data = series.dropna()

    features = ["Year", "Quarter", "Lag_1", "Lag_2"]
    model = RandomForestRegressor(n_estimators=300, random_state=42)
    model.fit(model_data[features], model_data["RG Year-on-Year"])

    # Recreate the original assignment's 2024-2025 iterative forecast horizon.
    last_value = float(series["RG Year-on-Year"].iloc[-1])
    lag_2 = float(series["RG Year-on-Year"].iloc[-2])
    rows = []
    for period in pd.period_range("2024Q1", "2025Q4", freq="Q"):
        x_future = pd.DataFrame(
            {
                "Year": [period.year],
                "Quarter": [period.quarter],
                "Lag_1": [last_value],
                "Lag_2": [lag_2],
            }
        )
        prediction = float(model.predict(x_future)[0])
        rows.append({"Country": country, "Quarter": str(period), "Forecast": prediction})
        lag_2, last_value = last_value, prediction
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Time Period"])
    countries = ["United States", "United Kingdom", "China"]
    result = pd.concat([forecast_country(df, country) for country in countries], ignore_index=True)
    result.to_csv(OUTPUT_PATH, index=False)
    print(result.to_string(index=False, formatters={"Forecast": "{:.2%}".format}))
    print(f"\nSaved: {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
