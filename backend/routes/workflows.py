"""Workflow API Routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from database import get_db
from auth import verify_api_key
from workflow_engine import workflow_engine

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])

class WorkflowStep(BaseModel):
    id: str
    model: Optional[str] = None
    prompt_template: str
    max_tokens: int = 1024
    temperature: float = 0.7

class WorkflowRequest(BaseModel):
    initial_input: str
    steps: List[WorkflowStep]
    user_id: str = "anonymous"

@router.post("")
async def run_workflow(
    request: WorkflowRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Execute a multi-stage AI workflow."""
    try:
        # Convert Pydantic models to dicts for the engine
        steps_dict = [step.dict() for step in request.steps]
        result = await workflow_engine.execute_workflow(
            steps=steps_dict,
            initial_input=request.initial_input,
            user_id=request.user_id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
