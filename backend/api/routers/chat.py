from fastapi import APIRouter, HTTPException, Depends, Request
from ..services.chat_service import ChatService, get_chat_service
from ..schemas import APIResponse, ChatRequest
import logging
from typing import Dict

from fastapi.responses import StreamingResponse
from ..auth import get_current_user

log = logging.getLogger(__name__)
router = APIRouter()

@router.post("/process")
async def process_input(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(get_current_user)
):
    llm_response, error = await chat_service.process_user_input(
        None, request.user_input, request.conversation_id
    )
    if error:
        raise HTTPException(status_code=404, detail=error)
    return APIResponse(data=llm_response)

@router.post("/process_stream")
async def process_input_stream(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(get_current_user)
):
    return StreamingResponse(
        chat_service.process_user_input_stream(None, request.user_input, request.conversation_id),
        media_type="text/event-stream"
    )

@router.get("/summary/{conversation_id}", response_model=APIResponse[str])
async def get_summary(
    conversation_id: int, 
    chat_service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(get_current_user)
):
    return APIResponse(data="Stateless summary unavailable.")
