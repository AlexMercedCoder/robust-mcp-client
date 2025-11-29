# API Reference

The backend exposes a REST API built with FastAPI.

## Endpoints

### Chat

#### `POST /api/chat`
Sends a message to the AI and receives a streaming response.

**Request Body**:
```json
{
  "message": "Hello, how are you?",
  "conversation_id": 1  // Optional
}
```

**Response**:
- Content-Type: `text/plain` (Streaming)
- The response body contains the AI's reply chunks.

### History

#### `GET /api/conversations`
List all conversations.

**Response**:
```json
[
  {
    "id": 1,
    "title": "Hello world",
    "created_at": "2023-10-27T10:00:00"
  }
]
```

#### `POST /api/conversations`
Create a new conversation.

**Request Body**:
```json
{
  "title": "New Chat"
}
```

#### `GET /api/history/{conversation_id}`
Get messages for a specific conversation.

**Response**:
```json
[
  {
    "role": "user",
    "content": "Hi"
  },
  {
    "role": "assistant",
    "content": "Hello!"
  }
]
```

### Configuration

#### `GET /api/config`
Get current configuration (provider and active servers).

#### `POST /api/config`
Update configuration.

**Request Body**:
```json
{
  "llm_provider": "openai",
  "openai_key": "sk-..."
}
```
