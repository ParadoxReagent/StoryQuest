# StoryQuest Backend

LLM-powered kids' text adventure game backend API.

## Implementation Status

- ✅ **Phase 1: Story Format & API Contract** - Complete
  - Pydantic models for story data structures
  - API endpoint definitions
  - LLM prompt templates

- ✅ **Phase 2: LLM Abstraction Layer** - Complete
  - Abstract LLM provider interface
  - Ollama provider (local LLM)
  - OpenAI provider (cloud LLM)
  - Anthropic provider (cloud LLM)
  - Gemini provider (cloud LLM)
  - OpenRouter provider (cloud LLM aggregator)
  - Configuration system with YAML support
  - Factory pattern for provider creation

- ✅ **Phase 3: Core Story Engine** - Complete
  - SQLAlchemy database models (sessions and story turns)
  - Database connection and session management
  - Story Engine with LLM orchestration
  - Basic Safety Filter for content moderation
  - Fully functional API endpoints
  - Error handling, retry logic, and fallback responses
  - Database initialization script

- ✅ **Phase 4: Web UI (MVP)** - Complete
  - React + TypeScript frontend
  - Interactive story interface
  - Theme selection and gameplay

- ✅ **Phase 6: Enhanced Safety & Guardrails** - Complete
  - Comprehensive safety filter (100+ banned words)
  - Sentiment analysis for content validation
  - Age-appropriate content filtering (6-8 vs 9-12)
  - Optional OpenAI Moderation API integration
  - Rate limiting (session, IP, custom input limits)
  - Violation tracking and logging
  - Admin endpoints for monitoring
  - Enhanced LLM prompts with explicit safety rules

- 🚧 **Phase 5, 7-8: Additional Features** - Not yet implemented

## Quick Start

> **💡 Recommended**: Use Docker for the easiest setup. See the main [README.md](../README.md) and [DOCKER.md](../DOCKER.md) for Docker instructions.

### 🐳 With Docker (Recommended)

**Run the entire application:**
```bash
# From project root
docker-compose up -d
```

**Access the API:**
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

**View backend logs:**
```bash
docker-compose logs -f backend
```

**Run backend commands:**
```bash
# Access backend shell
docker-compose exec backend /bin/bash

# Run tests
docker-compose exec backend pytest

# Initialize database (already done on startup)
docker-compose exec backend python scripts/init_db.py
```

**Configure LLM provider:**

Edit `.env` in the project root:
```bash
# For Ollama (default)
LLM_PROVIDER=ollama

# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# For Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=ai-your-key-here

# For OpenRouter
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=or-your-key-here
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

---

### 📦 Manual Installation (Advanced)

> **⚠️ Note**: Manual installation is only recommended for development. For production, use Docker.

<details>
<summary>Click to expand manual installation instructions</summary>

**Prerequisites:**
- Python 3.11+
- (Optional) Ollama installed for local LLM

**Installation Steps:**

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
```bash
cp .env.example .env
# Edit .env with your API keys if using cloud LLMs
```

4. (Optional) If using Ollama, pull a model:
```bash
ollama pull llama3.2:3b
```

5. Initialize the database:
```bash
python scripts/init_db.py
```

**Running the API:**

```bash
python -m uvicorn app.main:app --reload
```

Or using the shortcut:
```bash
cd app
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

</details>

## Configuration

### LLM Provider Selection

Edit `config.yaml` or set the `LLM_PROVIDER` environment variable:

```yaml
llm:
  provider: "ollama"  # or "openai", "anthropic", "gemini", "openrouter"
```

### Using Different LLM Providers

**Ollama (Local):**
```yaml
llm:
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2:3b"
```

**OpenAI (Cloud):**
```yaml
llm:
  provider: "openai"
  openai:
    api_key: "${OPENAI_API_KEY}"  # Set in .env
    model: "gpt-4o-mini"
```

**Anthropic (Cloud):**
```yaml
llm:
  provider: "anthropic"
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"  # Set in .env
    model: "claude-3-5-haiku-20241022"
```

**Gemini (Cloud):**
```yaml
llm:
  provider: "gemini"
  gemini:
    api_key: "${GEMINI_API_KEY}"  # Set in .env
    model: "gemini-1.5-flash"
```

**OpenRouter (Cloud Aggregator):**
```yaml
llm:
  provider: "openrouter"
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"  # Set in .env
    model: "anthropic/claude-3.5-haiku"
    site_url: "https://storyquest.local"
    app_name: "StoryQuest"
```

## API Endpoints

### `GET /`
Health check and API information.

### `GET /health`
Service health check.

### `POST /api/v1/story/start`
Start a new story session.

**Request:**
```json
{
  "player_name": "Alex",
  "age_range": "6-8",
  "theme": "space_adventure"
}
```

**Response:** (Not yet implemented - Phase 3)
```json
{
  "session_id": "uuid",
  "story_summary": "...",
  "current_scene": {...},
  "choices": [...]
}
```

### `POST /api/v1/story/continue`
Continue an existing story.

**Request:**
```json
{
  "session_id": "uuid",
  "choice_id": "c1",
  "custom_input": null,
  "story_summary": "..."
}
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── story.py         # Story data models
│   │   └── session.py       # Session models
│   ├── services/
│   │   ├── llm_provider.py  # LLM abstraction layer
│   │   ├── llm_factory.py   # Provider factory
│   │   └── prompts.py       # LLM prompt templates
│   ├── api/
│   │   └── v1/
│   │       └── story.py     # API endpoints
│   └── db/
│       └── (database models - Phase 3)
├── tests/
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Development

### With Docker (Recommended)

**Run tests:**
```bash
docker-compose exec backend pytest
```

**Code formatting:**
```bash
docker-compose exec backend black app/
docker-compose exec backend isort app/
```

**Type checking:**
```bash
docker-compose exec backend mypy app/
```

**Access Python shell:**
```bash
docker-compose exec backend python
```

**Hot-reload development mode:**
```bash
# From project root
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

See [DOCKER.md](../DOCKER.md) for complete Docker development workflows.

---

### Manual Development

If running without Docker:

**Run tests:**
```bash
pytest
```

**Code formatting:**
```bash
black app/
isort app/
```

**Type checking:**
```bash
mypy app/
```

## What's New in Phase 3

Phase 3 implements the core story engine with the following features:

- **Database Integration**: SQLAlchemy models for persistent session and story turn storage
- **Story Engine**: Orchestrates LLM calls, manages sessions, and handles story continuity
- **Safety Filter**: Multi-layer content moderation for kid-friendly content
- **Error Handling**: Retry logic with exponential backoff and fallback responses
- **Session Management**: Track story history, resume sessions, and enforce turn limits

## Roadmap

- ✅ Phase 1: Story Format & API Contract
- ✅ Phase 2: LLM Abstraction Layer
- ✅ Phase 3: Core Story Engine Backend
- ✅ Phase 4: Web UI (MVP)
- ✅ Phase 6: Enhanced Safety & Guardrails
- ✅ Docker Deployment
- [ ] Phase 5: iPad App (SwiftUI) - See [IOS_APP_PLAN.md](../IOS_APP_PLAN.md)
- [ ] Phase 7: Enhancements (TTS, images, achievements)
- [ ] Phase 8: Polish, testing, and production hardening

## License

TBD
