"""AegisNet — AI Control Plane. FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prometheus_client import make_asgi_app
from database import init_db
from routes import chat, models, logs, analytics, health, benchmarks, workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize DB tables."""
    await init_db()
    yield


app = FastAPI(
    title="AegisNet",
    description="Universal AI Control Plane — route, monitor, and secure AI model access.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router)
app.include_router(workflows.router)
app.include_router(models.router)
app.include_router(logs.router)
app.include_router(analytics.router)
app.include_router(health.router)
app.include_router(benchmarks.router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    return {
        "name": "AegisNet",
        "version": "0.1.0",
        "description": "Universal AI Control Plane",
        "docs": "/docs",
    }
