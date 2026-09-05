from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ai import router as ai_router
from app.routes.upload import router as upload_router
from app.routes.profile import router as profile_router
from app.routes.cleaning import router as cleaning_router
from app.routes.eda import router as eda_router
from app.routes.datasets import router as datasets_router

app = FastAPI(
    title="DataPilot AI",
    version="1.0.0",
    description="Smart data processing and automated EDA platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(profile_router)
app.include_router(cleaning_router)
app.include_router(eda_router)
app.include_router(datasets_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {
        "message": "DataPilot AI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
