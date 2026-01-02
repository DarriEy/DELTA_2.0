# backend/api/services/llm_service.py
import logging
from typing import Any, Dict, List, Optional, Union

from utils.config import get_settings
from utils.google_utils import get_credentials
from utils.prompts import DELTA_SYSTEM_PROMPT, EDUCATIONAL_GUIDE_PROMPT
from ..llm_providers import get_llm_provider

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self) -> None:
        self._provider = None

    def init_vertex(self) -> bool:
        # No-op for streamlined stateless mode unless explicitly needed
        return True

    def _get_provider(self):
        if self._provider is None:
            settings = get_settings()
            self._provider = get_llm_provider(settings)
        return self._provider

    async def generate_response(
        self,
        user_input: str,
        role: str = "DELTA",
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[str, Dict[str, Any]]:
        system_prompt = (
            DELTA_SYSTEM_PROMPT if role == "DELTA" else EDUCATIONAL_GUIDE_PROMPT
        )
        provider = self._get_provider()

        if hasattr(provider, "generate_response_with_history"):
            return await provider.generate_response_with_history(
                user_input,
                system_prompt,
                history or [],
                tools=None,
            )
        return await provider.generate_response(user_input, system_prompt)

    async def generate_stream(
        self,
        user_input: str,
        role: str = "DELTA",
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        system_prompt = (
            DELTA_SYSTEM_PROMPT if role == "DELTA" else EDUCATIONAL_GUIDE_PROMPT
        )
        provider = self._get_provider()

        if hasattr(provider, "generate_response_stream_with_history"):
            async for chunk in provider.generate_response_stream_with_history(
                user_input, system_prompt, history or []
            ):
                yield chunk
        else:
            async for chunk in provider.generate_response_stream(user_input, system_prompt):
                yield chunk

    async def generate_summary_from_messages(
        self, messages: List[Dict[str, str]]
    ) -> str:
        formatted_messages = "\n".join(
            [f"{msg['sender']}: {msg['content']}" for msg in messages]
        )
        prompt = (
            "Please provide a concise scientific summary of the following conversation, "
            "highlighting key hydrological insights and action items:\n\n"
            f"{formatted_messages}\n\nSummary:"
        )
        provider = self._get_provider()
        return await provider.generate_response(
            prompt, "You are a professional hydrological research summarizer."
        )

_SERVICE: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = LLMService()
    return _SERVICE