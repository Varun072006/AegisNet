"""Logs endpoint — query audit trail."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from auth import verify_api_key
from database import get_db
from models import RequestLog
from schemas import LogsResponse, LogEntry

router = APIRouter(prefix="/api/v1", tags=["logs"])


@router.get("/logs", response_model=LogsResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    provider: str = Query(None),
    model: str = Query(None),
    status: str = Query(None),
    user_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Retrieve paginated audit logs with optional filters."""
    query = select(RequestLog)

    if provider:
        query = query.where(RequestLog.provider == provider)
    if model:
        query = query.where(RequestLog.model == model)
    if status:
        query = query.where(RequestLog.status == status)
    if user_id:
        query = query.where(RequestLog.user_id == user_id)

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginated results
    query = query.order_by(desc(RequestLog.timestamp))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.scalars().all()

    logs = [LogEntry.model_validate(row) for row in rows]

    return LogsResponse(logs=logs, total=total, page=page, page_size=page_size)
