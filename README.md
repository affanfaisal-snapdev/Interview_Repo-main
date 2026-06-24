# AI Chatbot Backend System

A production-grade backend chatbot system built with FastAPI, LangGraph, and Google's Gemini API. Demonstrates enterprise-level architecture, best practices, and scalability patterns.

## Overview

This system provides a modern, scalable backend for AI-powered chatbot applications with:

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **LangGraph**: Graph-based workflow orchestration for agent systems
- **Gemini REST API**: Direct integration with Google's latest language models
- **SQLAlchemy 2.0**: Modern ORM with type hints and SQLite persistence
- **Production-Ready**: Docker support, comprehensive logging, error handling, security middleware

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  API Routers     │        │  Security &      │          │
│  │  - Sessions      │        │  Middleware      │          │
│  │  - Chat          │        │  - CORS           │          │
│  └────────┬─────────┘        │  - Auth (stub)    │          │
│           │                  └──────────────────┘          │
│           ▼                                                 │
│  ┌──────────────────────────────────────┐                  │
│  │        Service Layer                 │                  │
│  │  ┌──────────────┐  ┌──────────────┐ │                  │
│  │  │ ChatService  │  │LangGraphSvc  │ │                  │
│  │  └──────┬───────┘  └──────┬───────┘ │                  │
│  └─────────┼──────────────────┼────────┘                  │
│            │                  │                            │
│            ▼                  ▼                            │
│  ┌──────────────────────────────────────┐                  │
│  │     LangGraph Workflow                │                  │
│  │  ┌──────────────────────────────┐   │                  │
│  │  │  Graph Nodes:                │   │                  │
│  │  │  1. process_input            │   │                  │
│  │  │  2. call_gemini (REST API)   │   │                  │
│  │  │  3. format_output            │   │                  │
│  │  └──────────────────────────────┘   │                  │
│  └──────────────┬───────────────────────┘                  │
│                 │                                          │
│                 ▼                                          │
│  ┌──────────────────────────────────────┐                  │
│  │     External Services                 │                  │
│  │  ┌──────────────┐  ┌──────────────┐ │                  │
│  │  │ Gemini API   │  │ SQLite DB    │ │                  │
│  │  │ (REST)       │  │              │ │                  │
│  │  └──────────────┘  └──────────────┘ │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Create Session**: POST `/api/v1/sessions` → Returns `session_id`
2. **Send Message**:
   - POST `/api/v1/chat/message` with `session_id` and `message`
   - Service validates session
   - User message stored in DB
   - LangGraph workflow executed:
     - Process input (validation)
     - Call Gemini REST API
     - Format output
   - Assistant response stored in DB
   - Full conversation history returned

### Database Schema

```sql
-- Sessions Table
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Messages Table
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL FOREIGN KEY,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    INDEX ix_messages_session_id (session_id),
    INDEX ix_messages_created_at (created_at),
    INDEX ix_messages_session_created (session_id, created_at)
);
```

## Project Structure

```
.
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── routers/
│   │       ├── sessions.py     # Session endpoints
│   │       └── chat.py         # Chat endpoints
│   ├── core/
│   │   ├── config.py           # Configuration & settings
│   │   └── logging.py          # Structured logging
│   ├── db/
│   │   ├── base.py             # Database setup & engine
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── session.py          # Repository classes
│   ├── schemas/
│   │   ├── session.py          # Pydantic schemas for sessions
│   │   └── message.py          # Pydantic schemas for messages
│   ├── services/
│   │   ├── chat.py             # Chat business logic
│   │   ├── gemini_client.py    # Gemini REST API client
│   │   └── langgraph_service.py # LangGraph orchestration
│   ├── langgraph/
│   │   ├── graph.py            # Graph definition
│   │   └── nodes.py            # Node implementations
│   └── tests/
│       ├── conftest.py         # Pytest fixtures
│       ├── test_sessions.py    # Session endpoint tests
│       └── test_chat.py        # Chat endpoint tests
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── alembic.ini                 # Database migration config
└── README.md                   # This file
```

## Installation & Setup

### Prerequisites

