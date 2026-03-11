"""In-memory observability metrics collector."""

import logging
from collections import defaultdict
from typing import Dict, Any, List
from threading import Lock


class MetricsCollector:
    """Collects and aggregates runtime metrics."""

    def __init__(self):
        self._lock = Lock()
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_errors = 0
        self.latencies: List[float] = []

        # Breakdowns
        self.requests_by_provider: Dict[str, int] = defaultdict(int)
        self.requests_by_model: Dict[str, int] = defaultdict(int)
        self.cost_by_provider: Dict[str, float] = defaultdict(float)
        self.tokens_by_provider: Dict[str, int] = defaultdict(int)

    def record(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: float,
        success: bool = True,
    ):
        with self._lock:
            self.total_requests += 1
            self.total_tokens += input_tokens + output_tokens
            self.total_cost += cost_usd
            self.latencies.append(latency_ms)
            if not success:
                self.total_errors += 1

            self.requests_by_provider[provider] += 1
            self.requests_by_model[model] += 1
            self.cost_by_provider[provider] += cost_usd
            self.tokens_by_provider[provider] += input_tokens + output_tokens

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
            success_rate = (
                ((self.total_requests - self.total_errors) / self.total_requests * 100)
                if self.total_requests > 0 else 0.0
            )
            return {
                "total_requests": int(self.total_requests),
                "total_tokens": int(self.total_tokens),
                "total_cost_usd": float(round(self.total_cost, 6)),
                "avg_latency_ms": float(round(avg_latency, 2)),
                "success_rate": float(round(success_rate, 2)),
                "requests_by_provider": dict(self.requests_by_provider),
                "requests_by_model": dict(self.requests_by_model),
                "cost_by_provider": {k: float(round(v, 6)) for k, v in self.cost_by_provider.items()},
                "recent_latency": list(self.latencies[-50:]),  # Last 50
            }


# Global singleton
metrics = MetricsCollector()
