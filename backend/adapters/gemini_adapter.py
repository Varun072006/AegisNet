"""Google Gemini API adapter."""

import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional, AsyncGenerator
from .base import BaseAdapter

class GeminiAdapter(BaseAdapter):
    provider = "gemini"
    display_name = "Google Gemini"
    default_model = "gemini-1.5-flash"

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model_client = genai.GenerativeModel(self.default_model)
        else:
            self.model_client = None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        if not self.model_client:
            raise RuntimeError("Gemini API key not configured")

        # Convert messages to Gemini format
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [m["content"]]})

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        # Gemini SDK is synchronous/blocking in some parts, but has async support
        # We'll use the async method
        model_name = model or self.default_model
        curr_model = genai.GenerativeModel(model_name)
        
        response = await curr_model.generate_content_async(
            contents,
            generation_config=generation_config
        )

        # Gemini doesn't give precise token counts easily without another call
        # We'll estimate or use metadata if available
        return {
            "content": response.text,
            "input_tokens": 0, # Placeholder
            "output_tokens": 0, # Placeholder
            "total_tokens": 0,
            "model": model_name,
        }

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.model_client:
            raise RuntimeError("Gemini API key not configured")

        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [m["content"]]})

        model_name = model or self.default_model
        curr_model = genai.GenerativeModel(model_name)
        
        response = await curr_model.generate_content_async(
            contents,
            stream=True
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    def get_models(self) -> List[str]:
        return ["gemini-1.5-pro", "gemini-1.5-flash"]

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = "") -> float:
        return 0.0 # Free tier or varies widely
