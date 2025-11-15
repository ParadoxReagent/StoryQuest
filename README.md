# StoryQuest

A kid-friendly, interactive text adventure game powered by Large Language Models (LLMs).

## Overview

StoryQuest is an LLM-powered text adventure game designed for children aged 6-12. Kids can read or listen to engaging story scenes and either choose from suggested actions or enter their own creative responses. The story continues in a safe, whimsical, and age-appropriate way.

## Key Features

- **Flexible LLM Support**: Works with local LLMs (Ollama) or cloud LLMs (OpenAI, Anthropic)
- **Multi-Platform**: Designed for both Web UI and iPad app
- **Safe & Kid-Friendly**: Built-in safety filters and age-appropriate content
- **Interactive Storytelling**: Choose from suggestions or create your own responses
- **Multiple Themes**: Space adventures, magical forests, underwater quests, and more
- **Extensible**: Easy to add TTS, achievements, and image generation

## Architecture

The project is organized into phases:

1. **Phase 1**: Story format & API contract ✅
2. **Phase 2**: LLM abstraction layer ✅
3. **Phase 3**: Core story engine (in progress)
4. **Phase 4**: Web UI
5. **Phase 5**: iPad app
6. **Phase 6**: Safety & guardrails
7. **Phase 7**: Enhancements (TTS, images, achievements)
8. **Phase 8**: Testing & polish

## Project Structure

```
StoryQuest/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # LLM providers & business logic
│   │   ├── api/             # API endpoints
│   │   └── db/              # Database models
│   ├── tests/               # Backend tests
│   ├── config.yaml          # Configuration
│   └── requirements.txt     # Python dependencies
├── frontend/                # Web UI (Phase 4)
├── ios/                     # iPad app (Phase 5)
└── StoryQuest_Plan.md      # Detailed implementation plan
```

## Quick Start

### Backend Setup

See [backend/README.md](backend/README.md) for detailed instructions.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if using cloud LLMs
python app/main.py
```

The API will be available at http://localhost:8000

### Using Local LLM (Ollama)

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.2:3b`
3. Start the backend with `LLM_PROVIDER=ollama`

### Using Cloud LLMs

Set your API key in `.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Or for Anthropic:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Implementation Progress

### ✅ Completed (Phases 1-2)

- Story data models (Pydantic)
- API endpoint definitions
- LLM prompt templates
- Abstract LLM provider interface
- Ollama provider (local LLM)
- OpenAI provider
- Anthropic provider
- Configuration system
- Factory pattern for LLM providers

### 🚧 In Progress

- Phase 3: Core story engine
- Database integration
- Safety filters

### 📋 Planned

- Web UI (React + TypeScript)
- iPad app (SwiftUI)
- TTS (text-to-speech)
- Image generation
- Achievements system
- Comprehensive testing

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Pydantic (data validation)
- SQLAlchemy (ORM)
- httpx (async HTTP client)

**LLM Support:**
- Ollama (local)
- OpenAI GPT-4o-mini
- Anthropic Claude

**Frontend (planned):**
- React + TypeScript
- Tailwind CSS
- Vite

**iOS App (planned):**
- SwiftUI
- Core Data
- AVFoundation (TTS)

## Safety & Content Moderation

StoryQuest prioritizes child safety:
- G-rated content only (no violence, scary themes, or adult content)
- Multi-layer content filtering
- Input validation and sanitization
- Positive, encouraging language
- Educational focus (curiosity, problem-solving, kindness)

## Documentation

- [Detailed Plan](StoryQuest_Plan.md) - Complete implementation roadmap
- [Backend README](backend/README.md) - Backend setup and API documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Quality

```bash
# Format code
black backend/app
isort backend/app

# Type checking
mypy backend/app

# Linting
flake8 backend/app
```

## Contributing

This is a personal/educational project. Contributions, suggestions, and feedback are welcome!

## License

TBD

## Roadmap

- [x] Phase 1: API contract & data models
- [x] Phase 2: LLM abstraction layer
- [ ] Phase 3: Story engine implementation
- [ ] Phase 4: Web UI MVP
- [ ] Phase 5: iPad app
- [ ] Phase 6: Safety & content moderation
- [ ] Phase 7: TTS, images, achievements
- [ ] Phase 8: Testing & production deployment

## Contact

For questions or feedback, please open an issue on GitHub.
