from fastapi import APIRouter, HTTPException, Depends, Body, Request
from sqlalchemy.orm import Session
from ..models import get_db
from ..services import chat_service
from ..schemas import ImagePrompt, Message
from ..llm_integration import generate_response, generate_image
from utils.google_utils import get_tts_client
from google.cloud import texttospeech
import base64
import logging
from typing import List

from fastapi.responses import StreamingResponse

log = logging.getLogger(__name__)
router = APIRouter()

@router.post("/process")
async def process_input(
    user_input: str = Body(...),
    conversation_id: int = Body(...),
    db: Session = Depends(get_db),
):
    llm_response, error = await chat_service.process_user_input(db, user_input, conversation_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"llmResponse": llm_response}

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

@router.post("/learn")
async def learn_input(user_input: str = Body(...)):
    try:
        llm_response = await generate_response(user_input, "DELTA")
        return {"response": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_image/")
async def generate_image_route(prompt_data: ImagePrompt):
    try:
        data_uri = await generate_image(prompt_data.prompt)
        if data_uri:
            return {"image_url": data_uri}
        else:
            raise HTTPException(status_code=500, detail="Image generation failed")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Image generation failed")

@router.post("/tts")
async def text_to_speech(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        tts_client = get_tts_client()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Polyglot-1"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_content = base64.b64encode(response.audio_content).decode("utf-8")
        return {"audioContent": audio_content}
    except Exception as e:
        log.error(f"Error in /tts endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{conversation_id}")
async def get_summary(conversation_id: int, db: Session = Depends(get_db)):
    summary = await chat_service.get_conversation_summary(db, conversation_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found or empty")
    return {"summary": summary}
