from fastapi import APIRouter, HTTPException, Depends, Request
from ..services.chat_service import ChatService, get_chat_service
from ..schemas import APIResponse, ChatRequest
import logging
from typing import Dict

from fastapi.responses import StreamingResponse
from ..auth import get_current_user
from ..llm_providers import get_tts_provider
from utils.config import get_settings

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
    # Optional auth for easier local development/demo
    # current_user: dict = Depends(get_current_user)
):
    log.info(f"Stream request received for conversation {request.conversation_id}")
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

@router.post("/tts_stream")
async def text_to_speech_stream(
    request: dict,
    settings = Depends(get_settings)
):
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    tts_provider = get_tts_provider(settings)
    if not tts_provider:
        raise HTTPException(status_code=501, detail="TTS provider not configured")
    
    return StreamingResponse(
        tts_provider.generate_speech_stream(text),
        media_type="audio/mpeg"
    )
