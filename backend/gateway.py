"""AI Gateway — core orchestrator that ties routing, adapters, metrics, and compliance together."""

import time
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from router_engine import select_model
from adapters import get_adapter
from observability import metrics
from compliance import log_request
from security_engine import security_engine
from quality_evaluator import quality_evaluator
from policy_engine import policy_engine
from router_engine import select_model, _classify_task, performance_tracker
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
    
    prompt_text = messages[-1]["content"] if messages else ""

    # Security Filter (Updated for v3 Elite Safety)
    is_safe, reason, risk_score = security_engine.check_prompt(prompt_text)
    
    if not is_safe:
        # High Risk: Block immediately
        await log_request(
            db=db,
            user_id=user_id,
            provider="system",
            model="security-engine-v3",
            routing_strategy=strategy,
            prompt=prompt_text,
            response="",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            cost_usd=0,
            latency_ms=0,
            status="blocked",
            error_message=f"Risk: {risk_score} - {reason}",
        )
        raise ValueError(f"AegisNet v3 Security: {reason}")
    
    # Medium Risk: Sanitize prompt before sending
    if risk_score >= 0.5:
        prompt_text = security_engine.sanitize_prompt(prompt_text)
        # Update messages with sanitized text
        messages[-1]["content"] = prompt_text

    provider, model = select_model(messages, strategy, model_preference)

    # --- Enterprise Governance: Policy Engine ---
    policy_result = policy_engine.evaluate_policies(prompt_text)
    if policy_result["triggered"]:
        if policy_result["action"] == "restrict_to_local":
            provider = "local"
            # Keep original model if it was local, otherwise fallback to default
            if model_preference and not model_preference.startswith("local/"):
                model = None 
        elif policy_result["action"] == "force_high_quality":
            strategy = "quality"
            provider, model = select_model(messages, strategy, model_preference)
    # --------------------------------------------

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
            
            # Record performance for self-learning router
            performance_tracker.record_performance(result["model"], latency_ms, True)

            # --- AI Reliability: Quality Evaluation (Self-Healing) ---
            task_type = _classify_task(prompt_text)
            quality = quality_evaluator.evaluate(result["content"], task_context=task_type)
            
            if quality["should_retry"] and len(providers_tried) < 3:
                # Log the quality failure and continue to next provider in failover chain
                last_error = f"Quality low: {quality['reason']}"
                metrics.record(
                    provider=attempt_provider,
                    model=result["model"],
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0,
                    latency_ms=0,
                    success=False,
                )
                continue
            # --------------------------------------------------------

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
            performance_tracker.record_performance(model, 0, False)
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


async def process_chat_stream(
    messages: List[Dict[str, str]],
    model_preference: Optional[str],
    routing_strategy: str,
    user_id: str,
    max_tokens: int,
    temperature: float,
    db: AsyncSession,
):
    """Streaming version of process_chat."""
    strategy = routing_strategy or settings.default_routing_strategy
    prompt_text = messages[-1]["content"] if messages else ""

    # Security Filter
    is_safe, reason = security_engine.check_prompt(prompt_text)
    if not is_safe:
        raise ValueError(f"Security Alert: {reason}")

    provider, model = select_model(messages, strategy, model_preference)
    adapter = get_adapter(provider)
    
    # We yield directly from the adapter for now
    async for chunk in adapter.chat_stream(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        yield chunk


def _failover_sequence(primary: str) -> List[str]:
    """Return failover order."""
    sequence = [primary]
    for p in FAILOVER_CHAIN:
        if p != primary:
            sequence.append(p)
    return sequence
