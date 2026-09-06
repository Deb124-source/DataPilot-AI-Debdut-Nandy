import numpy as np
import pandas as pd

from app.services.data_loader import load_dataset
from app.services.dataset_manager import get_dataset


MAX_CATEGORIES = 10
MAX_NUMERIC_COLUMNS = 8
MAX_SCATTER_PAIRS = 6


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


def _safe_list(values):

    result = []

    for value in values:

        safe_value = _safe_number(value)

        if safe_value is not None:
            result.append(safe_value)

    return result


def _detect_datetime_columns(df):

    datetime_columns = []

    for column in df.columns:

        series = df[column]

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(series):

            datetime_columns.append(column)
            continue

        # Only try parsing object/string columns
        if (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):

            non_null = series.dropna()

            if len(non_null) == 0:
                continue

            sample = non_null.head(100)

            try:

                parsed = pd.to_datetime(
                    sample,
                    errors="coerce"
                )

                valid_ratio = (
                    parsed.notna().sum()
                    / len(sample)
                )

                if valid_ratio >= 0.8:

                    datetime_columns.append(
                        column
                    )

            except Exception:
                pass

    return datetime_columns


def generate_eda(dataset_id: str):

    dataset = get_dataset(dataset_id)

    if not dataset:
        raise ValueError("Dataset not found")

    df = load_dataset(
        dataset["file_path"]
    )

    # -----------------------------
    # BASIC INFORMATION
    # -----------------------------

    missing_by_column = {
        str(column): int(
            df[column].isna().sum()
        )
        for column in df.columns
    }

    numeric_df = df.select_dtypes(
        include=np.number
    )

    numeric_columns = list(
        numeric_df.columns
    )

    categorical_columns = list(
        df.select_dtypes(
            exclude=np.number
        ).columns
    )

    datetime_columns = (
        _detect_datetime_columns(df)
    )

    # Remove detected datetime columns
    # from categorical analysis
    categorical_columns = [
        column
        for column in categorical_columns
        if column not in datetime_columns
    ]

    # -----------------------------
    # NUMERIC SUMMARY
    # -----------------------------

    numeric_summary = {}

    for column in numeric_columns:

        series = (
            df[column]
            .dropna()
        )

        if len(series) == 0:
            continue

        numeric_summary[str(column)] = {
            "min": _safe_number(
                series.min()
            ),

            "mean": _safe_number(
                series.mean()
            ),

            "median": _safe_number(
                series.median()
            ),

            "max": _safe_number(
                series.max()
            ),

            "std": _safe_number(
                series.std()
            ),

            "q1": _safe_number(
                series.quantile(0.25)
            ),

            "q3": _safe_number(
                series.quantile(0.75)
            ),
        }

    # -----------------------------
    # CATEGORICAL SUMMARY
    # -----------------------------

    categorical_summary = {}

    for column in categorical_columns:

        counts = (
            df[column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(MAX_CATEGORIES)
        )

        categorical_summary[
            str(column)
        ] = {
            str(key): int(value)
            for key, value
            in counts.items()
        }

    # -----------------------------
    # CORRELATION
    # -----------------------------

    correlations = {}

    if len(numeric_columns) >= 2:

        corr = (
            numeric_df[
                numeric_columns[
                    :MAX_NUMERIC_COLUMNS
                ]
            ]
            .corr()
        )

        correlations = {
            str(row): {
                str(column):
                    _safe_number(value)
                for column, value
                in corr.loc[row].items()
            }
            for row in corr.index
        }

    # -----------------------------
    # CHART GENERATION
    # -----------------------------

    charts = []

    # -----------------------------
    # HISTOGRAMS
    # -----------------------------

    for column in numeric_columns[
        :MAX_NUMERIC_COLUMNS
    ]:

        series = (
            df[column]
            .dropna()
        )

        if len(series) < 2:
            continue

        counts, bins = np.histogram(
            series,
            bins=min(10, len(series))
        )

        labels = []

        for i in range(
            len(bins) - 1
        ):

            labels.append(
                f"{round(float(bins[i]), 2)} - "
                f"{round(float(bins[i + 1]), 2)}"
            )

        charts.append(
            {
                "type": "histogram",
                "title":
                    f"Distribution of {column}",

                "column":
                    str(column),

                "labels": labels,

                "values": [
                    int(value)
                    for value
                    in counts
                ],
            }
        )

    # -----------------------------
    # BOX PLOT DATA
    # -----------------------------

    for column in numeric_columns[
        :MAX_NUMERIC_COLUMNS
    ]:

        series = (
            df[column]
            .dropna()
        )

        if len(series) < 2:
            continue

        charts.append(
            {
                "type": "box",
                "title":
                    f"Spread and Outliers: {column}",

                "column":
                    str(column),

                "min":
                    _safe_number(
                        series.min()
                    ),

                "q1":
                    _safe_number(
                        series.quantile(0.25)
                    ),

                "median":
                    _safe_number(
                        series.median()
                    ),

                "q3":
                    _safe_number(
                        series.quantile(0.75)
                    ),

                "max":
                    _safe_number(
                        series.max()
                    ),
            }
        )

    # -----------------------------
    # CATEGORICAL CHARTS
    # -----------------------------

    for column in categorical_columns:

        counts = (
            df[column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(MAX_CATEGORIES)
        )

        if len(counts) == 0:
            continue

        labels = [
            str(label)
            for label
            in counts.index.tolist()
        ]

        values = [
            int(value)
            for value
            in counts.values.tolist()
        ]

        # Small number of categories
        # → Pie chart
        if len(labels) <= 6:

            chart_type = "pie"

        else:

            chart_type = "bar"

        charts.append(
            {
                "type":
                    chart_type,

                "title":
                    f"Distribution of {column}",

                "column":
                    str(column),

                "labels":
                    labels,

                "values":
                    values,
            }
        )

    # -----------------------------
    # SCATTER PLOTS
    # -----------------------------

    scatter_count = 0

    if len(numeric_columns) >= 2:

        for i in range(
            len(numeric_columns)
        ):

            for j in range(
                i + 1,
                len(numeric_columns)
            ):

                if (
                    scatter_count
                    >= MAX_SCATTER_PAIRS
                ):
                    break

                x_column = (
                    numeric_columns[i]
                )

                y_column = (
                    numeric_columns[j]
                )

                pair_df = (
                    df[
                        [
                            x_column,
                            y_column,
                        ]
                    ]
                    .dropna()
                    .head(300)
                )

                if len(pair_df) < 2:
                    continue

                points = []

                for _, row in (
                    pair_df.iterrows()
                ):

                    points.append(
                        {
                            "x":
                                _safe_number(
                                    row[
                                        x_column
                                    ]
                                ),

                            "y":
                                _safe_number(
                                    row[
                                        y_column
                                    ]
                                ),
                        }
                    )

                charts.append(
                    {
                        "type":
                            "scatter",

                        "title":
                            f"{y_column} vs "
                            f"{x_column}",

                        "x_column":
                            str(x_column),

                        "y_column":
                            str(y_column),

                        "data":
                            points,
                    }
                )

                scatter_count += 1

            if (
                scatter_count
                >= MAX_SCATTER_PAIRS
            ):
                break

    # -----------------------------
    # TIME SERIES LINE CHARTS
    # -----------------------------

    for date_column in datetime_columns:

        try:

            temp_df = df.copy()

            temp_df[
                date_column
            ] = pd.to_datetime(
                temp_df[date_column],
                errors="coerce"
            )

            temp_df = (
                temp_df
                .dropna(
                    subset=[
                        date_column
                    ]
                )
                .sort_values(
                    by=date_column
                )
            )

            for numeric_column in numeric_columns[
                :3
            ]:

                chart_df = (
                    temp_df[
                        [
                            date_column,
                            numeric_column,
                        ]
                    ]
                    .dropna()
                    .head(200)
                )

                if len(chart_df) < 2:
                    continue

                labels = [
                    str(
                        value.date()
                    )
                    for value in chart_df[
                        date_column
                    ]
                ]

                values = [
                    _safe_number(value)
                    for value in chart_df[
                        numeric_column
                    ]
                ]

                charts.append(
                    {
                        "type":
                            "line",

                        "title":
                            f"{numeric_column} "
                            f"over time",

                        "date_column":
                            str(
                                date_column
                            ),

                        "value_column":
                            str(
                                numeric_column
                            ),

                        "labels":
                            labels,

                        "values":
                            values,
                    }
                )

        except Exception:
            pass

    # -----------------------------
    # CORRELATION HEATMAP DATA
    # -----------------------------

    heatmap = None

    if len(numeric_columns) >= 2:

        selected_columns = (
            numeric_columns[
                :MAX_NUMERIC_COLUMNS
            ]
        )

        corr = (
            df[
                selected_columns
            ]
            .corr()
        )

        heatmap = {
            "type":
                "heatmap",

            "title":
                "Correlation Heatmap",

            "labels":
                [
                    str(column)
                    for column
                    in selected_columns
                ],

            "matrix":
                [
                    [
                        _safe_number(
                            corr.loc[
                                row,
                                column
                            ]
                        )
                        for column
                        in selected_columns
                    ]
                    for row
                    in selected_columns
                ],
        }

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------

    return {
        "rows": int(df.shape[0]),

        "columns": int(df.shape[1]),

        "missing_values": int(
            df.isna()
            .sum()
            .sum()
        ),

        "duplicate_rows": int(
            df.duplicated()
            .sum()
        ),

        "missing_by_column":
            missing_by_column,

        "numeric_summary":
            numeric_summary,

        "categorical_summary":
            categorical_summary,

        "correlations":
            correlations,

        "charts":
            charts,

        "heatmap":
            heatmap,
    }
