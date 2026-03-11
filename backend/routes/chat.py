"""Chat endpoint — unified AI chat through AegisNet."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import ChatRequest, ChatResponse, ChatResponseMetadata
from gateway import process_chat

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a chat request through AegisNet's AI gateway."""
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        result = await process_chat(
            messages=messages,
            model_preference=request.model,
            routing_strategy=request.routing_strategy or "auto",
            user_id=request.user_id or "anonymous",
            max_tokens=request.max_tokens or 1024,
            temperature=request.temperature or 0.7,
            db=db,
        )

        return ChatResponse(
            content=result["content"],
            metadata=ChatResponseMetadata(**result["metadata"]),
        )

    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
