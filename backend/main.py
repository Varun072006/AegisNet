"""AegisNet — AI Control Plane. FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import chat, models, logs, analytics, health


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
app.include_router(models.router)
app.include_router(logs.router)
app.include_router(analytics.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {
        "name": "AegisNet",
        "version": "0.1.0",
        "description": "Universal AI Control Plane",
        "docs": "/docs",
    }
