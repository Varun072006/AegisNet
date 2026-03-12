"""Analytics endpoint — aggregated metrics."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from auth import verify_api_key
from database import get_db
from models import RequestLog
from schemas import AnalyticsSummary
from observability import metrics

router = APIRouter(prefix="/api/v1", tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Return aggregated analytics from in-memory metrics and database."""
    # Use in-memory metrics for real-time data
    summary = metrics.get_summary()

    # Enrich with DB aggregates if in-memory is empty (e.g., after restart)
    if summary["total_requests"] == 0:
        result = await db.execute(
            select(
                func.count(RequestLog.id).label("total"),
                func.sum(RequestLog.total_tokens).label("tokens"),
                func.sum(RequestLog.cost_usd).label("cost"),
                func.avg(RequestLog.latency_ms).label("latency"),
            )
        )
        row = result.one()
        if row.total and row.total > 0:
            # Provider breakdown from DB
            prov_result = await db.execute(
                select(
                    RequestLog.provider,
                    func.count(RequestLog.id).label("count"),
                    func.sum(RequestLog.cost_usd).label("cost"),
                ).group_by(RequestLog.provider)
            )
            prov_rows = prov_result.all()
            req_by_provider = {r.provider: r.count for r in prov_rows}
            cost_by_provider = {r.provider: round(r.cost or 0, 6) for r in prov_rows}

            # Model breakdown from DB
            model_result = await db.execute(
                select(
                    RequestLog.model,
                    func.count(RequestLog.id).label("count"),
                ).group_by(RequestLog.model)
            )
            model_rows = model_result.all()
            req_by_model = {r.model: r.count for r in model_rows}

            # Success rate
            success_result = await db.execute(
                select(func.count(RequestLog.id)).where(RequestLog.status == "success")
            )
            success_count = success_result.scalar() or 0

            summary = {
                "total_requests": row.total,
                "total_tokens": row.tokens or 0,
                "total_cost_usd": round(row.cost or 0, 6),
                "avg_latency_ms": round(row.latency or 0, 2),
                "success_rate": round(success_count / row.total * 100, 2) if row.total else 0.0,
                "requests_by_provider": req_by_provider,
                "requests_by_model": req_by_model,
                "cost_by_provider": cost_by_provider,
                "recent_latency": [],
            }

    return AnalyticsSummary(**summary)
