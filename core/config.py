import os
import json
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class MCPServerConfig(BaseSettings):
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}

class Settings(BaseSettings):
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "local" # local, openai, gemini, anthropic
    
    # Local LLM
    LOCAL_MODEL_PATH: str = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    LOCAL_MODEL_REPO: str = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    LOCAL_MODEL_FILENAME: str = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    
    # Cloud Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # MCP Configuration
    MCP_SERVERS: List[MCPServerConfig] = []
    
    # App Config
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def load_mcp_config(self, path: str = "mcp.json"):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    servers = data.get("mcpServers", {})
                    for name, config in servers.items():
                        self.MCP_SERVERS.append(MCPServerConfig(
                            name=name,
                            command=config.get("command"),
                            args=config.get("args", []),
                            env=config.get("env", {})
                        ))
            except Exception as e:
                print(f"Error loading mcp.json: {e}")

settings = Settings()
settings.load_mcp_config()
