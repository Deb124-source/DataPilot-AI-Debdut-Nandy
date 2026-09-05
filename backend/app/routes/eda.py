from fastapi import APIRouter, HTTPException

from app.services.eda_service import generate_eda

router = APIRouter(prefix="/eda", tags=["EDA"])


@router.get("/{dataset_id}")
def run_eda(dataset_id: str):
    try:
        return {
            "dataset_id": dataset_id,
            "eda": generate_eda(dataset_id),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
