"""Smart routing engine — selects the best AI model for each request."""

from typing import Dict, List, Optional, Tuple
from adapters import get_adapters, get_adapter
from adapters.base import BaseAdapter
from cost_optimizer import cost_optimizer


# Rough model quality tiers (higher = better)
QUALITY_SCORES: Dict[str, int] = {
    "llama3": 75,
    "llama3:8b": 80,
    "mistral": 82,
    "codellama": 85,
    "gpt-4o": 98,
    "gpt-4o-mini": 90,
    "gemini-1.5-pro": 97,
    "gemini-1.5-flash": 88,
}

# Rough latency tiers (lower = faster, ms)
LATENCY_ESTIMATES = {
    "llama3": 800, 
    "llama3:8b": 600, 
    "mistral": 500, 
    "codellama": 700,
}

class PerformanceTracker:
    """Tracks real-time performance to optimize routing."""
    def __init__(self):
        self.stats = {} # { "model_name": {"latency": [], "success": [], "ratings": []} }

    def record_performance(self, model: str, latency: float, success: bool):
        if model not in self.stats:
            self.stats[model] = {"latency": [], "success": [], "ratings": []}
        
        # Keep last 50 samples
        lats = self.stats[model]["latency"]
        self.stats[model]["latency"] = (lats + [latency])[-50:]
        
        succs = self.stats[model]["success"]
        self.stats[model]["success"] = (succs + [bool(success)])[-50:]

    def record_rating(self, model: str, rating: int):
        """Record user rating (1-5)."""
        if model not in self.stats:
            self.stats[model] = {"latency": [], "success": [], "ratings": []}
        self.stats[model]["ratings"] = (self.stats[model]["ratings"] + [rating])[-100:]

    def get_avg_rating(self, model: str) -> float:
        ratings = self.stats.get(model, {}).get("ratings", [])
        return sum(ratings) / len(ratings) if ratings else 4.0 # Default decent rating

    def get_avg_latency(self, model: str) -> float:
        lats = self.stats.get(model, {}).get("latency", [])
        return sum(lats) / len(lats) if lats else LATENCY_ESTIMATES.get(model, 1000)

    def get_reliability(self, model: str) -> float:
        successes = self.stats.get(model, {}).get("success", [])
        return sum(successes) / len(successes) if successes else 1.0

performance_tracker = PerformanceTracker()


def _classify_task(prompt: str) -> str:
    """Classify prompt into task categories (Coding, Reasoning, Chat)."""
    prompt = prompt.lower()
    if any(k in prompt for k in ["code", "python", "javascript", "function", "bug", "write a script"]):
        return "coding"
    if any(k in prompt for k in ["calculate", "solve", "math", "equation", "proof"]):
        return "reasoning"
    if len(prompt) > 500:
        return "reasoning"
    return "chat"


def _estimate_complexity(messages: List[Dict]) -> str:
    """Estimate complexity of the conversation."""
    total_len = sum(len(m.get("content", "")) for m in messages)
    if total_len > 1000:
        return "high"
    if total_len > 200:
        return "medium"
    return "low"


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
    """Intelligent routing based on intent classification."""
    prompt = messages[-1].get("content", "") if messages else ""
    task = _classify_task(prompt)
    
    if task == "coding":
        return ("local", "codellama")
    if task == "reasoning":
        return ("local", "mistral")
    
    return ("local", "llama3")
def route_optimized(messages: List[Dict]) -> Tuple[str, str]:
    """10/10 Elite Routing: Dynamic scoring based on Quality, Reliability, Cost, and Latency."""
    best = None
    best_score = -999.0
    
    for provider, model, _ in _get_available_models():
        model_id = f"{provider}/{model}"
        
        # 1. Quality (0-100)
        quality = QUALITY_SCORES.get(model, 50)
        
        # 2. Reliability (0.0 - 1.0)
        reliability = performance_tracker.get_reliability(model)
        
        # 3. Cost Penalty (0.0 - 1.0)
        cost_penalty = cost_optimizer.get_cost_penalty(model_id)
        
        # 4. Latency Penalty (0.0 - 1.0)
        # Normalize: 2000ms is the high bar (~1.0 penalty)
        latency = performance_tracker.get_avg_latency(model)
        latency_penalty = min(latency / 2000.0, 1.0)
        
        # 5. User Rating (1-5 normalized to 0-1)
        avg_rating = performance_tracker.get_avg_rating(model)
        norm_rating = (avg_rating - 1.0) / 4.0
        
        # 10/10 Elite Formula (Updated with feedback)
        # score = (Q * 0.4) + (R * 0.2) + (Rating * 0.2) - (C * 0.1) - (L * 0.1)
        norm_quality = quality / 100.0
        
        score = (norm_quality * 0.4) + (reliability * 0.2) + (norm_rating * 0.2) - (cost_penalty * 0.1) - (latency_penalty * 0.1)
        
        if score > best_score:
            best_score = score
            best = (provider, model)
            
    return best or ("local", "llama3")


STRATEGIES = {
    "auto": route_auto,
    "cost_optimized": route_cost_optimized,
    "performance": route_performance,
    "quality": route_quality,
    "optimized": route_optimized,
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
        return (str(parts[0]), str(parts[1]))

    route_fn = STRATEGIES.get(strategy, route_auto)
    result = route_fn(messages)
    return result if result else ("local", "llama3")
