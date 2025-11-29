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
    "git": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/repo:/repo", "mcp/git"]
    }
  }
}
```

- **command**: The executable to run (e.g., `npx`, `python`, `docker`).
- **args**: List of arguments to pass to the command.
- **env**: (Optional) Dictionary of environment variables for the server process.

## Runtime Configuration

You can also update the configuration at runtime via the Web UI **Settings** page. Note that runtime changes to API keys might not persist across server restarts unless you update the `.env` file manually.
