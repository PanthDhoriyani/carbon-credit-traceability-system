from fastapi import APIRouter
from app.models.schemas import DashboardStats
from app.utils.database import get_db

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Aggregate statistics for the dashboard."""
    db = get_db()

    if db is None:
        return DashboardStats(
            total_submissions=0,
            approved_count=0,
            rejected_count=0,
            total_credits_issued=0.0,
            total_co2_saved_tonnes=0.0,
            approval_rate=0.0,
            top_material=None,
        )

    total = await db.submissions.count_documents({})
    approved = await db.submissions.count_documents({"final_status": "APPROVED"})
    rejected = await db.submissions.count_documents({"final_status": "REJECTED"})

    # Total credits issued
    pipeline_credits = [
        {"$match": {"final_status": "APPROVED"}},
        {"$group": {"_id": None, "total": {"$sum": "$credits_earned"}}},
    ]
    credits_result = await db.submissions.aggregate(pipeline_credits).to_list(1)
    total_credits = credits_result[0]["total"] if credits_result else 0.0

    # Total CO2 saved = same as credits (1 credit = 1 tonne)
    total_co2_saved = total_credits

    # Most submitted material
    pipeline_material = [
        {"$group": {"_id": "$material", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1},
    ]
    mat_result = await db.submissions.aggregate(pipeline_material).to_list(1)
    top_material = mat_result[0]["_id"] if mat_result else None

    approval_rate = round((approved / total * 100), 1) if total > 0 else 0.0

    return DashboardStats(
        total_submissions=total,
        approved_count=approved,
        rejected_count=rejected,
        total_credits_issued=round(total_credits, 2),
        total_co2_saved_tonnes=round(total_co2_saved, 2),
        approval_rate=approval_rate,
        top_material=top_material,
    )


@router.get("/recent")
async def get_recent_submissions(limit: int = 10):
    """Most recent submissions for the dashboard feed."""
    db = get_db()
    if db is None:
        return []

    cursor = db.submissions.find(
        {},
        {
            "_id": 0,
            "submission_id": 1,
            "company_name": 1,
            "material": 1,
            "reported_co2_tonnes": 1,
            "baseline_co2_tonnes": 1,
            "credits_earned": 1,
            "final_status": 1,
            "ai_verdict": 1,
            "created_at": 1,
        },
    ).sort("created_at", -1).limit(limit)

    return await cursor.to_list(length=limit)


@router.get("/credits-by-material")
async def credits_by_material():
    """Credits issued grouped by material type."""
    db = get_db()
    if db is None:
        return []

    pipeline = [
        {"$match": {"final_status": "APPROVED"}},
        {
            "$group": {
                "_id": "$material",
                "total_credits": {"$sum": "$credits_earned"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"total_credits": -1}},
    ]

    results = await db.submissions.aggregate(pipeline).to_list(10)
    return [
        {
            "material": r["_id"],
            "total_credits": round(r["total_credits"], 2),
            "submission_count": r["count"],
        }
        for r in results
    ]
