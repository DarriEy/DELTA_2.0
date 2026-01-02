# backend/api/services/llm_service.py
import logging
from typing import Any, Dict, List, Optional, Union

import httpx
import google.auth.transport.requests

try:
    import vertexai
except ImportError:  # pragma: no cover - optional dependency
    vertexai = None

from utils.config import get_settings
from utils.google_utils import get_credentials
from utils.prompts import DELTA_SYSTEM_PROMPT, EDUCATIONAL_GUIDE_PROMPT
from ..llm_providers import get_llm_provider
from ..tools_definition import get_tools_config

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self._vertex_ready = False
        self._provider = None

    @property
    def vertex_ready(self) -> bool:
        return self._vertex_ready

    def init_vertex(self) -> bool:
        settings = get_settings()
        if not vertexai:
            logger.warning("vertexai is not installed. Vertex AI init skipped.")
            self._vertex_ready = False
            return False

        try:
            creds = get_credentials()
            if creds:
                vertexai.init(
                    project=settings.project_id,
                    location=settings.location,
                    credentials=creds,
                )
                logger.info("Vertex AI initialized with project %s", settings.project_id)
                self._vertex_ready = True
                return True
            logger.warning("No Google credentials found for Vertex AI.")
            self._vertex_ready = False
            return False
        except Exception as exc:
            logger.error("Vertex AI init failed: %s", exc)
            self._vertex_ready = False
            return False

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

        # Tools omitted for simplified stateless mode
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
