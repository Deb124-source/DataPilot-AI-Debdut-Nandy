from pathlib import Path
import uuid
import numpy as np

from app.config import CLEANED_DIR
from app.services.data_loader import load_dataset, save_dataset
from app.services.dataset_manager import (
    get_dataset,
    register_dataset,
    set_active_dataset,
)


def dataset_stats(df):
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def get_cleaning_suggestions(dataset_id: str):
    dataset = get_dataset(dataset_id)

    if not dataset:
        raise ValueError("Dataset not found")

    df = load_dataset(dataset["file_path"])
    suggestions = []

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        if missing_count > 0:
            percentage = round(
                missing_count / max(len(df), 1) * 100,
                2,
            )

            if np.issubdtype(df[column].dtype, np.number):
                action = "median"
            else:
                action = "mode"

            suggestions.append({
                "issue": "missing_values",
                "column": str(column),
                "missing_count": missing_count,
                "missing_percentage": percentage,
                "recommended_action": action,
            })

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count > 0:
        suggestions.append({
            "issue": "duplicate_rows",
            "duplicate_count": duplicate_count,
            "recommended_action": "remove_duplicates",
        })

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:
        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = int(
            ((series < lower) | (series > upper)).sum()
        )

        if count > 0:
            suggestions.append({
                "issue": "potential_outliers",
                "column": str(column),
                "outlier_count": count,
                "recommended_action": "cap_iqr",
            })

    return suggestions


def apply_operations(dataset_id: str, operations: list):
    dataset = get_dataset(dataset_id)

    if not dataset:
        raise ValueError("Dataset not found")

    df = load_dataset(dataset["file_path"])
    before = dataset_stats(df)

    for operation in operations:
        operation_type = operation.get("type")

        if operation_type == "fill_missing":
            column = operation.get("column")
            strategy = operation.get("strategy", "median")

            if column not in df.columns:
                continue

            if strategy == "mean":
                value = df[column].mean()

            elif strategy == "mode":
                mode = df[column].mode(dropna=True)
                value = mode.iloc[0] if not mode.empty else "Unknown"

            else:
                value = df[column].median()

            df[column] = df[column].fillna(value)

        elif operation_type == "remove_duplicates":
            df = df.drop_duplicates()

        elif operation_type == "cap_outliers":
            column = operation.get("column")

            if column not in df.columns:
                continue

            series = df[column]

            if not np.issubdtype(series.dtype, np.number):
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            if iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            df[column] = series.clip(lower, upper)

    cleaned_id = (
        f"cleaned_{uuid.uuid4().hex[:12]}.csv"
    )

    cleaned_path = CLEANED_DIR / cleaned_id
    save_dataset(df, str(cleaned_path))

    register_dataset(
        dataset_id=cleaned_id,
        filename=cleaned_id,
        file_path=str(cleaned_path),
        dataset_type="cleaned",
        parent_dataset=dataset_id,
    )

    set_active_dataset(cleaned_id)

    after = dataset_stats(df)

    return {
        "cleaned_dataset_id": cleaned_id,
        "before": before,
        "after": after,
    }


def apply_recommended_cleaning(dataset_id: str):
    suggestions = get_cleaning_suggestions(dataset_id)
    operations = []

    for suggestion in suggestions:
        if suggestion["issue"] == "missing_values":
            operations.append({
                "type": "fill_missing",
                "column": suggestion["column"],
                "strategy": suggestion["recommended_action"],
            })

        elif suggestion["issue"] == "duplicate_rows":
            operations.append({
                "type": "remove_duplicates",
            })

        elif suggestion["issue"] == "potential_outliers":
            operations.append({
                "type": "cap_outliers",
                "column": suggestion["column"],
            })

    return apply_operations(dataset_id, operations)
