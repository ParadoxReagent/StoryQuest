# StoryQuest Backend

LLM-powered kids' text adventure game backend API.

## Implementation Status

- ✅ **Phase 1: Story Format & API Contract** - Complete
  - Pydantic models for story data structures
  - API endpoint definitions (stubs)
  - LLM prompt templates

- ✅ **Phase 2: LLM Abstraction Layer** - Complete
  - Abstract LLM provider interface
  - Ollama provider (local LLM)
  - OpenAI provider (cloud LLM)
  - Anthropic provider (cloud LLM)
  - Configuration system with YAML support
  - Factory pattern for provider creation

- 🚧 **Phase 3: Core Story Engine** - Not yet implemented
- 🚧 **Phase 4-8: Additional Features** - Not yet implemented

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

### Running the API

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

## Next Steps

- [ ] Implement Phase 3: Core Story Engine
- [ ] Add database integration
- [ ] Implement safety filters
- [ ] Add comprehensive tests
- [ ] Build Web UI (Phase 4)
- [ ] Build iPad app (Phase 5)

## License

TBD
