# Configuration Guide

The Robust MCP Client can be configured via Environment Variables and a JSON configuration file for MCP servers.

## Environment Variables (`.env`)

Create a `.env` file in the root directory to set API keys and preferences.

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_LLM_PROVIDER` | The default LLM to use (`local`, `openai`, `gemini`, `anthropic`). | `local` |
| `OPENAI_API_KEY` | API Key for OpenAI. | `None` |
| `GEMINI_API_KEY` | API Key for Google Gemini. | `None` |
| `ANTHROPIC_API_KEY` | API Key for Anthropic Claude. | `None` |
| `LOCAL_MODEL_PATH` | Path to the local GGUF model file. | `models/tinyllama...` |
| `DEBUG` | Enable debug logging. | `False` |

## MCP Configuration (`mcp.json`)

The `mcp.json` file defines the MCP servers that the client should connect to. It follows the standard MCP configuration format.

### Example `mcp.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/files"]
    },
    "remote-server": {
      "transport": "sse",
      "url": "http://localhost:3000/sse",
      "headers": {
        "Authorization": "Bearer my-token"
      }
    }
  }
}
```

- **transport**: `stdio` (default) or `sse`.
- **command**: The executable to run (for `stdio`).
- **args**: List of arguments (for `stdio`).
- **url**: The URL of the SSE endpoint (for `sse`).
- **headers**: (Optional) Dictionary of headers (e.g., for Auth) (for `sse`).
- **env**: (Optional) Dictionary of environment variables.

## Runtime Configuration

You can also update the configuration at runtime via the Web UI **Settings** page. Note that runtime changes to API keys might not persist across server restarts unless you update the `.env` file manually.
