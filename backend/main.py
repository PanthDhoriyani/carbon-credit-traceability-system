from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import os

from app.routes import submissions, dashboard, health, auth, admin
from app.services.ml_service import MLService
from app.utils.database import connect_db, close_db
from app.middleware.logging import LoggingMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

ml_service = MLService()  # loads from pkl if exists, trains only if not


async def _auto_seed_admin():
    """
    If ADMIN_EMAIL + ADMIN_PASSWORD env vars are set, automatically create
    the admin account on startup (idempotent — skips if already exists).
    This enables admin creation without shell access (e.g. Render free tier).
    """
    admin_email    = os.getenv("ADMIN_EMAIL", "").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "").strip()

    if not admin_email or not admin_password:
        return  # env vars not set — skip

    from app.utils.database import get_db
    from app.utils.auth import hash_password
    import uuid
    from datetime import datetime, timezone

    db = get_db()
    if db is None:
        logging.warning("Auto-seed: DB not available, skipping admin creation.")
        return

    existing = await db.companies.find_one({"email": admin_email})
    if existing:
        if existing.get("role") == "admin":
            logging.info(f"Auto-seed: Admin '{admin_email}' already exists — skipping.")
        else:
            await db.companies.update_one(
                {"email": admin_email},
                {"$set": {"role": "admin", "is_verified": True}}
            )
            logging.info(f"Auto-seed: Promoted '{admin_email}' to admin.")
        return

    await db.companies.insert_one({
        "user_id":        str(uuid.uuid4()),
        "email":          admin_email,
        "password_hash":  hash_password(admin_password),
        "company_name":   "CCT Admin",
        "company_id":     "ADMIN-001",
        "industry":       "Administration",
        "contact_phone":  None,
        "role":           "admin",
        "is_verified":    True,
        "created_at":     datetime.now(timezone.utc),
    })
    logging.info(f"Auto-seed: Admin account created for '{admin_email}'.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await _auto_seed_admin()          # <-- create admin if env vars set
    app.state.ml_service = ml_service
    yield
    await close_db()


app = FastAPI(
    title="Carbon Credit Tracer API",
    description="AI-powered carbon emission verification and credit issuance system",
    version="2.0.0",
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
app.add_middleware(LoggingMiddleware)

app.include_router(health.router,       prefix="/api",             tags=["Health"])
app.include_router(auth.router,         prefix="/api/auth",        tags=["Auth"])
app.include_router(submissions.router,  prefix="/api/submissions",  tags=["Submissions"])
app.include_router(dashboard.router,    prefix="/api/dashboard",   tags=["Dashboard"])
app.include_router(admin.router,        prefix="/api/admin",       tags=["Admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
