"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ── Chat ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    model: Optional[str] = Field(None, description="Specific model, e.g. 'local/llama3'")
    routing_strategy: Optional[str] = Field(None, description="auto, cost_optimized, performance, quality")
    user_id: Optional[str] = Field("anonymous", description="Caller identity for logging")
    max_tokens: Optional[int] = Field(1024, description="Max tokens in response")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")


class ChatResponseMetadata(BaseModel):
    provider: str
    model: str
    routing_strategy: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


class ChatResponse(BaseModel):
    content: str
    metadata: ChatResponseMetadata


# ── Logs ──────────────────────────────────────────────

class LogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    user_id: str
    provider: str
    model: str
    routing_strategy: str
    prompt: str
    response: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    status: str = "success"
    error_message: Optional[str] = None


class LogsResponse(BaseModel):
    logs: List[LogEntry]
    total: int
    page: int
    page_size: int


# ── Analytics ─────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_latency_ms: float = 0.0
    success_rate: float = 0.0
    requests_by_provider: dict = {}
    requests_by_model: dict = {}
    cost_by_provider: dict = {}
    recent_latency: List[float] = []


# ── Models ────────────────────────────────────────────

class ModelInfo(BaseModel):
    provider: str
    display_name: str
    is_enabled: bool
    models_available: List[str]
    cost_per_1k_input: float
    cost_per_1k_output: float
    avg_latency_ms: float
    status: str = "unknown"  # healthy, degraded, down, unknown


class ModelsResponse(BaseModel):
    providers: List[ModelInfo]
