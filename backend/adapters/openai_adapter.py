"""OpenAI API adapter."""

import os
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional, AsyncGenerator
from .base import BaseAdapter

class OpenAIAdapter(BaseAdapter):
    provider = "openai"
    display_name = "OpenAI"
    default_model = "gpt-4o-mini"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI API key not configured")

        model_name = model or self.default_model
        
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return {
            "content": response.choices[0].message.content,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "model": model_name,
        }

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            raise RuntimeError("OpenAI API key not configured")

        model_name = model or self.default_model
        
        stream = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def health_check(self) -> bool:
        return self.api_key is not None

    def get_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = "") -> float:
        # Mini prices (approx)
        return (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
popd
