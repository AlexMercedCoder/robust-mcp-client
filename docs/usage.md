# Usage Guide

## Web UI

The Web UI provides a rich chat experience with support for markdown, code highlighting, and diagrams.

### Starting the UI
1. Ensure the server is running (via Docker or Python).
2. Open your browser to `http://localhost:8000`.

### Features
- **Chat**: Type your message in the input box. The AI will stream the response.
- **Tools**: If configured in `mcp.json`, the AI can use tools to fetch information or perform actions.
- **Settings**: Click the "Settings" button in the sidebar to:
  - Change the LLM Provider (Local, OpenAI, Gemini, Claude).
  - Enter API Keys.
  - Manage MCP Servers (Add/Remove Stdio or HTTP servers).
- **History**: Previous conversations are saved in the sidebar. Click to load them.
- **Dark Mode**: Toggle the sun/moon icon in the header.

## CLI

The CLI is a lightweight alternative for terminal users.

### Commands
- **Start Chat**:
  ```bash
  python -m cli.main chat
  ```
- **Start Server**:
  ```bash
  python -m cli.main serve
  ```

### CLI Features
- Streaming responses.
- Markdown rendering (tables, lists, code blocks).
- Persistent history (shared with the UI).

## Docker

See the [README](../README.md#docker) for Docker usage instructions.
