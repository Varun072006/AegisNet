"""Base adapter interface for AI model providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseAdapter(ABC):
    """Abstract base class for all AI model adapters."""

    provider: str = "unknown"
    display_name: str = "Unknown"
    default_model: str = ""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Send a chat request and return unified response.

        Returns:
            {
                "content": str,
                "input_tokens": int,
                "output_tokens": int,
                "total_tokens": int,
                "model": str,
            }
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ):
        """Send a chat request and yield unified response chunks."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is reachable."""
        pass

    def get_models(self) -> List[str]:
        """Return list of supported model names."""
        return []

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = "") -> float:
        """Estimate cost in USD for given token counts."""
        return 0.0
