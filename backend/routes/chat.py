from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth import verify_api_key
from redis_utils import redis_client
from database import get_db
from schemas import ChatRequest, ChatResponse, ChatResponseMetadata
from gateway import process_chat, process_chat_stream

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Streaming AI chat via SSE."""
    # Rate Limiting
    user_id = request.user_id or "anonymous"
    is_allowed = await redis_client.check_rate_limit(user_id)
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Too many requests.")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def event_generator():
        try:
            async for chunk in process_chat_stream(
                messages=messages,
                model_preference=request.model,
                routing_strategy=request.routing_strategy or "auto",
                user_id=request.user_id or "anonymous",
                max_tokens=request.max_tokens or 1024,
                temperature=request.temperature or 0.7,
                db=db,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Send a chat request through AegisNet's AI gateway."""
    # Rate Limiting
    user_id = request.user_id or "anonymous"
    is_allowed = await redis_client.check_rate_limit(user_id)
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

    # Caching (Step 1.2)
    cache_key = f"cache:{hash(str(request.messages))}:{request.model}:{request.routing_strategy}"
    cached_response = await redis_client.get_cache(cache_key)
    if cached_response:
        import json
        return ChatResponse(**json.loads(cached_response))

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

        response = ChatResponse(
            content=result["content"],
            metadata=ChatResponseMetadata(**result["metadata"]),
        )
        
        # Store in cache (1 hour)
        import json
        await redis_client.set_cache(cache_key, response.model_dump_json(), expire=3600)

        return response

    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
