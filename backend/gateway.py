"""AI Gateway — core orchestrator that ties routing, adapters, metrics, and compliance together."""

import time
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from router_engine import select_model
from adapters import get_adapter
from observability import metrics
from compliance import log_request
from config import settings


# Failover order
FAILOVER_CHAIN = ["local"]


async def process_chat(
    messages: List[Dict[str, str]],
    model_preference: Optional[str],
    routing_strategy: str,
    user_id: str,
    max_tokens: int,
    temperature: float,
    db: AsyncSession,
) -> Dict:
    """
    Main gateway function:
    1. Route to the best model.
    2. Call the adapter.
    3. Record metrics + compliance log.
    4. On failure, attempt failover.
    5. Return unified response.
    """
    strategy = routing_strategy or settings.default_routing_strategy
    provider, model = select_model(messages, strategy, model_preference)

    prompt_text = messages[-1]["content"] if messages else ""

    providers_tried = []
    last_error = None

    for attempt_provider in _failover_sequence(provider):
        if attempt_provider in providers_tried:
            continue
        providers_tried.append(attempt_provider)

        try:
            adapter = get_adapter(attempt_provider)
            attempt_model = model if attempt_provider == provider else adapter.default_model

            start = time.perf_counter()
            result = await adapter.chat(
                messages=messages,
                model=attempt_model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            latency_ms = (time.perf_counter() - start) * 1000

            cost = adapter.estimate_cost(
                result["input_tokens"], result["output_tokens"], result["model"]
            )

            metrics.record(
                provider=attempt_provider,
                model=result["model"],
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                cost_usd=cost,
                latency_ms=latency_ms,
                success=True,
            )

            await log_request(
                db=db,
                user_id=user_id,
                provider=attempt_provider,
                model=result["model"],
                routing_strategy=strategy,
                prompt=prompt_text,
                response=result["content"],
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                total_tokens=result["total_tokens"],
                cost_usd=cost,
                latency_ms=latency_ms,
                status="success",
            )

            return {
                "content": result["content"],
                "metadata": {
                    "provider": attempt_provider,
                    "model": result["model"],
                    "routing_strategy": strategy,
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "total_tokens": result["total_tokens"],
                    "cost_usd": round(cost, 6),
                    "latency_ms": round(latency_ms, 2),
                },
            }

        except Exception as e:
            last_error = str(e)
            metrics.record(
                provider=attempt_provider,
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0,
                latency_ms=0,
                success=False,
            )
            continue

    await log_request(
        db=db,
        user_id=user_id,
        provider=provider,
        model=model,
        routing_strategy=strategy,
        prompt=prompt_text,
        response="",
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        cost_usd=0,
        latency_ms=0,
        status="error",
        error_message=f"All providers failed. Last error: {last_error}",
    )

    raise RuntimeError(f"All AI providers failed. Last error: {last_error}")


def _failover_sequence(primary: str) -> List[str]:
    """Return failover order."""
    sequence = [primary]
    for p in FAILOVER_CHAIN:
        if p != primary:
            sequence.append(p)
    return sequence
