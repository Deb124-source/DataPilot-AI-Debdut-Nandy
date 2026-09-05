import json
import numpy as np
import pandas as pd

from app.services.dataset_manager import get_dataset
from app.services.data_loader import load_dataset


def safe_value(value):
    """Convert NumPy/Pandas values into JSON-safe Python values."""

    if value is None:
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating, float)):
        if np.isnan(value) or np.isinf(value):
            return None
        return round(float(value), 4)

    if isinstance(value, (pd.Timestamp,)):
        return str(value)

    return value


def build_dataset_context(dataset_id: str):
    """
    Build a compact but informative representation
    of the dataset for the AI model.
    """

    dataset = get_dataset(dataset_id)

    if not dataset:
        raise ValueError("Dataset not found")

    df = load_dataset(dataset["file_path"])

    context = {
        "dataset_name": dataset["filename"],
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": [str(column) for column in df.columns],
        "data_types": {
            str(column): str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            str(column): int(df[column].isna().sum())
            for column in df.columns
        },
        "duplicate_rows": int(df.duplicated().sum()),
    }

    # Numeric column statistics
    numeric_df = df.select_dtypes(include=np.number)

    numeric_statistics = {}

    for column in numeric_df.columns:
        series = numeric_df[column].dropna()

        if len(series) == 0:
            continue

        numeric_statistics[str(column)] = {
            "count": int(series.count()),
            "min": safe_value(series.min()),
            "max": safe_value(series.max()),
            "mean": safe_value(series.mean()),
            "median": safe_value(series.median()),
            "std": safe_value(series.std()),
        }

    context["numeric_statistics"] = numeric_statistics

    # Categorical information
    categorical_df = df.select_dtypes(exclude=np.number)

    categorical_statistics = {}

    for column in categorical_df.columns:
        values = (
            df[column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )

        categorical_statistics[str(column)] = {
            str(key): int(value)
            for key, value in values.items()
        }

    context["top_categorical_values"] = (
        categorical_statistics
    )

    # Correlations
    correlations = {}

    if numeric_df.shape[1] >= 2:
        correlation_matrix = numeric_df.corr()

        for column in correlation_matrix.columns:
            column_correlations = {}

            for other_column, value in (
                correlation_matrix[column].items()
            ):
                if column != other_column:
                    column_correlations[
                        str(other_column)
                    ] = safe_value(value)

            correlations[str(column)] = (
                column_correlations
            )

    context["correlations"] = correlations

    # Small sample of dataset
    sample = (
        df.head(5)
        .where(df.notna(), None)
        .to_dict(orient="records")
    )

    cleaned_sample = []

    for row in sample:
        cleaned_row = {
            str(key): safe_value(value)
            for key, value in row.items()
        }

        cleaned_sample.append(cleaned_row)

    context["sample_rows"] = cleaned_sample

    return context


def context_to_text(dataset_id: str):
    """
    Convert dataset context into formatted JSON text
    suitable for sending to the AI model.
    """

    context = build_dataset_context(dataset_id)

    return json.dumps(
        context,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
