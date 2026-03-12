"""AegisNet Evaluation Lab — automatically tests and ranks AI models."""

from typing import List, Dict, Any
import asyncio
from router_engine import QUALITY_SCORES, select_model
from gateway import process_chat

# Sample benchmark dataset
BENCHMARK_TASKS = [
    {"prompt": "Write a Python function to sort a list of dictionaries by a key.", "category": "coding"},
    {"prompt": "Calculate the surface area of a cylinder with radius 5 and height 10.", "category": "reasoning"},
    {"prompt": "Explain the concept of quantum entanglement to a 5-year old.", "category": "chat"},
]

class EvaluationLab:
    """Automated benchmarking and leaderboard generation."""

    async def run_benchmark(self, db) -> Dict[str, Any]:
        """Runs the benchmark suite across all available models."""
        leaderboard = []
        
        # In a real system, we'd query all models. Here we simulate for speed.
        models_to_test = [
            ("local", "llama3"),
            ("local", "mistral"),
            ("openai", "gpt-4o"),
        ]

        for provider, model_name in models_to_test:
            model_id = f"{provider}/{model_name}"
            total_latency = 0
            success_count = 0
            
            for task in BENCHMARK_TASKS:
                try:
                    # Execute task
                    start_time = asyncio.get_event_loop().time()
                    # We bypass the full gateway for pure model testing if needed, 
                    # but here we use it to test the full stack.
                    response = await process_chat(
                        messages=[{"role": "user", "content": task["prompt"]}],
                        model_preference=model_id,
                        db=db
                    )
                    latency = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    total_latency += latency
                    success_count += 1
                except Exception:
                    continue

            avg_latency = total_latency / success_count if success_count > 0 else 0
            accuracy_score = QUALITY_SCORES.get(model_name, 50) # Simulated accuracy based on quality score
            
            leaderboard.append({
                "model": model_id,
                "accuracy": accuracy_score,
                "latency_ms": round(avg_latency, 2),
                "success_rate": round(success_count / len(BENCHMARK_TASKS) * 100, 2)
            })

        # Sort by accuracy then latency
        leaderboard.sort(key=lambda x: (x["accuracy"], -x["latency_ms"]), reverse=True)
        return {"leaderboard": leaderboard, "dataset_size": len(BENCHMARK_TASKS)}

# Global instance
evaluation_lab = EvaluationLab()
