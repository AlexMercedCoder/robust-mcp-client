from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional

class BaseLLM(ABC):
    @abstractmethod
    async def chat_complete(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        """
        Get a complete response from the LLM.
        """
        pass

    @abstractmethod
    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Stream the response from the LLM.
        """
        pass
