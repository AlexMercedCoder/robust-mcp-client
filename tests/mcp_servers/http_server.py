from mcp.server.fastmcp import FastMCP
import uvicorn

mcp = FastMCP("dummy-http")

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

if __name__ == "__main__":
    import uvicorn
    mcp.run(transport="sse") # FastMCP doesn't easily expose port in run() without args?
    # Actually FastMCP.run() uses uvicorn.run(). 
    # Let's use uvicorn directly to control port if FastMCP exposes the app.
    # mcp._sse_app is the Starlette app.
    # But mcp.run() does a lot of setup.
    # Let's check FastMCP source or docs? 
    # For now, let's try passing arguments to mcp.run if it supports it, or just use `uvicorn.run(mcp._sse_app, port=8001)` if accessible.
    # Better yet, let's just use `mcp.run(transport="sse", port=8001)` and hope it works (it likely passes kwargs to uvicorn).
    mcp.run(transport="sse", port=8001)
