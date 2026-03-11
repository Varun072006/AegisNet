"""Models endpoint — list available AI providers and their status."""

import json
from fastapi import APIRouter
from schemas import ModelsResponse, ModelInfo
from adapters import get_adapters

router = APIRouter(prefix="/api/v1", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """List all registered AI providers, their models, and status."""
    adapters = get_adapters()
    providers = []

    for name, adapter in adapters.items():
        # Quick health check
        try:
            healthy = await adapter.health_check()
            status = "healthy" if healthy else "down"
        except Exception:
            status = "unknown"

        providers.append(ModelInfo(
            provider=adapter.provider,
            display_name=adapter.display_name,
            is_enabled=True,
            models_available=adapter.get_models(),
            cost_per_1k_input=adapter.estimate_cost(1000, 0),
            cost_per_1k_output=adapter.estimate_cost(0, 1000),
            avg_latency_ms=0,
            status=status,
        ))

    return ModelsResponse(providers=providers)
