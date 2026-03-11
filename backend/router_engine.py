"""Smart routing engine — selects the best AI model for each request."""

from typing import Dict, List, Optional, Tuple
from adapters import get_adapters, get_adapter
from adapters.base import BaseAdapter


# Rough model quality tiers (higher = better)
QUALITY_SCORES = {
    "llama3": 65, 
    "llama3:8b": 60, 
    "mistral": 63, 
    "codellama": 60,
}

# Rough latency tiers (lower = faster, ms)
LATENCY_ESTIMATES = {
    "llama3": 800, 
    "llama3:8b": 600, 
    "mistral": 500, 
    "codellama": 700,
}


def _estimate_complexity(messages: List[Dict]) -> str:
    """Estimate task complexity from message length."""
    total_chars = sum(len(m.get("content", "")) for m in messages)
    if total_chars < 200:
        return "low"
    elif total_chars < 1000:
        return "medium"
    return "high"


def _get_available_models() -> List[Tuple[str, str, BaseAdapter]]:
    """Return list of (provider, model, adapter) for all available models."""
    available = []
    adapters = get_adapters()
    for provider_name, adapter in adapters.items():
        for model_name in adapter.get_models():
            available.append((provider_name, model_name, adapter))
    return available


def route_cost_optimized(messages: List[Dict]) -> Tuple[str, str]:
    """Select the cheapest model. (All local are free currently)"""
    return ("local", "llama3")


def route_performance(messages: List[Dict]) -> Tuple[str, str]:
    """Select the fastest model."""
    best = None
    best_latency = float("inf")
    for provider, model, _ in _get_available_models():
        latency = LATENCY_ESTIMATES.get(model, 9999)
        if latency < best_latency:
            best_latency = latency
            best = (provider, model)
    return best or ("local", "llama3")


def route_quality(messages: List[Dict]) -> Tuple[str, str]:
    """Select the highest quality model."""
    best = None
    best_score = -1
    for provider, model, _ in _get_available_models():
        score = QUALITY_SCORES.get(model, 0)
        if score > best_score:
            best_score = score
            best = (provider, model)
    return best or ("local", "llama3")


def route_auto(messages: List[Dict]) -> Tuple[str, str]:
    """Balanced routing based on task complexity."""
    complexity = _estimate_complexity(messages)
    if complexity == "low":
        return route_performance(messages)
    else:
        return route_quality(messages)


STRATEGIES = {
    "auto": route_auto,
    "cost_optimized": route_cost_optimized,
    "performance": route_performance,
    "quality": route_quality,
}


def select_model(
    messages: List[Dict],
    strategy: str = "auto",
    preferred_model: Optional[str] = None,
) -> Tuple[str, str]:
    """Select a model based on strategy or user preference.

    Args:
        messages: Chat messages for complexity estimation.
        strategy: Routing strategy name.
        preferred_model: If set, format is 'provider/model' (e.g., 'local/llama3').

    Returns:
        (provider, model) tuple.
    """
    if preferred_model and "/" in preferred_model:
        parts = preferred_model.split("/", 1)
        return (parts[0], parts[1])

    route_fn = STRATEGIES.get(strategy, route_auto)
    return route_fn(messages)
