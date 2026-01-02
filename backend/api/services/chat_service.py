import logging
from typing import List, Dict, Any, Union, Optional, Tuple
from .llm_service import get_llm_service

log = logging.getLogger(__name__)

class ChatService:
    def __init__(self, llm_service=None):
        from .llm_service import get_llm_service
        self.llm_service = llm_service or get_llm_service()

    async def process_user_input(
        self,
        db: Optional[Any], 
        user_input: str, 
        conversation_id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        # Stateless mode: no history, no persistence
        llm_response = await self.llm_service.generate_response(user_input, history=[])
        
        if isinstance(llm_response, dict):
            return llm_response.get("text", "Task acknowledged."), None
        return str(llm_response), None

    async def process_user_input_stream(self, db: Optional[Any], user_input: str, conversation_id: int):
        log.info("Starting stateless stream for conversation %s", conversation_id)
        
        full_response = ""
        log.info("Requesting LLM stream for input: %s", user_input[:50] + "..." if len(user_input) > 50 else user_input)
        try:
            # We use an explicit history=[] for now to maintain statelessness
            async for chunk in self.llm_service.generate_stream(user_input, history=[]):
                if chunk:
                    log.debug("Received chunk: %s", repr(chunk))
                    full_response += chunk
                    # Split by newline and append literal \n to keep them through the stream
                    lines = chunk.split('\n')
                    for i, line in enumerate(lines):
                        nl = '\\n' if i < len(lines) - 1 else ''
                        yield f"data: {line}{nl}\n\n"
            
            log.info("Stream completed successfully for conversation %s", conversation_id)
        except Exception as e:
            log.error("LLM Stream Error: %s", e, exc_info=True)
            yield f"data: Error: LLM stream failed - {str(e)}\n\n"
            return

    async def get_conversation_summary(self, db: Optional[Any], conversation_id: int) -> Optional[str]:
        return "Stateless summary unavailable."

_SERVICE: Optional[ChatService] = None

def get_chat_service() -> ChatService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = ChatService()
    return _SERVICE
