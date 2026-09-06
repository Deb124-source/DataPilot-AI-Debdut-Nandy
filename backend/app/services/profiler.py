import numpy as np
import pandas as pd


def _safe_value(value):

    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating, float)):
        if np.isnan(value) or np.isinf(value):
            return None

        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    return value


def generate_profile(df):

    column_info = {}

    for column in df.columns:

        series = df[column]

        info = {
            "dtype": str(series.dtype),
            "missing_values": int(series.isna().sum()),
            "unique_values": int(
                series.nunique(dropna=True)
            ),
        }

        if pd.api.types.is_numeric_dtype(series):

            info["min"] = _safe_value(
                series.min()
            )

            info["max"] = _safe_value(
                series.max()
            )

            info["mean"] = _safe_value(
                series.mean()
            )

            info["median"] = _safe_value(
                series.median()
            )

        else:

            top_values = (
                series
                .dropna()
                .astype(str)
                .value_counts()
                .head(5)
            )

            info["top_values"] = {
                str(key): int(value)
                for key, value in top_values.items()
            }

        column_info[str(column)] = info

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(
            df.isna().sum().sum()
        ),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "column_info": column_info,
    }
