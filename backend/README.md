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

### Prerequisites

- Python 3.11+
- (Optional) Ollama installed for local LLM

### Installation

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

### Running the API

```bash
python -m uvicorn app.main:app --reload
```

Or using the shortcut:
```bash
cd app
python main.py
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

### LLM Provider Selection

Edit `config.yaml` or set the `LLM_PROVIDER` environment variable:

```yaml
llm:
  provider: "ollama"  # or "openai", "anthropic"
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

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

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

## Next Steps

- ✅ Phase 1: Story Format & API Contract
- ✅ Phase 2: LLM Abstraction Layer
- ✅ Phase 3: Core Story Engine Backend
- [ ] Phase 4: Minimal Web UI (MVP)
- [ ] Phase 5: iPad App (SwiftUI) client
- [ ] Phase 6: Safety, guardrails, and kid-friendly constraints (enhanced)
- [ ] Phase 7: Enhancements (TTS, images, achievements)
- [ ] Phase 8: Polish, testing, and hardening

## License

TBD
