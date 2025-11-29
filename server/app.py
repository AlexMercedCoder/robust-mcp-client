import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from core.config import settings, MCPServerConfig
from core.chat_engine import ChatEngine
from core.llm.base import BaseLLM
from core.llm.local import LocalLLM
from core.llm.cloud import OpenAILLM, GeminiLLM, AnthropicLLM
from core.mcp.client import MCPClientManager
from core.memory.manager import MemoryManager

# Global State
class GlobalState:
    llm: Optional[BaseLLM] = None
    mcp: Optional[MCPClientManager] = None

state = GlobalState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MCP
    state.mcp = MCPClientManager()
    await state.mcp.connect_all()
    
    # Initialize LLM
    if settings.DEFAULT_LLM_PROVIDER == "openai":
        state.llm = OpenAILLM()
    elif settings.DEFAULT_LLM_PROVIDER == "gemini":
        state.llm = GeminiLLM()
    elif settings.DEFAULT_LLM_PROVIDER == "anthropic":
        state.llm = AnthropicLLM()
    else:
        state.llm = LocalLLM()
        
    yield
    
    # Cleanup
    if state.mcp:
        await state.mcp.cleanup()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

from core.config import settings, MCPServerConfig

class ConfigUpdate(BaseModel):
    llm_provider: Optional[str] = None
    openai_key: Optional[str] = None
    gemini_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    engine = ChatEngine(
        conversation_id=request.conversation_id,
        llm=state.llm,
        mcp=state.mcp
    )
    await engine.initialize() # Ensures memory is ready
    
    async def generate():
        async for chunk in engine.chat(request.message):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/api/conversations")
async def list_conversations():
    memory = MemoryManager()
    return await memory.list_conversations()

@app.post("/api/conversations")
async def create_conversation(title: str = Body(..., embed=True)):
    memory = MemoryManager()
    id = await memory.create_conversation(title)
    return {"id": id, "title": title}

@app.get("/api/history/{conversation_id}")
async def get_history(conversation_id: int):
    memory = MemoryManager()
    return await memory.get_messages(conversation_id)

@app.get("/api/config")
async def get_config():
    return {
        "provider": settings.DEFAULT_LLM_PROVIDER,
        "mcp_servers": [
            {
                "name": s.name, 
                "transport": s.transport, 
                "command": s.command, 
                "args": s.args, 
                "url": s.url
            } 
            for s in settings.MCP_SERVERS
        ]
    }

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    # This is a runtime update, ideally we should persist to .env
    # For now we just update the settings object and re-init LLM if needed
    
    if config.llm_provider:
        settings.DEFAULT_LLM_PROVIDER = config.llm_provider
        
        # Re-init LLM
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            state.llm = OpenAILLM(api_key=config.openai_key)
        elif settings.DEFAULT_LLM_PROVIDER == "gemini":
            state.llm = GeminiLLM(api_key=config.gemini_key)
        elif settings.DEFAULT_LLM_PROVIDER == "anthropic":
            state.llm = AnthropicLLM(api_key=config.anthropic_key)
        else:
            state.llm = LocalLLM()
            
    if config.mcp_servers is not None:
        # Update MCP servers
        new_servers = []
        for s in config.mcp_servers:
            new_servers.append(MCPServerConfig(
                name=s["name"],
                transport=s.get("transport", "stdio"),
                command=s.get("command"),
                args=s.get("args", []),
                env=s.get("env", {}),
                url=s.get("url")
            ))
        settings.MCP_SERVERS = new_servers
        
        # Re-connect MCP
        if state.mcp:
            await state.mcp.cleanup()
        state.mcp = MCPClientManager()
        await state.mcp.connect_all()
            
    return {"status": "updated"}

# Serve Static Files (UI)
# Ensure ui/dist exists or handle it gracefully
if os.path.exists("ui/dist"):
    app.mount("/assets", StaticFiles(directory="ui/dist/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API routes are already handled above because they are defined first
        # If it's a file in dist, serve it
        if os.path.exists(f"ui/dist/{full_path}") and full_path != "":
            return FileResponse(f"ui/dist/{full_path}")
        # Otherwise serve index.html for SPA routing
        return FileResponse("ui/dist/index.html")
