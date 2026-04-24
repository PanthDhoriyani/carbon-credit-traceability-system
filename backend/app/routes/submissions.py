from fastapi import APIRouter, HTTPException, Request, Query
from datetime import datetime, timezone
import uuid

from app.models.schemas import (
    SubmissionRequest,
    SubmissionResponse,
    SubmissionListItem,
    BaselineResult,
    AIVerificationResult,
    CreditResult,
)
from app.utils.baseline import get_baseline
from app.services.credit_service import calculate_credits
from app.utils.database import get_db

router = APIRouter()


@router.post("/", response_model=SubmissionResponse, status_code=201)
async def submit_emission(request: Request, body: SubmissionRequest):
    """
    Submit an emission report for verification.
    Runs baseline check → AI fraud detection → credit calculation.
    """
    ml_service = request.app.state.ml_service
    db = get_db()

    # 1. Baseline lookup
    try:
        baseline_data = get_baseline(body.material, body.quantity_tonnes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    baseline_co2 = baseline_data["baseline_co2_tonnes"]

    # 2. AI anomaly detection
    ai_result = ml_service.predict(
        material=body.material,
        quantity_tonnes=body.quantity_tonnes,
        reported_co2=body.reported_co2_tonnes,
        baseline_co2=baseline_co2,
    )

    # 3. Credit calculation
    credit_result = calculate_credits(
        reported_co2=body.reported_co2_tonnes,
        baseline_co2=baseline_co2,
        ai_verdict=ai_result["verdict"],
    )

    # 4. Final status
    final_status = "APPROVED" if credit_result["eligible"] else "REJECTED"

    # 5. Build document for storage
    submission_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    doc = {
        "submission_id": submission_id,
        "company_name": body.company_name,
        "company_id": body.company_id,
        "material": body.material,
        "quantity_tonnes": body.quantity_tonnes,
        "reported_co2_tonnes": body.reported_co2_tonnes,
        "period": body.period,
        "baseline_co2_tonnes": baseline_co2,
        "emission_factor": baseline_data["emission_factor"],
        "baseline_source": baseline_data["source"],
        "anomaly_score": ai_result["anomaly_score"],
        "is_anomaly": ai_result["is_anomaly"],
        "ai_confidence": ai_result["confidence"],
        "ai_verdict": ai_result["verdict"],
        "credits_earned": credit_result["credits_earned"],
        "credit_eligible": credit_result["eligible"],
        "credit_reason": credit_result["reason"],
        "final_status": final_status,
        "blockchain_ref": None,
        "created_at": now,
    }

    if db is not None:
        await db.submissions.insert_one(doc)

    return SubmissionResponse(
        submission_id=submission_id,
        company_name=body.company_name,
        company_id=body.company_id,
        material=body.material,
        quantity_tonnes=body.quantity_tonnes,
        reported_co2_tonnes=body.reported_co2_tonnes,
        period=body.period,
        baseline=BaselineResult(
            material=body.material,
            quantity_tonnes=body.quantity_tonnes,
            emission_factor=baseline_data["emission_factor"],
            baseline_co2_tonnes=baseline_co2,
            unit=baseline_data["unit"],
            source=baseline_data["source"],
        ),
        ai_verification=AIVerificationResult(
            anomaly_score=ai_result["anomaly_score"],
            is_anomaly=ai_result["is_anomaly"],
            confidence=ai_result["confidence"],
            verdict=ai_result["verdict"],
        ),
        credits=CreditResult(
            credits_earned=credit_result["credits_earned"],
            eligible=credit_result["eligible"],
            reason=credit_result["reason"],
        ),
        final_status=final_status,
        blockchain_ref=None,
        created_at=now,
    )


@router.get("/", response_model=list[SubmissionListItem])
async def list_submissions(
    limit: int = Query(50, ge=1, le=200),
    status: str = Query(None),
    material: str = Query(None),
):
    """List all submissions with optional filters."""
    db = get_db()
    if db is None:
        return []

    query = {}
    if status:
        query["final_status"] = status.upper()
    if material:
        query["material"] = material.lower()

    cursor = db.submissions.find(query).sort("created_at", -1).limit(limit)
    docs = await cursor.to_list(length=limit)

    return [
        SubmissionListItem(
            submission_id=d["submission_id"],
            company_name=d["company_name"],
            material=d["material"],
            quantity_tonnes=d["quantity_tonnes"],
            reported_co2_tonnes=d["reported_co2_tonnes"],
            baseline_co2_tonnes=d["baseline_co2_tonnes"],
            credits_earned=d["credits_earned"],
            final_status=d["final_status"],
            created_at=d["created_at"],
        )
        for d in docs
    ]


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(submission_id: str):
    """Fetch a single submission by ID."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    doc = await db.submissions.find_one({"submission_id": submission_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Submission not found")

    return SubmissionResponse(
        submission_id=doc["submission_id"],
        company_name=doc["company_name"],
        company_id=doc["company_id"],
        material=doc["material"],
        quantity_tonnes=doc["quantity_tonnes"],
        reported_co2_tonnes=doc["reported_co2_tonnes"],
        period=doc["period"],
        baseline=BaselineResult(
            material=doc["material"],
            quantity_tonnes=doc["quantity_tonnes"],
            emission_factor=doc["emission_factor"],
            baseline_co2_tonnes=doc["baseline_co2_tonnes"],
            unit=f"t CO2 / t {doc['material']}",
            source=doc["baseline_source"],
        ),
        ai_verification=AIVerificationResult(
            anomaly_score=doc["anomaly_score"],
            is_anomaly=doc["is_anomaly"],
            confidence=doc["ai_confidence"],
            verdict=doc["ai_verdict"],
        ),
        credits=CreditResult(
            credits_earned=doc["credits_earned"],
            eligible=doc["credit_eligible"],
            reason=doc["credit_reason"],
        ),
        final_status=doc["final_status"],
        blockchain_ref=doc.get("blockchain_ref"),
        created_at=doc["created_at"],
    )
