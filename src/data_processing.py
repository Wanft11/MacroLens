from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

PROJECT_ROOT: Final = Path(__file__).resolve().parents[1]
RAW_DATA_DIR: Final = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_PATH: Final = PROJECT_ROOT / "data" / "processed" / "economic_growth.csv"

COUNTRIES: Final = {
    "United States": "US",
    "United Kingdom": "UK",
    "China": "China",
}

INDICATORS: Final = {
    "IP": "Industrial Production",
    "RG": "Real GDP",
    "RS": "Retail Sales",
}


def quarter_to_timestamp(series: pd.Series) -> pd.Series:
    """Convert strings such as '2023 Q4' to quarter-start timestamps."""
    cleaned = series.astype(str).str.strip().str.replace(" ", "", regex=False)
    periods = pd.PeriodIndex(cleaned, freq="Q")
    return periods.to_timestamp(how="start")


def transform_indicator(path: Path, short_name: str, full_name: str) -> pd.DataFrame:
    """Load one raw quarterly series and calculate YoY and QoQ growth rates."""
    df = pd.read_csv(path)
    required = {"Time Period", full_name}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")

    df = df[["Time Period", full_name]].copy()
    df["Time Period"] = quarter_to_timestamp(df["Time Period"])
    df = df.sort_values("Time Period").reset_index(drop=True)

    values = pd.to_numeric(df[full_name], errors="coerce")
    if values.isna().any():
        raise ValueError(f"{path.name} contains non-numeric values in {full_name!r}")

    df[f"{short_name} Year-on-Year"] = values.pct_change(4)
    df[f"{short_name} Quarter-on-Quarter"] = values.pct_change(1)

    return df.drop(columns=[full_name])


def build_country_dataset(country_name: str, file_prefix: str) -> pd.DataFrame:
    """Merge all indicator transformations for one country."""
    frames: list[pd.DataFrame] = []
    for short_name, full_name in INDICATORS.items():
        path = RAW_DATA_DIR / f"{file_prefix}_{full_name}_2013Q1-2023Q4.csv"
        frames.append(transform_indicator(path, short_name, full_name))

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="Time Period", how="inner", validate="one_to_one")

    # YoY requires four prior quarters; use a shared clean period across indicators.
    yoy_columns = [f"{short} Year-on-Year" for short in INDICATORS]
    merged = merged.dropna(subset=yoy_columns).reset_index(drop=True)
    merged["Country"] = country_name
    return merged


def build_combined_dataset(save: bool = False) -> pd.DataFrame:
    """Build the three-country dataset used by the dashboard."""
    frames = [
        build_country_dataset(country_name, prefix)
        for country_name, prefix in COUNTRIES.items()
    ]
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["Country", "Time Period"]).reset_index(drop=True)

    if save:
        PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(PROCESSED_DATA_PATH, index=False)

    return combined


def load_dashboard_data() -> pd.DataFrame:
    """Load the cached processed dataset, or build it from raw files if needed."""
    if PROCESSED_DATA_PATH.exists():
        df = pd.read_csv(PROCESSED_DATA_PATH, parse_dates=["Time Period"])
        return df
    return build_combined_dataset(save=True)


if __name__ == "__main__":
    df = build_combined_dataset(save=True)
    print(
        f"Saved {len(df)} rows to {PROCESSED_DATA_PATH.relative_to(PROJECT_ROOT)} "
        f"({df['Time Period'].min().date()} to {df['Time Period'].max().date()})."
    )
