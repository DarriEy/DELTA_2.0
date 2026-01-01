from fastapi import APIRouter, HTTPException, Depends, Body, Request, BackgroundTasks
from sqlalchemy.orm import Session
from utils.db import get_db
from ..services.chat_service import ChatService, get_chat_service
from ..services.media_service import MediaService, get_media_service
from ..schemas import ImagePrompt, APIResponse, ChatRequest, LearnRequest
from ..services.llm_service import get_llm_service
import logging
from typing import Dict, Optional

from fastapi.responses import StreamingResponse

from ..auth import get_current_user
from ..models import User as DBUser
from ..services.user_service import get_user_service

log = logging.getLogger(__name__)
router = APIRouter()

@router.post("/process", response_model=APIResponse[str])
async def process_input(
    background_tasks: BackgroundTasks,
    request: ChatRequest,
    db: Optional[Session] = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    current_user: DBUser = Depends(get_current_user)
):
    # Verify conversation ownership
    if db:
        conv = get_user_service().get_conversation(db, request.conversation_id)
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized for this conversation")

    llm_response, error = await chat_service.process_user_input(
        db, request.user_input, request.conversation_id, background_tasks
    )
    if error:
        raise HTTPException(status_code=404, detail=error)
    return APIResponse(data=llm_response)

@router.post("/process_stream")
async def process_input_stream(
    request: ChatRequest,
    db: Optional[Session] = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    current_user: DBUser = Depends(get_current_user)
):
    # Verify conversation ownership
    if db:
        conv = get_user_service().get_conversation(db, request.conversation_id)
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized for this conversation")

    return StreamingResponse(
        chat_service.process_user_input_stream(db, request.user_input, request.conversation_id),
        media_type="text/event-stream"
    )

@router.post("/learn", response_model=APIResponse[str])
async def learn_input(
    request: LearnRequest,
    llm_service = Depends(get_llm_service),
    current_user: DBUser = Depends(get_current_user)
):
    try:
        llm_response = await llm_service.generate_response(request.user_input, "DELTA")
        return APIResponse(data=llm_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_image/", response_model=APIResponse[Dict[str, str]])
async def generate_image_route(
    prompt_data: ImagePrompt,
    media_service: MediaService = Depends(get_media_service),
    current_user: DBUser = Depends(get_current_user)
):
    try:
        data_uri = await media_service.generate_image_data_uri(prompt_data.prompt)
        return APIResponse(data={"image_url": data_uri})
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Image generation failed")

@router.post("/tts", response_model=APIResponse[Dict[str, str]])
async def text_to_speech(
    request: Request,
    media_service: MediaService = Depends(get_media_service),
    current_user: DBUser = Depends(get_current_user)
):
    try:
        data = await request.json()
        text = data.get("text")
        payload = media_service.synthesize_speech(text)
        return APIResponse(data=payload)
    except Exception as e:
        log.error(f"Error in /tts endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{conversation_id}", response_model=APIResponse[str])
async def get_summary(
    conversation_id: int, 
    db: Session = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    current_user: DBUser = Depends(get_current_user)
):
    # Verify ownership
    conv = get_user_service().get_conversation(db, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this conversation")

    summary = await chat_service.get_conversation_summary(db, conversation_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found or empty")
    return APIResponse(data=summary)
