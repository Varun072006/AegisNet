"""Enterprise-grade AI Safety & Risk Detection."""

import re

class SecurityEngine:
    """Enterprise-grade AI Safety & Risk Detection."""

    def __init__(self):
        # Risk levels
        self.RISK_LOW = 0.0
        self.RISK_MEDIUM = 0.5
        self.RISK_HIGH = 0.9

        # Security patterns
        self.injection_patterns = [
            r"ignore (all )?previous instructions",
            r"system override",
            r"you are now an unfiltered",
            r"jailbreak",
            r"bypass (all )?filters",
        ]
        self.pii_patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "api_key": r"(?:sk-|key-)[a-zA-Z0-9]{20,}",
        }

    def classify_risk(self, prompt: str) -> float:
        """Calculate a risk score from 0.0 to 1.0."""
        score = 0.0
        prompt_lower = prompt.lower()
        
        # Injection check
        if any(re.search(p, prompt_lower) for p in self.injection_patterns):
            score = max(score, self.RISK_HIGH)
            
        # PII Check
        for category, pattern in self.pii_patterns.items():
            if re.search(pattern, prompt):
                score = max(score, self.RISK_MEDIUM)
                
        return score

    def sanitize_prompt(self, prompt: str) -> str:
        """Remove PII from prompt before sending to AI."""
        sanitized = prompt
        for category, pattern in self.pii_patterns.items():
            sanitized = re.sub(pattern, f"[REDACTED_{category.upper()}]", sanitized)
        return sanitized

    def check_prompt(self, text: str) -> tuple[bool, str, float]:
        """
        Comprehensive security check.
        Returns: (is_safe, reason, risk_score)
        """
        risk_score = self.classify_risk(text)
        
        if risk_score >= self.RISK_HIGH:
            return False, "High risk activity detected (Injection)", risk_score
            
        return True, "Safe", risk_score

# Global instance
security_engine = SecurityEngine()
