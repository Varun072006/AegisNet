"""LangChain integration for AegisNet."""

from typing import Any, List, Optional, Dict
from langchain.llms.base import LLM
from aegisnet import AegisNet

class AegisNetLLM(LLM):
    """AegisNet LLM for LangChain."""
    
    api_key: str
    base_url: str = "http://localhost:8000"
    model: Optional[str] = None
    routing_strategy: str = "auto"
    
    _client: Optional[AegisNet] = None

    @property
    def _llm_type(self) -> str:
        return "aegisnet"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if self._client is None:
            self._client = AegisNet(self.api_key, self.base_url)
            
        response = self._client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            routing_strategy=self.routing_strategy
        )
        return response["content"]

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "routing_strategy": self.routing_strategy,
            "base_url": self.base_url
        }