- Python 3.11+
- pip or uv
- Docker & Docker Compose (optional)
- Gemini API Key (from [Google AI Studio](https://aistudio.google.com/apikey))

### Local Setup

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd chatbot-backend
   ```

2. **Create Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Gemini API key
   export GEMINI_API_KEY="your-api-key-here"
   ```

5. **Run application**
   ```bash
   uvicorn app.main:app --reload
   ```

   Application runs at `http://localhost:8000`

6. **View API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f chatbot
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## API Usage Examples

### 1. Create a Chat Session

```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-12T10:00:00"
}
```

### 2. Get Session Information

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-12T10:00:00",
  "message_count": 2
}
```

### 3. Send a Chat Message

```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "What is the capital of France?"
  }'
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_message": "What is the capital of France?",
  "assistant_message": "The capital of France is Paris. It is the largest city in France and serves as the political, cultural, and economic center of the country.",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is the capital of France?",
      "created_at": "2026-02-12T10:00:00"
    },
    {
      "role": "assistant",
      "content": "The capital of France is Paris...",
      "created_at": "2026-02-12T10:00:01"
    }
  ]
}
```

### 4. Continue Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Tell me about its history"
  }'
```

The full conversation history is maintained and sent to the Gemini API for context-aware responses.

## Testing

### Run Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_sessions.py -v

# Run specific test
pytest app/tests/test_sessions.py::test_create_session -v
```

### Test Coverage

- Session creation and retrieval
- Chat message sending
- Conversation history maintenance
- Error handling
- Input validation

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment: `development` or `production` |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DATABASE_URL` | `sqlite:///./chatbot.db` | Database connection string |
| `GEMINI_API_KEY` | `` | Google Gemini API key (required) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `GEMINI_TEMPERATURE` | `0.7` | Temperature for generation (0.0-2.0) |
| `GEMINI_MAX_OUTPUT_TOKENS` | `2048` | Max output tokens |
| `GEMINI_TOP_P` | `1.0` | Top-P nucleus sampling |
| `GEMINI_TOP_K` | `64` | Top-K sampling |

### Application Settings

Modify `app/core/config.py` for:
- CORS origins
- Rate limiting
- Session timeouts
- API retry policies
- Security settings

## LangGraph Workflow

### Graph Structure

The chat graph follows a linear pipeline:

```
START → process_input → call_gemini → format_output → END
```

### Node Details

1. **process_input_node**
   - Validates message format
   - Checks conversation state
   - Prepares data for Gemini call

2. **call_gemini_node**
   - Executes Gemini REST API call
   - Manages conversation history
   - Handles API errors gracefully
   - Returns formatted response

3. **format_output_node**
   - Ensures response format consistency
   - Validates output structure
   - Prepares for database storage

### Extending the Graph

To add new capabilities:

1. Define new node in `app/langgraph/nodes.py`:
   ```python
   def new_node(state: dict[str, Any]) -> dict[str, Any]:
       # Processing logic
       return updated_state
   ```

2. Add to graph in `app/langgraph/graph.py`:
   ```python
   graph_builder.add_node("new_node", nodes.new_node)
   graph_builder.add_edge("call_gemini", "new_node")
   graph_builder.add_edge("new_node", "format_output")
   ```

## Gemini API Integration

### REST API Details

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- **Authentication**: `x-goog-api-key` header
- **Model**: `gemini-2.5-flash` (default)
- **Timeout**: 30 seconds
- **Retries**: 3 attempts on failure

### Request/Response Cycle

**Request Body Structure:**
```json
{
  "contents": [
    {
      "role": "user|model",
      "parts": [{"text": "message"}]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 2048
  },
  "safetySettings": [...]
}
```

**Response Structure:**
```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [{"text": "response"}]
      },
      "finishReason": "STOP",
      "safetyRatings": [...]
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 100,
    "candidatesTokenCount": 50,
    "totalTokenCount": 150
  }
}
```

## Performance & Scalability

### Optimization Strategies

1. **Database Indexes**: Messages indexed by session and creation time
2. **Connection Pooling**: SQLAlchemy session management
3. **Async/Await**: Full async support for I/O operations
4. **Caching**: Message history loaded once per request
5. **Timeouts**: 30-second timeout for external API calls

