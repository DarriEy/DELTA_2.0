# backend/api/llm_integration.py
from typing import Any, Dict, List, Optional, Union

from .services.llm_service import get_llm_service

vertex_ready = False


def init_vertex() -> bool:
    """Initializes Vertex AI with the provided credentials."""
    global vertex_ready
    service = get_llm_service()
    vertex_ready = service.init_vertex()
    return vertex_ready


async def generate_image(prompt: str) -> Optional[str]:
    """Generates an image using Imagen 3 via Vertex AI."""
    return await get_llm_service().generate_image(prompt)


async def generate_response(
    user_input: str,
    role: str = "DELTA",
    history: Optional[List[Dict[str, Any]]] = None,
) -> Union[str, Dict[str, Any]]:
    """Main entry point for generating responses."""
    return await get_llm_service().generate_response(user_input, role=role, history=history)


async def generate_stream(
    user_input: str,
    role: str = "DELTA",
    history: Optional[List[Dict[str, Any]]] = None,
):
    """Main entry point for generating streaming responses."""
    async for chunk in get_llm_service().generate_stream(
        user_input, role=role, history=history
    ):
        yield chunk


async def generate_summary_from_messages(messages: List[Dict[str, str]]) -> str:
    """Generates a summary of a conversation."""
    return await get_llm_service().generate_summary_from_messages(messages)
