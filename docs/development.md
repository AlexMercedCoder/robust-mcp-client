# Development Guide

This guide is for developers who want to contribute to the Robust MCP Client or build upon it.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **C++ Compiler** (for building `llama-cpp-python` if pre-built wheels are unavailable)

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd robust-mcp-client
   ```

2. **Install Python Dependencies**:
   It is recommended to use a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Install UI Dependencies**:
   ```bash
   cd ui
   npm install
   ```

## Running Locally

### Backend
Start the FastAPI server with hot-reload enabled:
```bash
# From root directory
python -m cli.main serve
```
The server will start at `http://0.0.0.0:8000`.

### Frontend
Start the Vite development server:
```bash
# From ui/ directory
npm run dev
```
The UI will be available at `http://localhost:5173`.

## Testing

### Unit Tests
Run the Python unit tests using `pytest`:
```bash
python -m pytest tests/
```

### Manual Verification
You can use the CLI to verify core functionality without the UI:
```bash
python -m cli.main chat
```

## Project Structure

- `core/`: Business logic (LLM, MCP, Memory).
- `server/`: FastAPI application.
- `cli/`: Typer CLI application.
- `ui/`: React frontend.
- `tests/`: Pytest tests.