### Scaling Considerations

- **Horizontal**: Deploy multiple instances behind load balancer
- **Database**: Replace SQLite with PostgreSQL for production
- **Caching**: Add Redis for session/conversation caching
- **Message Queue**: Use Celery for async task processing
- **Monitoring**: Integrate with LangSmith for tracing

## Security Features

1. **CORS Middleware**: Configurable allowed origins
2. **Trusted Host**: Host header validation
3. **Input Validation**: Pydantic schema validation
4. **Error Handling**: Sanitized error responses
5. **Structured Logging**: Audit trail of operations
6. **Environment Variables**: Sensitive data in .env

### Future Security Enhancements

- API key authentication
- Rate limiting (placeholders present)
- Request signing
- HTTPS enforcement
- Database encryption
- User authentication & authorization

## Monitoring & Debugging

### Logging

Structured logs with timestamps and context:

```
2026-02-12 10:00:01 - app.services.chat - INFO - Processing message for session: 550e8400...
2026-02-12 10:00:02 - app.langgraph.nodes - INFO - Executing call_gemini_node
2026-02-12 10:00:03 - app.services.gemini_client - INFO - Successfully generated response from Gemini
```

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
export LANGGRAPH_DEBUG=true
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

## Database Migrations

### Setting Up Alembic

```bash
# Initialize Alembic (already done in this repo)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# View migration history
alembic current
alembic history
```

### Custom Migrations

```bash
# Create new migration
alembic revision -m "Add new column"

# Edit alembic/versions/{timestamp}_*.py

# Apply
alembic upgrade head
```

## Future Enhancements

### Planned Features

- [ ] User authentication & authorization
- [ ] Multi-user sessions with access control
- [ ] Conversation export (PDF, JSON)
- [ ] Message editing and deletion
- [ ] Conversation search & filtering
- [ ] Streaming responses
- [ ] Custom system prompts per session
- [ ] Token counting & cost estimation
- [ ] Conversation analytics
- [ ] Admin dashboard

### Advanced Capabilities

- [ ] Tool/function calling integration
- [ ] File upload & processing
- [ ] Image understanding
- [ ] Long context support (millions of tokens)
- [ ] Context caching for cost optimization
- [ ] Multi-modal input (images, documents)
- [ ] Voice integration
- [ ] Real-time collaboration

### Integration Opportunities

- [ ] LangSmith for tracing & evaluation
- [ ] LangServe for agent deployment
- [ ] OpenAI compatibility layer
- [ ] Structured output (JSON schemas)
- [ ] Agent frameworks (ReAct, etc.)
- [ ] Memory systems (short/long term)
- [ ] Persistent vector database

## Troubleshooting

### Common Issues

**Issue**: `GEMINI_API_KEY not configured`
- **Solution**: Set `GEMINI_API_KEY` environment variable

**Issue**: `Session not found` (404)
- **Solution**: Ensure session was created first with POST `/api/v1/sessions`

**Issue**: `Database locked` (SQLite)
- **Solution**: Close other database connections; use PostgreSQL for production

**Issue**: Timeout calling Gemini API
- **Solution**: Increase `GEMINI_TIMEOUT_SECONDS` in config

**Issue**: Tests failing
- **Solution**: Run `pip install -r requirements.txt` and ensure pytest is installed

## Development

### Code Style

```bash
# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/

# Sort imports
isort app/
```

### Contributing

1. Create feature branch: `git checkout -b feature/feature-name`
2. Follow code style guidelines
3. Write tests for new functionality
4. Run test suite: `pytest`
5. Commit and push: `git push origin feature/feature-name`
6. Create pull request

## License

MIT License - See LICENSE file for details

## Support & Resources

- **API Documentation**: `http://localhost:8000/docs`
- **Google Gemini Docs**: https://ai.google.dev/
- **LangGraph Docs**: https://docs.langchain.com/oss/python/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

## Contact

For issues, questions, or contributions, please open an issue on the repository.

---

Built with ❤️ using FastAPI, LangGraph, and Google Gemini API
# Interview_Repo
# Interview_Repo
