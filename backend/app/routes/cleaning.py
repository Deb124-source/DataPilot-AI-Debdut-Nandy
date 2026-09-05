from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.cleaner import (
    get_cleaning_suggestions,
    apply_operations,
    apply_recommended_cleaning,
)
from app.services.dataset_manager import get_dataset

router = APIRouter(
    prefix="/cleaning",
    tags=["Cleaning"],
)


class CleaningRequest(BaseModel):
    operations: list[dict]


@router.get("/suggestions/{dataset_id}")
def cleaning_suggestions(dataset_id: str):
    try:
        return {
            "dataset_id": dataset_id,
            "suggestions": get_cleaning_suggestions(
                dataset_id
            ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.post("/apply/{dataset_id}")
def apply_cleaning(
    dataset_id: str,
    request: CleaningRequest,
):
    try:
        return apply_operations(
            dataset_id,
            request.operations,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.post("/apply-recommended/{dataset_id}")
def apply_recommended(dataset_id: str):
    try:
        return apply_recommended_cleaning(
            dataset_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.get("/download/{dataset_id}")
def download_cleaned_dataset(dataset_id: str):
    dataset = get_dataset(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    file_path = Path(dataset["file_path"])

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found",
        )

    return FileResponse(
        path=str(file_path),
        filename=dataset["filename"],
        media_type="text/csv",
    )
