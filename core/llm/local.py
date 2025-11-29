import os
import sys
import requests
from typing import AsyncGenerator, List, Dict, Optional
from tqdm import tqdm
from llama_cpp import Llama
from core.config import settings
from core.llm.base import BaseLLM

class LocalLLM(BaseLLM):
    def __init__(self):
        self.model_path = settings.LOCAL_MODEL_PATH
        self._ensure_model_exists()
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_threads=os.cpu_count(),
            verbose=settings.DEBUG
        )

    def _ensure_model_exists(self):
        if os.path.exists(self.model_path):
            return

        print(f"Model not found at {self.model_path}. Downloading...")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        url = f"https://huggingface.co/{settings.LOCAL_MODEL_REPO}/resolve/main/{settings.LOCAL_MODEL_FILENAME}"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(self.model_path, "wb") as f, tqdm(
            desc=settings.LOCAL_MODEL_FILENAME,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
        
        print("Model downloaded successfully.")

    async def chat_complete(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        # Convert messages to llama-cpp format if needed, but it supports OpenAI format mostly
        # We might need to handle system prompt if it's not in messages
        msgs = messages.copy()
        if system_prompt:
            msgs.insert(0, {"role": "system", "content": system_prompt})

        response = self.llm.create_chat_completion(
            messages=msgs,
            stream=False
        )
        return response["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        msgs = messages.copy()
        if system_prompt:
            msgs.insert(0, {"role": "system", "content": system_prompt})

        stream = self.llm.create_chat_completion(
            messages=msgs,
            stream=True
        )
        
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
