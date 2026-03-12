import httpx
from typing import List, Dict, Optional, Any, AsyncGenerator

class AegisNet:
    """AegisNet Python SDK."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        routing_strategy: str = "auto",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        user_id: str = "anonymous",
    ) -> Dict[str, Any]:
        """Synchronous chat."""
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/api/v1/chat",
                json={
                    "messages": messages,
                    "model": model,
                    "routing_strategy": routing_strategy,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "user_id": user_id,
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def achat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        routing_strategy: str = "auto",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        user_id: str = "anonymous",
    ) -> Dict[str, Any]:
        """Asynchronous chat."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chat",
                json={
                    "messages": messages,
                    "model": model,
                    "routing_strategy": routing_strategy,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "user_id": user_id,
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        routing_strategy: str = "auto",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        user_id: str = "anonymous",
    ) -> AsyncGenerator[str, None]:
        """Asynchronous streaming chat (SSE)."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/v1/chat/stream",
                json={
                    "messages": messages,
                    "model": model,
                    "routing_strategy": routing_strategy,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "user_id": user_id,
                },
                headers=self.headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        content = line[6:].strip()
                        if content:
                            yield content
