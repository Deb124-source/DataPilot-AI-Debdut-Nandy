from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import UPLOAD_DIR
from app.services.data_loader import load_dataset
from app.services.dataset_manager import (
    register_dataset,
    set_active_dataset,
)

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {
    ".csv",
    ".tsv",
    ".xlsx",
    ".xls",
    ".json",
    ".parquet",
}


@router.post("/")
async def upload_dataset(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format",
        )

    dataset_id = (
        f"{uuid.uuid4().hex[:12]}{extension}"
    )

    file_path = UPLOAD_DIR / dataset_id

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        df = load_dataset(str(file_path))

    except Exception as error:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=f"Unable to read dataset: {error}",
        )

    register_dataset(
        dataset_id=dataset_id,
        filename=file.filename,
        file_path=str(file_path),
        dataset_type="original",
    )

    set_active_dataset(dataset_id)

    preview = (
        df.head(10)
        .replace({float("nan"): None})
        .where(df.notna(), None)
        .to_dict(orient="records")
    )

    return {
        "message": "Dataset uploaded successfully",
        "dataset_id": dataset_id,
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": [
            str(column)
            for column in df.columns
        ],
        "preview": preview,
    }
