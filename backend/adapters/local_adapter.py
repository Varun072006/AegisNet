"""Local model adapter via Ollama API."""

import httpx
from typing import List, Dict, Any, Optional
from .base import BaseAdapter
from config import settings


class LocalAdapter(BaseAdapter):
    provider = "local"
    display_name = "Local (Ollama)"
    default_model = "llama3"

    def __init__(self):
        self.base_url = settings.ollama_base_url

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        model_name = model or self.default_model

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

        return {
            "content": data.get("message", {}).get("content", ""),
            "input_tokens": data.get("prompt_eval_count", 0),
            "output_tokens": data.get("eval_count", 0),
            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            "model": model_name,
        }

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def get_models(self) -> List[str]:
        return ["llama3", "llama3:8b", "mistral", "codellama"]

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = "") -> float:
        return 0.0  # Local inference is free
