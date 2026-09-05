from fastapi import APIRouter, HTTPException

from app.services.dataset_manager import (
    get_all_datasets,
    get_active_dataset_id,
    set_active_dataset,
)

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


@router.get("/")
def list_datasets():
    return {
        "datasets": get_all_datasets(),
        "active_dataset": get_active_dataset_id(),
    }


@router.put("/active/{dataset_id}")
def change_active_dataset(dataset_id: str):
    dataset = set_active_dataset(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return {
        "message": "Active dataset changed",
        "active_dataset": dataset,
    }
