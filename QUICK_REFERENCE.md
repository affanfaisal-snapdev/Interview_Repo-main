# Quick Reference Guide

## 🚀 Fast Start (5 minutes)

### Linux/Mac
```bash
# 1. Setup
bash setup.sh

# 2. Configure
export GEMINI_API_KEY="your-api-key"

# 3. Run
uvicorn app.main:app --reload

# 4. Visit
open http://localhost:8000/docs
```

### Windows
```cmd
# 1. Setup
setup.bat

# 2. Configure
set GEMINI_API_KEY=your-api-key

# 3. Run
uvicorn app.main:app --reload

# 4. Visit
http://localhost:8000/docs
```

### Docker
```bash
# 1. Build and run
export GEMINI_API_KEY="your-api-key"
docker-compose up

# 2. Visit
open http://localhost:8000/docs
```

---

## 📚 API Quick Reference

### Create Session
```bash
curl -X POST http://localhost:8000/api/v1/sessions
```

### Get Session
```bash
curl http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Hello!"
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 🧪 Testing Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest app/tests/test_sessions.py::test_create_session -v

# Run with output
pytest -s

# Stop on first failure
pytest -x
```

---

## 🔧 Configuration Quick Reference

### Environment Variables
```bash
# Required
GEMINI_API_KEY=sk_...

# Optional (defaults shown)
APP_ENV=development           # or 'production'
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
DATABASE_URL=sqlite:///./chatbot.db
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_OUTPUT_TOKENS=2048
```

### Common Changes
```python
# In app/core/config.py

# Change database
DATABASE_URL = "postgresql://user:pass@localhost/chatbot"

# Change model
GEMINI_MODEL = "gemini-3-flash"

# Change temperature (0-2, 0=deterministic)
GEMINI_TEMPERATURE = 0.5
```

---

## 📁 File Navigation Guide

| Want to... | Go to... |
|-----------|----------|
| Start app | `app/main.py` |
| Configure settings | `app/core/config.py` |
| View API endpoints | `app/api/routers/` |
| Add database models | `app/db/models.py` |
| Modify workflow | `app/langgraph/graph.py` |
| Update business logic | `app/services/chat.py` |
| Add tests | `app/tests/` |
| See all endpoints | Visit `http://localhost:8000/docs` |
| Update dependencies | `requirements.txt` |
| Deploy with Docker | `Dockerfile` + `docker-compose.yml` |

---

## 🔍 Code Exploration

### Understand the Flow
1. Request arrives at `app/api/routers/chat.py`
2. Service layer in `app/services/chat.py` validates
3. LangGraph workflow in `app/langgraph/graph.py` executes
4. Gemini client in `app/services/gemini_client.py` calls API
5. Response stored in database (`app/db/`)
6. Response returned to client

### Key Classes
```python
# Models
from app.db.models import SessionModel, MessageModel

# Schemas
from app.schemas.message import ChatRequest, ChatResponse

# Services
from app.services.chat import ChatService
from app.services.gemini_client import GeminiClient
from app.services.langgraph_service import LangGraphService

# Configuration
from app.core.config import settings
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `GEMINI_API_KEY not found` | Set environment variable or edit `.env` |
| `Database locked` | Restart app (SQLite limitation) |
| `Connection refused` | Ensure app is running with `uvicorn` |
| `404 on /api/v1/...` | Check router is registered in `main.py` |
| `500 on chat` | Check logs, ensure Gemini API key is valid |
| `Tests failing` | Run `pytest -v` to see details |

---

## 📊 Useful Commands

```bash
# Development
uvicorn app.main:app --reload              # Run with auto-reload
uvicorn app.main:app --reload --log-level debug  # Debug mode

# Testing
pytest                                      # Run all tests
pytest -v                                   # Verbose output
pytest --cov=app                           # With coverage
pytest -k "test_create_session"            # Specific tests

# Code Quality
black app/                                  # Format code
flake8 app/                                # Check style
mypy app/                                  # Type check
isort app/                                 # Sort imports

