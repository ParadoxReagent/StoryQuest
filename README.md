# StoryQuest

A kid-friendly, interactive text adventure game powered by Large Language Models (LLMs).

## Overview

StoryQuest is an LLM-powered text adventure game designed for children aged 6-12. Kids can read or listen to engaging story scenes and either choose from suggested actions or enter their own creative responses. The story continues in a safe, whimsical, and age-appropriate way.

## Key Features

- **Flexible LLM Support**: Works with local LLMs (Ollama) or cloud LLMs (OpenAI, Anthropic, Gemini, OpenRouter)
- **Multi-Platform**: Designed for both Web UI and iPad app
- **Safe & Kid-Friendly**: Built-in safety filters and age-appropriate content
- **Interactive Storytelling**: Choose from suggestions or create your own responses
- **Multiple Themes**: Space adventures, magical forests, underwater quests, and more
- **Extensible**: Easy to add TTS, achievements, and image generation

## Architecture

The project is organized into phases:

1. **Phase 1**: Story format & API contract ✅
2. **Phase 2**: LLM abstraction layer ✅
3. **Phase 3**: Core story engine ✅
4. **Phase 4**: Web UI (MVP) ✅
5. **Phase 5**: iPad app
6. **Phase 6**: Enhanced Safety & Guardrails ✅
7. **Phase 7**: Enhancements (TTS, images, achievements)
8. **Phase 8**: Testing & polish

## Project Structure

```
StoryQuest/
├── backend/                  # FastAPI backend ✅
│   ├── app/
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # LLM providers, story engine, safety filter
│   │   ├── api/             # API endpoints
│   │   ├── db/              # Database models & connection
│   │   └── main.py          # Application entry point
│   ├── scripts/             # Database initialization
│   ├── tests/               # Backend tests
│   ├── config.yaml          # Configuration
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend Docker image
│   └── .dockerignore        # Docker ignore patterns
├── frontend/                # React Web UI ✅
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript definitions
│   │   └── App.tsx          # Main app component
│   ├── package.json         # Dependencies
│   ├── vite.config.ts       # Vite configuration
│   ├── nginx.conf           # Nginx configuration for production
│   ├── Dockerfile           # Frontend Docker image (multi-stage)
│   └── .dockerignore        # Docker ignore patterns
├── ios/                     # iPad app (Phase 5 - planned)
│   ├── README.md            # iOS development guide
│   ├── IOS_APP_PLAN.md      # Complete implementation plan (in root)
│   └── Examples/            # Reference Swift code
│       ├── Models.swift     # Data models example
│       └── ThemeSelectionView.swift  # UI example
├── docker-compose.yml       # Docker orchestration (production)
├── docker-compose.dev.yml   # Docker development overrides
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── GETTING_STARTED.md       # ⭐ Quick start guide (read this first!)
├── DOCKER.md                # Complete Docker guide
├── DOCKER_QUICK_REFERENCE.md # Docker commands cheat sheet
├── IOS_APP_PLAN.md          # Complete iOS app implementation plan
└── StoryQuest_Plan.md      # Detailed implementation plan
```

## Quick Start

> **💡 Recommended**: Use Docker for the easiest setup and deployment. All instructions below assume Docker usage.

### 🐳 Docker Setup (Primary Method)

StoryQuest is designed to run with Docker. This provides:
- ✅ Consistent environment across all platforms
- ✅ Automatic dependency management
- ✅ Easy deployment and scaling
- ✅ No manual Python/Node.js setup required

