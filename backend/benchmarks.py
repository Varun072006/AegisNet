"""Automated model benchmarking system."""

import time
import asyncio
from typing import List, Dict
from adapters import get_adapter
from config import settings

TEST_PROMPTS = [
    "Write a hello world in Python.",
    "Solve 123 * 456.",
    "Explain quantum entanglement like I'm five.",
]

async def run_benchmark(provider: str, model: str) -> Dict:
    """Run benchmark for a specific model."""
    adapter = get_adapter(provider)
    latencies = []
    tokens_per_sec = []
    total_cost = 0.0
    
    for prompt in TEST_PROMPTS:
        messages = [{"role": "user", "content": prompt}]
        start = time.perf_counter()
        try:
            result = await adapter.chat(messages, model=model)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
            
            if result["output_tokens"] > 0:
                tps = result["output_tokens"] / (latency / 1000)
                tokens_per_sec.append(tps)
            
            total_cost += adapter.estimate_cost(
                result["input_tokens"], result["output_tokens"], model
            )
        except Exception:
            continue

    if not latencies:
        return {"status": "failed"}

    return {
        "provider": provider,
        "model": model,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
        "avg_tokens_per_sec": round(sum(tokens_per_sec) / len(tokens_per_sec), 2) if tokens_per_sec else 0,
        "estimated_cost_usd": round(total_cost / len(TEST_PROMPTS), 6),
        "status": "success"
    }

async def benchmark_all():
    """Run benchmarks for all configured models."""
    # This would iterate over registered models in a real system
    # For demo, we just test a few
    models_to_test = [
        ("local", "llama3"),
        ("local", "mistral"),
    ]
    
    results = []
    for p, m in models_to_test:
        res = await run_benchmark(p, m)
        results.append(res)
    
    return results
