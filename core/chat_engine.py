import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from core.config import settings
from core.llm.base import BaseLLM
from core.llm.local import LocalLLM
from core.llm.cloud import OpenAILLM, GeminiLLM, AnthropicLLM
from core.memory.manager import MemoryManager
from core.mcp.client import MCPClientManager

class ChatEngine:
    def __init__(self, conversation_id: Optional[int] = None, llm: Optional[BaseLLM] = None, mcp: Optional[MCPClientManager] = None):
        self.memory = MemoryManager()
        self.mcp = mcp or MCPClientManager()
        self.llm = llm
        self.conversation_id = conversation_id

    async def initialize(self):
        await self.memory.init_db()
        if not self.mcp.sessions: # Only connect if not already connected (naive check)
            await self.mcp.connect_all()
        
        # Initialize LLM based on settings if not provided
        if not self.llm:
            if settings.DEFAULT_LLM_PROVIDER == "openai":
                self.llm = OpenAILLM()
            elif settings.DEFAULT_LLM_PROVIDER == "gemini":
                self.llm = GeminiLLM()
            elif settings.DEFAULT_LLM_PROVIDER == "anthropic":
                self.llm = AnthropicLLM()
            else:
                self.llm = LocalLLM()

        if self.conversation_id is None:
            self.conversation_id = await self.memory.create_conversation()

    async def chat(self, message: str) -> AsyncGenerator[str, None]:
        if not self.llm:
            await self.initialize()

        # Add user message to memory
        await self.memory.add_message(self.conversation_id, "user", message)

        # Get history
        history = await self.memory.get_messages(self.conversation_id)
        
        # Get tools (for system prompt or function calling)
        tools = await self.mcp.list_tools()
        
        # Construct system prompt with tools info
        # This is a naive implementation for local LLMs. 
        # Advanced models would use native tool calling.
        system_prompt = "You are a helpful AI assistant."
        if tools:
            tools_json = json.dumps(tools, indent=2)
            system_prompt += f"\n\nAvailable Tools:\n{tools_json}\n\nTo use a tool, output a JSON block like:\n```json\n{{\"tool\": \"tool_name\", \"server\": \"server_name\", \"arguments\": {{...}}}}\n```"

        # Stream response
        full_response = ""
        async for chunk in self.llm.chat_stream(history, system_prompt=system_prompt):
            full_response += chunk
            yield chunk

        # Add assistant response to memory
        await self.memory.add_message(self.conversation_id, "assistant", full_response)
        
        # TODO: Parse response for tool calls and execute them (ReAct loop)
        # For this MVP step, we just return the response.
        
    async def cleanup(self):
        await self.mcp.cleanup()
