import pytest
import os
from core.config import settings, MCPServerConfig
from core.mcp.client import MCPClientManager

@pytest.mark.asyncio
async def test_config_parsing():
    # Test Stdio config
    c1 = MCPServerConfig(name="test1", command="echo", args=["hello"])
    assert c1.transport == "stdio"
    assert c1.command == "echo"
    
    # Test SSE config
    c2 = MCPServerConfig(name="test2", transport="sse", url="http://localhost:3000", headers={"Authorization": "Bearer token"})
    assert c2.transport == "sse"
    assert c2.url == "http://localhost:3000"
    assert c2.headers == {"Authorization": "Bearer token"}

@pytest.mark.asyncio
async def test_mcp_client_connection_logic():
    # We can't easily test actual connection without running servers, 
    # but we can test that it attempts to use the right client based on config.
    # For now, we'll just verify the config object is passed correctly.
    
    manager = MCPClientManager()
    # This is more of a sanity check that the class loads and methods exist
    assert hasattr(manager, "connect")
    assert hasattr(manager, "connect_all")
