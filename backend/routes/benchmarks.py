"""Benchmark routes."""

from fastapi import APIRouter, Depends
from auth import verify_api_key
from benchmarks import benchmark_all

router = APIRouter(prefix="/api/v1/benchmarks", tags=["benchmarks"])

@router.get("/")
async def get_benchmarks(api_key: str = Depends(verify_api_key)):
    """Run and return model benchmarks."""
    results = await benchmark_all()
    return results
