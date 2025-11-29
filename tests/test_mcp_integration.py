import pytest
import asyncio
import httpx
import subprocess
import time
import os
import sys
from uvicorn import Config, Server

# Helper to start HTTP MCP server
@pytest.fixture(scope="module")
async def http_mcp_server():
    # Start the dummy HTTP server
    process = subprocess.Popen(
        [sys.executable, "tests/mcp_servers/http_server.py"],
        env={**os.environ, "PORT": "8001"}, # FastMCP uses PORT env var or default 8000? FastMCP run uses uvicorn. 
        # FastMCP.run() defaults to 8000. We need to make sure it doesn't conflict.
        # Let's check how to configure port for FastMCP.run(). It uses uvicorn.run.
        # We might need to pass arguments if FastMCP supports it, or set env vars.
        # Assuming FastMCP respects PORT or we can pass it. 
        # Actually, let's just run it and see. If it defaults to 8000, it conflicts with main app.
        # We should modify http_server.py to accept port or use a different default.
    )
    # Wait for it to start
    time.sleep(2)
    yield "http://localhost:8000/sse" # FastMCP default
    process.terminate()
    process.wait()

# Actually, let's modify http_server.py to run on 8001 to avoid conflict
# For now, let's assume we can run the main app on 8002 for testing.

@pytest.mark.asyncio
async def test_mcp_integration():
    # 1. Start Dummy HTTP Server on 8001
    http_server_process = subprocess.Popen(
        [sys.executable, "tests/mcp_servers/http_server.py", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait a bit
    await asyncio.sleep(2)
    
    # 2. Start Main App on 8002
    # We can use TestClient, but we want to test the full flow including MCP connection which might involve background tasks.
    # However, TestClient with AsyncClient is usually fine.
    
    from server.app import app
    from core.config import settings
    
    # Reset settings
    settings.MCP_SERVERS = []
    
    from httpx import ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 3. Add Stdio Server via API
        stdio_config = {
            "mcp_servers": [
                {
                    "name": "dummy-stdio",
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["tests/mcp_servers/stdio_server.py"]
                }
            ]
        }
        response = await client.post("/api/config", json=stdio_config)
        assert response.status_code == 200
        
        # 4. Verify Stdio Tools
        # We need an endpoint to list tools or check if they are loaded.
        # The chat endpoint uses them.
        # Let's check /api/config to see if it's listed
        response = await client.get("/api/config")
        data = response.json()
        assert len(data["mcp_servers"]) == 1
        assert data["mcp_servers"][0]["name"] == "dummy-stdio"
        
        # 5. Add HTTP Server via API
        # Note: FastMCP default might be 8000. We need to ensure http_server.py runs on 8001.
        # We'll need to modify http_server.py to accept port arg or use hardcoded 8001.
        
        http_config = {
            "mcp_servers": [
                {
                    "name": "dummy-stdio",
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["tests/mcp_servers/stdio_server.py"]
                },
                {
                    "name": "dummy-http",
                    "transport": "sse",
                    "url": "http://localhost:8001/sse"
                }
            ]
        }
        # We need to make sure http server is running on 8001.
        # See step 1.
        
        response = await client.post("/api/config", json=http_config)
        assert response.status_code == 200
        
        # 6. Verify Both Servers
        response = await client.get("/api/config")
        data = response.json()
        assert len(data["mcp_servers"]) == 2
    
    http_server_process.terminate()
