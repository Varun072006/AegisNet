"""Cost Optimizer — tracks per-token pricing for AI providers."""

class CostOptimizer:
    """Manages model pricing and calculates cost-efficiency."""

    # Pricing per 1M tokens (Approximate USD)
    PRICING = {
        "local": {"prompt": 0.0, "completion": 0.0},
        "openai/gpt-4o": {"prompt": 2.50, "completion": 10.00},
        "openai/gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
        "gemini/gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    }

    def get_cost_estimate(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost in USD."""
        rates = self.PRICING.get(model_id, {"prompt": 1.0, "completion": 3.0}) # Default safe high
        cost = (prompt_tokens / 1_000_000 * rates["prompt"]) + (completion_tokens / 1_000_000 * rates["completion"])
        return cost

    def get_cost_penalty(self, model_id: str) -> float:
        """Return a normalized penalty for high-cost models (0.0 to 1.0)."""
        rates = self.PRICING.get(model_id, {"prompt": 0, "completion": 0})
        # Normalize: GPT-4o is the high bar (~1.0 penalty)
        max_rate = 10.0 
        return min(rates["completion"] / max_rate, 1.0)

# Global instance
cost_optimizer = CostOptimizer()
