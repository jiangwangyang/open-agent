from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse

from openagent.service import agent_service

router = APIRouter()


@router.get("/stream/{conversation_id}")
async def agent_stream_get(conversation_id: int, query: str = Query(...)):
    return StreamingResponse(
        agent_service.agent(conversation_id, query),
        media_type="text/event-stream"
    )


@router.post("/stream/{conversation_id}")
async def agent_stream_post(conversation_id: int, query: str = Body(..., embed=True)):
    return StreamingResponse(
        agent_service.agent(conversation_id, query),
        media_type="text/event-stream"
    )
