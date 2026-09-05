import numpy as np
from app.services.data_loader import load_dataset
from app.services.dataset_manager import get_dataset


def _safe_number(value):
    if value is None:
        return None

    if isinstance(value, (np.integer, int)):
        return int(value)

    if isinstance(value, (np.floating, float)):
        if np.isnan(value) or np.isinf(value):
            return None
        return round(float(value), 4)

    return value


def generate_eda(dataset_id: str):
    dataset = get_dataset(dataset_id)

    if not dataset:
        raise ValueError("Dataset not found")

    df = load_dataset(dataset["file_path"])

    missing_by_column = {
        str(column): int(df[column].isna().sum())
        for column in df.columns
    }

    numeric_summary = {}

    numeric_df = df.select_dtypes(include=np.number)

    for column in numeric_df.columns:
        series = numeric_df[column].dropna()

        if len(series) == 0:
            continue

        numeric_summary[str(column)] = {
            "min": _safe_number(series.min()),
            "mean": _safe_number(series.mean()),
            "median": _safe_number(series.median()),
            "max": _safe_number(series.max()),
            "std": _safe_number(series.std()),
        }

    categorical_summary = {}

    categorical_columns = df.select_dtypes(
        exclude=np.number
    ).columns

    for column in categorical_columns:
        counts = (
            df[column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )

        categorical_summary[str(column)] = {
            str(key): int(value)
            for key, value in counts.items()
        }

    correlations = {}

    if numeric_df.shape[1] >= 2:
        corr = numeric_df.corr()

        correlations = {
            str(row): {
                str(column): _safe_number(value)
                for column, value in corr.loc[row].items()
            }
            for row in corr.index
        }

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_by_column": missing_by_column,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "correlations": correlations,
    }
