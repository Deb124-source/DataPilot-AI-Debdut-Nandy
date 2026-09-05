from fastapi import APIRouter, HTTPException

from app.services.dataset_manager import get_dataset
from app.services.data_loader import load_dataset
from app.services.profiler import generate_profile

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/{dataset_id}")
def profile_dataset(dataset_id: str):
    dataset = get_dataset(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    try:
        df = load_dataset(dataset["file_path"])
        profile = generate_profile(df)

        return {
            "dataset_id": dataset_id,
            "profile": profile,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
