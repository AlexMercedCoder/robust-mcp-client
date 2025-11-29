import asyncio
import os
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from core.config import settings, MCPServerConfig

class MCPClientManager:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()

    async def connect_all(self):
        for server_config in settings.MCP_SERVERS:
            await self.connect(server_config)

    async def connect(self, config: MCPServerConfig):
        try:
            # Currently only supporting Stdio for local servers as per common use case
            # TODO: Add SSE support for remote servers
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env={**os.environ, **config.env}
            )
            
            # We need to maintain the connection context
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            await session.initialize()
            self.sessions[config.name] = session
            print(f"Connected to MCP server: {config.name}")
            
        except Exception as e:
            print(f"Failed to connect to MCP server {config.name}: {e}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                for tool in result.tools:
                    tool_dict = tool.model_dump()
                    tool_dict["server"] = name
                    all_tools.append(tool_dict)
            except Exception as e:
                print(f"Error listing tools for {name}: {e}")
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if server_name not in self.sessions:
            raise ValueError(f"Server {server_name} not found")
        
        session = self.sessions[server_name]
        result = await session.call_tool(tool_name, arguments)
        return result

    async def cleanup(self):
        await self.exit_stack.aclose()
