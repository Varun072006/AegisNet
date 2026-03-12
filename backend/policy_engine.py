"""Enterprise Policy Engine — defines and enforces routing rules for governance."""

import re
from typing import Dict, Any, List, Optional

class PolicyEngine:
    """Enforces organizational policies on AI model usage."""

    def __init__(self):
        # Default policies
        self.policies = [
            {
                "id": "restricted_data",
                "keywords": ["finance", "salary", "medical", "patient", "revenue", "password"],
                "action": "restrict_to_local",
                "reason": "Sensitive data detected; restricted to local infrastructure."
            },
            {
                "id": "compliance_only",
                "keywords": ["legal", "contract", "terms"],
                "action": "force_high_quality",
                "reason": "Legal content requires high-quality reasoning models."
            }
        ]

    def evaluate_policies(self, prompt: str) -> Dict[str, Any]:
        """
        Check if any policies apply to the given prompt.
        Returns the action and reason if a policy is triggered.
        """
        prompt_lower = prompt.lower()
        
        for policy in self.policies:
            if any(keyword in prompt_lower for keyword in policy["keywords"]):
                return {
                    "triggered": True,
                    "action": policy["action"],
                    "reason": policy["reason"],
                    "policy_id": policy["id"]
                }
        
        return {"triggered": False, "action": None, "reason": None}

# Global instance
policy_engine = PolicyEngine()