**Prerequisites:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- (Optional) [Ollama](https://ollama.ai) for local LLM

**Steps:**

1. Clone the repository:
```bash
git clone <repository-url>
cd StoryQuest
```

2. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env if using cloud LLMs (OpenAI/Anthropic/Gemini/OpenRouter)
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

5. View logs:
```bash
docker-compose logs -f
```

6. Stop the application:
```bash
docker-compose down
```

**Using with Ollama (Local LLM):**

If using Ollama running on your host machine, the default configuration will work automatically. The backend connects to `http://host.docker.internal:11434`.

**Using with Cloud LLMs:**

Edit `.env` file:
```bash
# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# For Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

---

### 📦 Manual Installation (Advanced)

> **⚠️ Note**: Manual installation is only recommended for development or if you cannot use Docker. For production and easiest setup, use Docker (see above).

<details>
<summary>Click to expand manual installation instructions</summary>

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- (Optional) Ollama for local LLM

#### 1. Backend Setup

See [backend/README.md](backend/README.md) for detailed instructions.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if using cloud LLMs

# Initialize the database
python scripts/init_db.py

# Start the backend server
python -m uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Frontend Setup

See [frontend/README.md](frontend/README.md) for detailed instructions.

```bash
cd frontend
npm install

# Start the development server
npm run dev
```

The web app will be available at http://localhost:3000

#### Using Local LLM (Ollama)

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.2:3b`
3. Ollama will be accessible from the backend automatically

#### Using Cloud LLMs

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

Or for Gemini:
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=ai-...
```

Or for OpenRouter:
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=or-...
```

</details>

---

## Implementation Progress

### ✅ Completed (Phases 1-4, 6)

**Phase 1: Story Format & API Contract**
- Story data models (Pydantic)
- API endpoint definitions
- LLM prompt templates

**Phase 2: LLM Abstraction Layer**
- Abstract LLM provider interface
- Ollama provider (local LLM)
- OpenAI provider (GPT-4o-mini)
- Anthropic provider (Claude)
- Gemini provider (Gemini 1.5 Flash)
- OpenRouter provider (multi-model aggregator)
- Configuration system with YAML support
- Factory pattern for LLM providers

**Phase 3: Core Story Engine**
- SQLAlchemy database models
- Database connection and session management
- Story Engine with LLM orchestration
- Basic Safety Filter for content moderation
- Fully functional API endpoints
- Error handling, retry logic, and fallback responses
- Database initialization script
- Session tracking and story history

**Phase 4: Web UI (MVP)**
- React + TypeScript + Vite setup
- Tailwind CSS styling
- Theme selection screen
- Interactive story view
- Choice buttons and custom input
- Story history viewer
- Loading states and error handling
- Responsive, kid-friendly design
- Accessibility features (ARIA labels, keyboard navigation)

**Phase 6: Enhanced Safety & Guardrails**
- Comprehensive enhanced safety filter (100+ banned words)
- Sentiment analysis for content validation (positive/negative scoring)
- Age-appropriate content filtering (6-8 vs 9-12)
- Optional OpenAI Moderation API integration
- Multi-layer rate limiting:
  - Session limits (20 turns/hour, 100/day)
  - Custom input limits (5 per 10 minutes)
  - IP limits (50/hour, 200/day)
  - Start story limits (10/hour per IP)
- Violation tracking and logging system
- Admin endpoints for monitoring:
  - View safety violations
  - Rate limiter statistics
  - System health checks
  - Configuration review
- Enhanced LLM prompts with explicit safety rules
- Fallback responses for rejected content

### 📋 Planned

**Phase 5: iPad App (SwiftUI)** - Designed, ready for implementation
- Native iOS/iPadOS app with SwiftUI
- Text-to-speech for read-aloud mode
- Offline story viewing and export
- Touch-optimized UI for kids
- Complete implementation plan available
- See [IOS_APP_PLAN.md](IOS_APP_PLAN.md) for details

**Future Phases:**
- Phase 7: TTS, image generation, achievements
- Phase 8: Comprehensive testing & production deployment

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Pydantic (data validation)
- SQLAlchemy (ORM)
- httpx (async HTTP client)
- SQLite / PostgreSQL (database)

**LLM Support:**
- Ollama (local LLM)
- OpenAI GPT-4o-mini (cloud)
- Anthropic Claude (cloud)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- Nginx (production server)

**DevOps:**
- Docker & Docker Compose
- Multi-stage builds
- Health checks and auto-restart

**iOS/iPadOS App (Phase 5 - designed):**
- Swift 5.9+ & SwiftUI
- Combine (reactive programming)
- Core Data (local storage)
- AVFoundation (text-to-speech)
- URLSession (API integration)
- Native iPad-optimized interface

## Safety & Content Moderation

StoryQuest prioritizes child safety:
- G-rated content only (no violence, scary themes, or adult content)
- Multi-layer content filtering
- Input validation and sanitization
- Positive, encouraging language
- Educational focus (curiosity, problem-solving, kindness)

## Documentation

### Getting Started

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - ⭐ Start here! Quick setup guide

### Docker & Deployment

- [Docker Guide](DOCKER.md) - Complete Docker setup and deployment guide
- [Docker Quick Reference](DOCKER_QUICK_REFERENCE.md) - Command cheat sheet

### Development Guides

- [Backend README](backend/README.md) - Backend setup and API documentation
- [Frontend README](frontend/README.md) - Frontend setup and development guide
- [iOS README](ios/README.md) - iOS app development guide
- [Safety Guide](backend/SAFETY.md) - Safety features and content moderation

### Planning & Architecture

- [iOS App Plan](IOS_APP_PLAN.md) - Complete iOS/iPadOS implementation plan
- [Detailed Plan](StoryQuest_Plan.md) - Complete implementation roadmap

### API Documentation (when running)

- [Interactive API Docs](http://localhost:8000/docs) - Swagger UI
- [Alternative Docs](http://localhost:8000/redoc) - ReDoc UI
- [Health Check](http://localhost:8000/health) - Backend health status
- [Admin Panel](http://localhost:8000/api/v1/admin/health/detailed) - Detailed system status

## Development

### Docker Development Workflow

**Start services in development mode:**
```bash
# Backend with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend
```

**Run commands inside containers:**
```bash
# Backend tests
docker-compose exec backend pytest

# Backend shell
docker-compose exec backend /bin/bash

# Frontend shell
docker-compose exec frontend /bin/sh
```

### Code Quality (Manual Setup Only)

If running without Docker:

```bash
# Format code
black backend/app
isort backend/app

# Type checking
mypy backend/app

# Linting
flake8 backend/app
```

For Docker-based development, see [DOCKER.md](DOCKER.md) for complete development workflows.

## Contributing

This is a personal/educational project. Contributions, suggestions, and feedback are welcome!

## License

TBD

## Roadmap

- [x] Phase 1: API contract & data models
- [x] Phase 2: LLM abstraction layer
- [x] Phase 3: Story engine implementation
- [x] Phase 4: Web UI MVP
- [x] Phase 6: Enhanced safety & content moderation
- [x] Docker deployment setup
- [ ] Phase 5: iPad app (planned - see [IOS_APP_PLAN.md](IOS_APP_PLAN.md))
- [ ] Phase 7: TTS, images, achievements
- [ ] Phase 8: Testing & production deployment

## How to Use

### With Docker (Recommended)

1. **Start the application**:
   ```bash
   docker-compose up -d
   ```

2. **Open the App**: Navigate to http://localhost:3000 in your browser

3. **Create a Story**:
   - Enter your name
   - Choose your age range (6-8 or 9-12)
   - Select an adventure theme
   - Click "Start My Adventure!"

4. **Play the Story**:
   - Read the scene text
   - Either click a suggested choice or type your own idea
   - Watch the story unfold based on your decisions!

5. **View History**: Click "Story So Far" to see all previous turns

6. **Start Over**: Click "New Story" to begin a fresh adventure

7. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Without Docker (Manual Setup)

If you're running manually (not recommended for production):

1. Start the backend: `cd backend && uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000
4. Follow steps 3-6 above

## Contact

For questions or feedback, please open an issue on GitHub.
