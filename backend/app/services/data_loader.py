from pathlib import Path
import pandas as pd


def load_dataset(file_path: str):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(path)

    if extension == ".tsv":
        return pd.read_csv(path, sep="\t")

    if extension in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    if extension == ".json":
        return pd.read_json(path)

    if extension == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(
        f"Unsupported file format: {extension}"
    )


def save_dataset(df, file_path: str):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".csv":
        df.to_csv(path, index=False)

    elif extension == ".tsv":
        df.to_csv(path, index=False, sep="\t")

    elif extension in [".xlsx", ".xls"]:
        df.to_excel(path, index=False)

    elif extension == ".json":
        df.to_json(path, orient="records")

    elif extension == ".parquet":
        df.to_parquet(path, index=False)

    else:
        raise ValueError(
            f"Unsupported output format: {extension}"
        )
