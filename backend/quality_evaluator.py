"""AI Quality Evaluator — detects hallucinations and low-quality responses."""

import re
from typing import Dict, Any, List

class QualityEvaluator:
    """Evaluates the quality of AI responses to trigger self-healing."""

    def __init__(self):
        # Heuristic patterns for poor responses
        self.failure_patterns = [
            r"I'm sorry, but I can't",
            r"As an AI language model",
            r"I don't have enough information",
            r"Apologies, but I am unable",
            r"I cannot fulfill this request",
        ]

    def evaluate(self, content: str, task_context: str = "") -> Dict[str, Any]:
        """
        Evaluate response quality.
        Returns a score from 0.0 to 1.0 and a recommendation.
        """
        if not content or len(content.strip()) < 5:
            return {"score": 0.0, "reason": "Empty or too short", "should_retry": True}

        # 1. Check for failure patterns
        for pattern in self.failure_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    "score": 0.2, 
                    "reason": "Model refusal or limitation detected", 
                    "should_retry": True
                }

        # 2. Heuristic length check (too short for complex context)
        if task_context == "coding" and len(content.split()) < 10:
            return {
                "score": 0.4, 
                "reason": "Insufficient detail for coding task", 
                "should_retry": True
            }

        # 3. Basic formatting check for code
        if task_context == "coding" and "```" not in content:
            return {
                "score": 0.5, 
                "reason": "Missing code blocks in coding response", 
                "should_retry": True
            }

        return {"score": 1.0, "reason": "Passed heuristics", "should_retry": False}

# Global instance
quality_evaluator = QualityEvaluator()