# Docker
docker-compose up                          # Start services
docker-compose down                        # Stop services
docker-compose logs -f                     # View logs
docker build -t chatbot .                  # Build image

# Database
python -c "from app.db.base import create_all_tables; create_all_tables()"

# Interactive Demo
python quickstart.py
```

---

## 🎯 Common Tasks

### Add New Endpoint
1. Create router function in `app/api/routers/`
2. Create schema in `app/schemas/`
3. Create service method in `app/services/`
4. Register in `app/main.py` with `app.include_router()`
5. Add tests in `app/tests/`

### Extend LangGraph
1. Add node function to `app/langgraph/nodes.py`
2. Add node to graph in `app/langgraph/graph.py`
3. Connect with `graph.add_node()` and `graph.add_edge()`
4. Test with `pytest`

### Change Database
1. Update `DATABASE_URL` in `.env` or `app/core/config.py`
2. For new models: edit `app/db/models.py`
3. Create Alembic migration: `alembic revision --autogenerate -m "..."`
4. Apply: `alembic upgrade head`

### Deploy to Production
1. Create `.env` with production values
2. Build Docker image: `docker build -t chatbot:latest .`
3. Set `APP_ENV=production`
4. Use Gunicorn: `gunicorn wsgi:app --workers 4`
5. Monitor logs and health endpoint

---

## 🌐 API Examples

### Python Client
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create session
session_resp = requests.post(f"{BASE_URL}/sessions")
session_id = session_resp.json()["session_id"]

# Send message
chat_resp = requests.post(
    f"{BASE_URL}/chat/message",
    json={
        "session_id": session_id,
        "message": "What is AI?"
    }
)
print(chat_resp.json()["assistant_message"])
```

### JavaScript Client
```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Create session
const sessionResp = await fetch(`${BASE_URL}/sessions`, {
  method: "POST"
});
const { session_id } = await sessionResp.json();

// Send message
const chatResp = await fetch(`${BASE_URL}/chat/message`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id,
    message: "What is AI?"
  })
});
const { assistant_message } = await chatResp.json();
console.log(assistant_message);
```

### CURL
```bash
# Create session
SESS=$(curl -s -X POST http://localhost:8000/api/v1/sessions | jq -r .session_id)

# Send message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESS\", \"message\": \"Hello\"}" | jq .
```

---

## 📈 Performance Tips

- Use `GEMINI_TEMPERATURE=0` for deterministic responses
- Increase `GEMINI_MAX_OUTPUT_TOKENS` only if needed
- Use connection pooling for database (automatic with SQLAlchemy)
- Enable caching for frequent queries
- Use load balancer with multiple workers
- Monitor with LangSmith integration

---

## 🔒 Security Checklist

- [ ] Set `APP_ENV=production`
- [ ] Use strong `GEMINI_API_KEY`
- [ ] Configure `CORS_ORIGINS` properly
- [ ] Use HTTPS in production
- [ ] Keep dependencies updated
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable rate limiting
- [ ] Add authentication/authorization
- [ ] Regular backups
- [ ] Monitor logs for anomalies

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Comprehensive guide (1000+ lines) |
| `GENERATION_SUMMARY.md` | Project overview |
| `FILE_LISTING.md` | Complete file listing |
| `QUICK_REFERENCE.md` | This file |

---

## 🆘 Getting Help

1. **API Docs**: Visit `http://localhost:8000/docs` (interactive)
2. **Code Docs**: Read docstrings in files
3. **Tests**: Look at `app/tests/` for examples
4. **README**: See `README.md` for detailed guide
5. **LangGraph Docs**: https://docs.langchain.com/oss/python/langgraph/
6. **FastAPI Docs**: https://fastapi.tiangolo.com/
7. **Gemini API**: https://ai.google.dev/

---

## ⚡ Next Steps

1. ✅ Start the application
2. ✅ Create a session
3. ✅ Send a message
4. ✅ Read the code
5. ✅ Run tests
6. ✅ Extend with new features
7. ✅ Deploy to production

---

**Status**: ✅ Ready to use
**Version**: 1.0.0
**Updated**: February 12, 2026
