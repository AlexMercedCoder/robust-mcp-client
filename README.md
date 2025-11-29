# Robust MCP Client

A versatile Chat Client that supports the Model Context Protocol (MCP), works via CLI and Web UI, and integrates with both local and cloud LLMs.

## Features
- **Dual Interface**: CLI and Web UI (React + Tailwind).
- **Local LLM**: Built-in support for `llama-cpp-python` (auto-downloads TinyLlama).
- **Cloud LLM**: Support for OpenAI, Gemini, and Claude.
- **MCP Support**: Connect to multiple MCP servers via `mcp.json`.
- **Memory**: Persistent conversation history (SQLite).
- **Rich UI**: Streaming responses, Markdown, Code Highlighting, Mermaid Diagrams.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   cd ui && npm install
   ```

2. **Configuration**:
   - Create a `.env` file (optional) for API keys:
     ```
     OPENAI_API_KEY=...
     GEMINI_API_KEY=...
     ANTHROPIC_API_KEY=...
     ```
   - Edit `mcp.json` to add MCP servers.

## Usage

### CLI
Run the chat interface in the terminal:
```bash
python -m cli.main chat
```

### Web UI
1. Start the backend server:
   ```bash
   python -m cli.main serve
   ```
2. Start the frontend (in a separate terminal):
   ```bash
   cd ui
   npm run dev
   ```
3. Open http://localhost:5173

### Docker

#### Quick Start (Ephemeral)
To try it out quickly without persisting data:
```bash
docker run -p 8000:8000 alexmerced/robust_mcp_client
```
*Note: Models will be re-downloaded and chat history lost when the container stops.*

#### Using Pre-built Image (Persistent)
To persist models and history:

```bash
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/history.db:/app/history.db \
  alexmerced/robust_mcp_client
```

#### Building Locally
You can also build the image yourself:

1. **Build the image**:
   ```bash
   docker build -t robust-mcp-client .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 \
     -v $(pwd)/models:/app/models \
     -v $(pwd)/history.db:/app/history.db \
     robust-mcp-client
   ```
   - `-p 8000:8000`: Expose the server port.
   - `-v .../models`: Persist downloaded models.
   - `-v .../history.db`: Persist conversation history.

3. **Access the UI**:
   Open http://localhost:8000

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Development](docs/development.md)
- [Usage](docs/usage.md)
- [API Reference](docs/api.md)

## Development
- Run tests: `python -m pytest tests/`
