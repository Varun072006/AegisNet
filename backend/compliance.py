"""Compliance logger — writes audit records to the database."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models import RequestLog


async def log_request(
    db: AsyncSession,
    user_id: str,
    provider: str,
    model: str,
    routing_strategy: str,
    prompt: str,
    response: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    cost_usd: float,
    latency_ms: float,
    status: str = "success",
    error_message: Optional[str] = None,
):
    """Write a complete audit record for one AI request."""
    entry = RequestLog(
        user_id=user_id,
        provider=provider,
        model=model,
        routing_strategy=routing_strategy,
        prompt=prompt,
        response=response,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message,
    )
    db.add(entry)
    await db.commit()
    return entry
