from fastapi import APIRouter, HTTPException, Depends, Body, Request, BackgroundTasks
from sqlalchemy.orm import Session
from utils.db import get_db
from ..services import chat_service
from ..schemas import ImagePrompt, APIResponse
from ..llm_integration import generate_response
from ..services import media_service
import logging
from typing import Dict

from fastapi.responses import StreamingResponse

log = logging.getLogger(__name__)
router = APIRouter()

@router.post("/process", response_model=APIResponse[str])
async def process_input(
    background_tasks: BackgroundTasks,
    user_input: str = Body(...),
    conversation_id: int = Body(...),
    db: Session = Depends(get_db),
):
    llm_response, error = await chat_service.process_user_input(db, user_input, conversation_id, background_tasks)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return APIResponse(data=llm_response)

@router.post("/process_stream")
async def process_input_stream(
    user_input: str = Body(...),
    conversation_id: int = Body(...),
    db: Session = Depends(get_db),
):
    return StreamingResponse(
        chat_service.process_user_input_stream(db, user_input, conversation_id),
        media_type="text/event-stream"
    )

@router.post("/learn", response_model=APIResponse[str])
async def learn_input(user_input: str = Body(...)):
    try:
        llm_response = await generate_response(user_input, "DELTA")
        return APIResponse(data=llm_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_image/", response_model=APIResponse[Dict[str, str]])
async def generate_image_route(prompt_data: ImagePrompt):
    try:
        data_uri = await media_service.generate_image_data_uri(prompt_data.prompt)
        return APIResponse(data={"image_url": data_uri})
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Image generation failed")

@router.post("/tts", response_model=APIResponse[Dict[str, str]])
async def text_to_speech(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        payload = media_service.synthesize_speech(text)
        return APIResponse(data=payload)
    except Exception as e:
        log.error(f"Error in /tts endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{conversation_id}", response_model=APIResponse[str])
async def get_summary(conversation_id: int, db: Session = Depends(get_db)):
    summary = await chat_service.get_conversation_summary(db, conversation_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found or empty")
    return APIResponse(data=summary)
