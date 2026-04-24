from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from app.routes import submissions, dashboard, health
from app.services.ml_service import MLService
from app.utils.database import connect_db, close_db

load_dotenv()

ml_service = MLService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    ml_service.train()
    app.state.ml_service = ml_service
    yield
    await close_db()

app = FastAPI(
    title="Carbon Credit Tracer API",
    description="AI-powered carbon emission verification and credit issuance system",
    version="1.0.0",
    lifespan=lifespan,
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
