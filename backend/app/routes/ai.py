from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_service import ask_dataset_ai


router = APIRouter(
    prefix="/ai",
    tags=["AI Data Assistant"],
)


class AIQuestion(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5000,
    )


@router.post("/chat/{dataset_id}")
def chat_with_dataset(
    dataset_id: str,
    request: AIQuestion,
):
    try:
        answer = ask_dataset_ai(
            dataset_id=dataset_id,
            question=request.question,
        )

        return {
            "dataset_id": dataset_id,
            "question": request.question,
            "answer": answer,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print("AI Error:", error)

        raise HTTPException(
            status_code=500,
            detail=(
                "AI analysis failed. "
                "Please check your Gemini API configuration."
            ),
        )
