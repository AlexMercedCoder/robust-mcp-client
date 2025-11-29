import os
from typing import AsyncGenerator, List, Dict, Optional
from core.config import settings
from core.llm.base import BaseLLM

# OpenAI
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

# Gemini
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Anthropic
try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

class OpenAILLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API Key not found")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4o" # Default model

    async def chat_complete(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        msgs = messages.copy()
        if system_prompt:
            msgs.insert(0, {"role": "system", "content": system_prompt})
            
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=msgs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        msgs = messages.copy()
        if system_prompt:
            msgs.insert(0, {"role": "system", "content": system_prompt})
            
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=msgs,
            stream=True
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API Key not found")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _convert_messages(self, messages: List[Dict[str, str]]):
        history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        return history

    async def chat_complete(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        # Gemini handles system prompt differently, usually via config or just prepending
        # For simplicity, we'll prepend if needed or use system_instruction if available in newer SDKs
        # We'll just use the chat session
        history = self._convert_messages(messages[:-1])
        chat = self.model.start_chat(history=history)
        
        last_msg = messages[-1]["content"]
        if system_prompt:
            # Prepend system prompt to the last message or first message? 
            # Best to just assume it's part of context.
            pass 

        response = await chat.send_message_async(last_msg)
        return response.text

    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        history = self._convert_messages(messages[:-1])
        chat = self.model.start_chat(history=history)
        last_msg = messages[-1]["content"]
        
        response = await chat.send_message_async(last_msg, stream=True)
        async for chunk in response:
            yield chunk.text

class AnthropicLLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API Key not found")
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"

    async def chat_complete(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        kwargs = {}
        if system_prompt:
            kwargs["system"] = system_prompt
            
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=messages,
            **kwargs
        )
        return response.content[0].text

    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        kwargs = {}
        if system_prompt:
            kwargs["system"] = system_prompt

        async with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            messages=messages,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text
