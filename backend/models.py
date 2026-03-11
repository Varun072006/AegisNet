"""SQLAlchemy ORM models for AegisNet."""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class RequestLog(Base):
    """Full audit trail for every AI request routed through AegisNet."""
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Request info
    user_id = Column(String(255), default="anonymous")
    provider = Column(String(50), nullable=False)         # e.g., local
    model = Column(String(100), nullable=False)            # gpt-4o-mini, gemini-2.0-flash, etc.
    routing_strategy = Column(String(50), default="auto")

    # Content
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)

    # Metrics
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)

    # Status
    status = Column(String(20), default="success")        # success, error, timeout
    error_message = Column(Text, nullable=True)


class ModelConfig(Base):
    """Registered AI providers and their configuration."""
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=True)
    models_available = Column(Text, default="[]")          # JSON array of model names
    cost_per_1k_input = Column(Float, default=0.0)
    cost_per_1k_output = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
