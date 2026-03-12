"""Adapter registry — maps provider names to adapter instances."""

from .local_adapter import LocalAdapter
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .base import BaseAdapter
from typing import Dict

# Singleton registry
_adapters: Dict[str, BaseAdapter] = {}


def get_adapters() -> Dict[str, BaseAdapter]:
    """Return the adapter registry, initializing on first call."""
    global _adapters
    if not _adapters:
        _adapters = {
            "local": LocalAdapter(),
            "openai": OpenAIAdapter(),
            "gemini": GeminiAdapter(),
            # We can map different local instances if needed, e.g. "lmstudio"
        }
    return _adapters


def get_adapter(provider: str) -> BaseAdapter:
    """Get a specific adapter by provider name."""
    adapters = get_adapters()
    if provider not in adapters:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(adapters.keys())}")
    return adapters[provider]
