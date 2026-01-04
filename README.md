# 🎭 StoryQuest

**An AI-powered interactive storytelling adventure for kids**

StoryQuest is a safe, creative, and educational storytelling platform where children and young adults aged 5-18 become the heroes of their own AI-generated adventures. Choose from magical themes, make decisions that shape the story, and watch your imagination come to life through the power of Large Language Models. The beautiful storybook-themed interface adapts content complexity based on reading level.

---

## ✨ Features

### 🎨 **Multi-Platform Experience**
- **Web Application**: Full-featured React web app with responsive design
- **iOS/iPadOS App**: Native SwiftUI app optimized for iPad with text-to-speech
- **Cross-Platform**: Same backend powers all platforms seamlessly

### 🤖 **Flexible AI Integration**
- **Local LLMs**: Run completely offline with Ollama (privacy-first)
- **Cloud LLMs**: OpenAI GPT-4o-mini, Anthropic Claude, Google Gemini, OpenRouter
- **Smart Fallbacks**: Automatic retry logic and graceful degradation
- **Streaming Responses**: Real-time story generation for engaging experiences

### 🛡️ **Advanced Safety System**
- **Multi-Layer Content Filtering**: Comprehensive banned word list and sentiment analysis
- **Age-Adaptive Content**: Four distinct reading levels with tailored content complexity:
  - **Early Reader (5-7)**: Wonder, friendship, simple vocabulary
  - **Middle Reader (8-10)**: Action, bravery, age-appropriate challenges
  - **Tween (11-13)**: Moral dilemmas, deeper themes, complex narratives
  - **Young Adult (14-18)**: Sophisticated storytelling, mature themes handled appropriately
- **Rate Limiting**: Prevents abuse with session, IP, and custom input limits
- **Moderation API**: Optional OpenAI Moderation API integration
- **Violation Tracking**: Admin dashboard for monitoring and compliance

### 📚 **Rich Story Experience**
- **7 Unique Themes**: Space adventures, magical forests, underwater quests, medieval castles, dinosaur lands, superhero cities, and Arctic explorations
- **Dynamic Choices**: Select from AI-generated options or write your own creative responses
- **Story History**: Review your adventure journey from beginning to end
- **Progress Tracking**: Visual indicators for story completion and turns
- **Text-to-Speech**: Story narration on web (Kokoro/Chatterbox TTS) and iOS (native AVFoundation)

### 🔊 **Text-to-Speech Narration**
- **Kokoro TTS** (Default): Fast, lightweight 82M model - perfect for CPU and Apple Silicon
- **Chatterbox TTS** (Alternative): Higher quality with voice cloning - requires NVIDIA GPU
- **44+ Voice Options**: American, British, Japanese, Chinese, Spanish, French, and more
- **Customizable**: Adjust speed, emotion, and voice characteristics
- **Cached Audio**: Previously generated narrations are cached for instant playback

### 🚀 **Production-Ready**
- **Docker Deployment**: Complete containerized setup with docker-compose
- **Database Persistence**: SQLite with WAL mode for development, PostgreSQL-ready for production
- **Performance Optimized**: Streaming throttling, CSS-only animations, database indexes
- **Health Monitoring**: Built-in health checks and detailed system status endpoints
- **Admin Dashboard**: Real-time monitoring of safety violations, rate limits, and system health
- **Hot Reload**: Development mode with automatic code reloading

---

## 🏗️ Architecture

StoryQuest is built with a modern, scalable architecture:

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend Clients                      │
│  ┌──────────────────┐      ┌──────────────────┐         │
│  │   React Web UI   │      │  SwiftUI iOS App │         │
│  │ (Vite + Tailwind)│      │  (iPad Optimized)│         │
│  └────────┬─────────┘      └─────────┬────────┘         │
└───────────┼─────────────────────────┼───────────────────┘
            │                         │
            ├─────────────────────────┤
            │                         │
┌───────────▼───────────┐   ┌─────────▼─────────┐
│   FastAPI Backend     │   │   TTS Service     │
│  ┌──────────────┐     │   │  ┌─────────────┐  │
│  │ Story Engine │     │   │  │ Kokoro TTS  │  │
│  └──────┬───────┘     │   │  │   (Default) │  │
│         │             │   │  └─────────────┘  │
│  ┌──────▼───────┐     │   │        or         │
│  │ Safety Filter│     │   │  ┌─────────────┐  │
│  └──────┬───────┘     │   │  │ Chatterbox  │  │
│         │             │   │  │ (GPU/CUDA)  │  │
│  ┌──────▼───────┐     │   │  └─────────────┘  │
│  │ LLM Providers│     │   └───────────────────┘
│  └──────────────┘     │
└──────────┬────────────┘
           │
  ┌────────┼────────┬─────────────┐
  │        │        │             │
┌─▼────┐ ┌─▼─────┐ ┌▼─────┐ ┌─────▼───────────┐
│Ollama│ │OpenAI │ │Claude│ │Gemini/OpenRouter│
└──────┘ └───────┘ └──────┘ └─────────────────┘
```

---

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy with async support
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (async)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Safety**: Custom content filter + OpenAI Moderation API

### Frontend (Web)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **State Management**: React Query (@tanstack/react-query)
- **Animations**: Framer Motion
- **Notifications**: Sonner
- **Testing**: Vitest + React Testing Library

### Frontend (iOS)
- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI
- **Reactive Programming**: Combine
- **Local Storage**: Core Data
- **Text-to-Speech**: AVFoundation
- **Networking**: URLSession
- **Architecture**: MVVM pattern

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (production frontend)
- **CI/CD**: GitHub Actions (planned)
- **Monitoring**: Health checks, admin dashboard

### AI/LLM Providers
- **Local**: Ollama (llama3.2, qwen2.5, gemma2, etc.)
- **Cloud**: OpenAI, Anthropic Claude, Google Gemini, OpenRouter

### Text-to-Speech
- **Kokoro TTS**: 82M parameter model, CPU/MPS optimized, 44+ voices
- **Chatterbox TTS**: Resemble AI's model with voice cloning, CUDA recommended

---

## 🚀 Quick Start

### Using Docker (Recommended)

The fastest way to run StoryQuest is with Docker:

```bash
# Clone the repository
git clone <repository-url>
cd StoryQuest

# (Optional) Configure environment for cloud LLMs
cp .env.example .env
# Edit .env to add API keys if not using Ollama

# Start all services
docker-compose up -d

# Access the application
# Web UI: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**That's it!** The web app is now running and ready to use.

#### Using with Ollama (Local LLM)

If you have Ollama installed locally, the default configuration will work automatically:

```bash
# Pull a model (first time only)
ollama pull llama3.2:3b

# Start StoryQuest
docker-compose up -d
```

The backend automatically connects to Ollama at `http://host.docker.internal:11434`.

#### Using with Cloud LLMs

Edit your `.env` file:

```bash
# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o-mini

# For Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
MODEL_NAME=claude-3-haiku-20240307
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

### Manual Installation (Development)

<details>
<summary>Click to expand manual installation instructions</summary>

#### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Ollama for local LLM

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env as needed

# Initialize database
python scripts/init_db.py

# Start backend
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

#### iOS App Setup

See [ios/README.md](ios/README.md) for complete Xcode setup instructions.

</details>

---

## 📖 How to Use

### Web Application

1. **Start StoryQuest**: Navigate to http://localhost:3000
2. **Enter Your Name**: Tell us what to call you
3. **Set Reading Level**: Use the age slider (5-18) to select your reading level:
   - **5-7**: Early Reader (Wonder & Friendship)
   - **8-10**: Middle Reader (Action & Bravery)
   - **11-13**: Tween (Moral Dilemmas)
   - **14-18**: Young Adult (Complex Themes)
4. **Pick a Theme**: Choose from dynamically generated adventure themes
5. **Start Your Adventure**: Click "Begin Your Quest" to begin
6. **Make Choices**:
   - Click suggested choices for quick decisions
   - Or type your own creative responses
7. **Watch the Story Unfold**: See how your choices shape the adventure
8. **Listen Along**: Click the speaker button for text-to-speech narration
9. **View History**: Click "Story So Far" to review previous turns
10. **Start Over**: Click "New Story" anytime to begin fresh

### iOS/iPadOS App

1. **Open StoryQuest** on your iPad
2. **Configure API URL**: First launch will prompt for backend URL
3. **Select Theme**: Browse beautiful theme cards
4. **Begin Story**: Tap to start your adventure
5. **Listen or Read**: Toggle text-to-speech for read-aloud mode
6. **Make Choices**: Tap choices or use custom input
7. **Track Progress**: See your story progress visually
8. **Review History**: Access your story history anytime

---

## 📂 Project Structure

```
StoryQuest/
├── backend/                    # FastAPI Backend ✅
│   ├── app/
│   │   ├── api/v1/            # REST API endpoints
│   │   │   ├── story.py       # Story endpoints (start, continue, history)
│   │   │   └── admin.py       # Admin monitoring endpoints
│   │   ├── models/            # Pydantic data models
│   │   │   ├── story.py       # Story, scene, choice models
│   │   │   └── requests.py    # API request/response models
│   │   ├── services/          # Business logic
│   │   │   ├── llm/           # LLM provider implementations
│   │   │   │   ├── base.py    # Abstract base class
│   │   │   │   ├── ollama.py  # Ollama provider
│   │   │   │   ├── openai.py  # OpenAI provider
│   │   │   │   ├── anthropic.py # Anthropic provider
│   │   │   │   └── gemini.py  # Google Gemini provider
│   │   │   ├── story_engine.py    # Core story generation logic
│   │   │   ├── safety_filter.py   # Content moderation
│   │   │   └── rate_limiter.py    # Rate limiting service
│   │   ├── db/                # Database layer
│   │   │   ├── database.py    # Connection and session management
│   │   │   └── models.py      # SQLAlchemy ORM models
│   │   ├── config.py          # Configuration management
│   │   └── main.py            # FastAPI application entry point
│   ├── scripts/               # Utility scripts
│   │   └── init_db.py         # Database initialization
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container image
│   └── README.md              # Backend documentation
│
├── frontend/                   # React Web UI ✅
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ThemeSelection.tsx   # Theme picker screen
│   │   │   ├── StoryView.tsx        # Main story interface
│   │   │   ├── ChoiceButtons.tsx    # Choice selection UI
│   │   │   ├── CustomInput.tsx      # Custom text input
│   │   │   └── StoryHistory.tsx     # History viewer
│   │   ├── services/          # API integration
│   │   │   └── api.ts         # Axios API client
│   │   ├── types/             # TypeScript definitions
│   │   │   └── story.ts       # Story type definitions
│   │   ├── App.tsx            # Main application component
│   │   └── main.tsx           # Application entry point
│   ├── public/                # Static assets
│   ├── package.json           # NPM dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── nginx.conf             # Production nginx config
│   ├── Dockerfile             # Frontend container image
│   └── README.md              # Frontend documentation
│
├── ios/                        # iOS/iPadOS App ✅
│   ├── StoryQuest-iOS/
│   │   └── StoryQuest/
│   │       ├── App/           # App entry point
│   │       │   ├── StoryQuestApp.swift      # Main app
│   │       │   └── AppEnvironment.swift     # App-wide state
│   │       ├── Models/        # Data models
│   │       │   ├── Story.swift              # Story models
│   │       │   ├── Theme.swift              # Theme definitions
│   │       │   ├── StreamEvent.swift        # Streaming models
│   │       │   └── SessionHistory.swift     # History models
│   │       ├── Services/      # Business logic
│   │       │   ├── APIService.swift         # Backend API client
│   │       │   ├── StreamingService.swift   # Real-time streaming
│   │       │   ├── StorageService.swift     # Core Data persistence
│   │       │   └── TTSService.swift         # Text-to-speech
│   │       ├── ViewModels/    # MVVM view models
│   │       │   ├── ThemeViewModel.swift     # Theme selection logic
│   │       │   ├── StoryViewModel.swift     # Story state management
│   │       │   └── HistoryViewModel.swift   # History logic
│   │       ├── Views/         # SwiftUI views
│   │       │   ├── Theme/     # Theme selection screens
│   │       │   ├── Story/     # Story gameplay screens
│   │       │   └── Shared/    # Reusable components
│   │       └── Utilities/     # Helper code
│   │           ├── Constants.swift          # App constants
│   │           ├── Extensions.swift         # Swift extensions
│   │           └── RateLimitTracker.swift   # Client-side rate limiting
│   ├── Examples/              # Reference implementations
│   └── README.md              # iOS development guide
│
├── tts-kokoro/                 # Kokoro TTS Service (Default) ✅
│   ├── app.py                 # FastAPI TTS wrapper
│   ├── Dockerfile             # Container image (CPU/MPS)
│   └── requirements.txt       # Python dependencies
│
├── tts-chatterbox/             # Chatterbox TTS Service (Alternative) ✅
│   ├── app.py                 # FastAPI TTS wrapper
│   ├── Dockerfile             # Container image (CUDA)
│   └── requirements.txt       # Python dependencies
│
├── docker-compose.yml         # Production Docker setup ✅
├── docker-compose.dev.yml     # Development overrides ✅
├── .env.example               # Environment template ✅
├── .gitignore                 # Git ignore patterns ✅
│
├── GETTING_STARTED.md         # ⭐ Quick start guide
├── DOCKER.md                  # Complete Docker guide
├── DOCKER_QUICK_REFERENCE.md  # Docker cheat sheet
├── StoryQuest_Plan.md         # Implementation roadmap
└── README.md                  # This file
```

---

## 🛡️ Safety & Content Moderation

StoryQuest prioritizes child safety with multiple layers of protection:

### Content Filtering
- **100+ Banned Words**: Comprehensive blocklist for inappropriate content
- **Sentiment Analysis**: Real-time scoring to ensure positive, encouraging content
- **Age-Adaptive Modes**: Four distinct content levels (5-7, 8-10, 11-13, 14-18) with tailored vocabulary, themes, and complexity
- **LLM Prompt Engineering**: Age-specific system prompts with drastically different tones and content rules
- **OpenAI Moderation API**: Optional additional layer for cloud deployments

### Rate Limiting
- **Session Limits**: 20 turns per hour, 100 turns per day per session
- **Custom Input Limits**: 5 custom responses per 10 minutes
- **IP-Based Limits**: 50 requests per hour, 200 per day per IP
- **Story Start Limits**: 10 new stories per hour per IP
- **Graceful Handling**: Clear error messages and retry guidance

### Monitoring & Administration
- **Violation Tracking**: All safety filter violations are logged with context
- **Admin Dashboard**: Real-time monitoring at `/api/v1/admin/`
  - View safety violations
  - Check rate limiter statistics
  - Review system health
  - Monitor configuration
- **Detailed Logging**: Comprehensive logs for debugging and compliance

### Safety Guarantees
✅ Age-appropriate content tailored to reading level
✅ Younger ages (5-10): Gentle themes, no conflict, educational focus
✅ Tweens (11-13): Appropriate challenges with positive resolution
✅ Young adults (14-18): Mature themes handled responsibly
✅ Input validation and sanitization
✅ Automatic fallback for rejected content

---

## 🔊 Text-to-Speech Configuration

StoryQuest includes two TTS options for story narration. Click the speaker button in the story header to hear the current scene read aloud.

### Choosing a TTS Provider

Edit `docker-compose.yml` to switch between providers:

```yaml
# In docker-compose.yml, only ONE tts service should be uncommented at a time

# Option 1: Kokoro TTS (DEFAULT) - Fast, works on CPU/Apple Silicon
tts:
  build:
    context: ./tts-kokoro
    ...

# Option 2: Chatterbox TTS - Higher quality, requires NVIDIA GPU
# Uncomment this and comment out Kokoro above to switch
# tts:
#   build:
#     context: ./tts-chatterbox
#     ...
```

### Kokoro TTS (Default)

**Best for**: CPU-only systems, Apple Silicon Macs, faster response times

**API Endpoint**: `POST /synthesize`

```json
{
  "text": "Once upon a time...",
  "voice": "af_heart",
  "speed": 1.0
}
```

**Parameters**:
| Parameter | Type   | Default    | Range        | Description             |
|-----------|--------|------------|--------------|-------------------------|
| `text`    | string | required   | 1-5000 chars | Text to synthesize      |
| `voice`   | string | `af_heart` | see below    | Voice ID to use         |
| `speed`   | float  | `1.0`      | 0.5-2.0      | Speech speed multiplier |

**Available Voices (44 total)**:

<details>
<summary>🇺🇸 American English (20 voices)</summary>

|   Voice ID   | Gender | Quality |         Notes       |
|--------------|--------|---------|---------------------|
| `af_heart`   | Female | ⭐ A    | Recommended default |
| `af_bella`   | Female | A-      | Warm, expressive    |
| `af_nicole`  | Female | B-      | Clear, professional |
| `af_sarah`   | Female | C+      | Friendly            |
| `af_aoede`   | Female | C+      | Soft                |
| `af_kore`    | Female | C+      | Young               |
| `af_nova`    | Female | C       | Bright              |
| `af_alloy`.  | Female | C       | Neutral             |
| `af_sky`     | Female | C-      | Light               |
| `af_jessica` | Female | D       | Casual              |
| `af_river`   | Female | D       | Calm                |
| `am_fenrir`  | Male   | C+      | Deep, authoritative |
| `am_michael` | Male   | C+      | Professional        |
| `am_puck`    | Male   | C+      | Playful             |
| `am_adam`    | Male   | F+      | Standard            |
| `am_echo`    | Male   | D       | Smooth              |
| `am_eric`    | Male   | D       | Casual              |
| `am_liam`    | Male   | D       | Young               |
| `am_onyx`    | Male   | D       | Deep                |
| `am_santa`   | Male   | D-      | Festive             |

</details>

<details>
<summary>🇬🇧 British English (8 voices)</summary>

|   Voice ID    | Gender | Quality |
|---------------|--------|---------|
| `bf_emma`     | Female | B-      |
| `bf_isabella` | Female | C       |
| `bf_alice`    | Female | D       |
| `bf_lily`     | Female | D       |
| `bm_fable`    | Male   | C       |
| `bm_george`   | Male   | C       |
| `bm_lewis`    | Male   | D+      |
| `bm_daniel`   | Male   | D       |

</details>

<details>
<summary>🌍 Other Languages (16 voices)</summary>

**Japanese**: `jf_alpha`, `jf_gongitsune`, `jf_nezumi`, `jf_tebukuro`, `jm_kumo`

**Mandarin Chinese**: `zf_xiaobei`, `zf_xiaoni`, `zf_xiaoxiao`, `zf_xiaoyi`, `zm_yunjian`, `zm_yunxi`, `zm_yunxia`, `zm_yunyang`

**Spanish**: `ef_dora`, `em_alex`, `em_santa`

**French**: `ff_siwis`

**Hindi**: `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi`

**Italian**: `if_sara`, `im_nicola`

**Brazilian Portuguese**: `pf_dora`, `pm_alex`, `pm_santa`

</details>

### Chatterbox TTS (Alternative)

**Best for**: Systems with NVIDIA GPU, highest quality output, voice cloning

**API Endpoint**: `POST /synthesize`

```json
{
  "text": "Once upon a time...",
  "exaggeration": 0.5,
  "cfg_weight": 0.5
}
```

**Parameters**:
| Parameter      | Type   | Default  | Range        | Description                    |
|----------------|--------|----------|--------------|--------------------------------|
| `text`         | string | required | 1-5000 chars | Text to synthesize             |
| `exaggeration` | float  | `0.5`    | 0.0-1.0      | Emotion/expressiveness level   |
| `cfg_weight`   | float  | `0.5`    | 0.0-1.0      | Voice characteristic adherence |

**Parameter Tips**:
- **Higher exaggeration** (0.7+): More dramatic, expressive delivery (may increase speed)
- **Lower cfg_weight** (0.3): Better pacing, reduced accent transfer
- **Default values** (0.5/0.5): Balanced, natural speech

**Advanced Features**:
- Supports `[laugh]`, `[cough]`, `[chuckle]` tags for natural expressiveness
- Voice cloning available via `audio_prompt_path` parameter (requires ~10s reference audio)

### Customizing the Default Voice

To change the default voice used for story narration, edit the frontend TTS service:

**File**: `frontend/src/services/tts.ts`

```typescript
export async function synthesizeSpeech(request: TTSRequest): Promise<string> {
  const response = await fetch(`${TTS_BASE_URL}/synthesize`, {
    // ...
    body: JSON.stringify({
      text: request.text,
      voice: request.voice ?? 'af_bella',  // Change default voice here
      speed: request.speed ?? 1.0,
    }),
  });
}
```

### TTS API Endpoints

Both services expose the same endpoints on port 8001:

| Endpoint.     | Method | Description                         |
|---------------|--------|-------------------------------------|
| `/health`     | GET    | Health check and device info        |
| `/synthesize` | POST   | Generate speech audio (returns WAV) |
| `/cache`      | DELETE | Clear the audio cache               |

---

## 📚 Documentation

### Getting Started
- **[Getting Started Guide](GETTING_STARTED.md)** - ⭐ Start here! Comprehensive setup guide
- **[Quick Start](QUICKSTART.md)** - 5-minute quick start

### Deployment
- **[Docker Guide](DOCKER.md)** - Complete Docker setup and deployment
- **[Docker Quick Reference](DOCKER_QUICK_REFERENCE.md)** - Common Docker commands

### Development
- **[Backend README](backend/README.md)** - Backend API documentation
- **[Frontend README](frontend/README.md)** - Frontend development guide
- **[iOS README](ios/README.md)** - iOS app development guide
- **[Safety Documentation](backend/SAFETY.md)** - Safety features and moderation

### Planning & Architecture
- **[Implementation Plan](StoryQuest_Plan.md)** - Complete implementation roadmap
- **[Performance Guide](PERFORMANCE.md)** - Implemented optimizations and recommendations

### API Documentation (Live)
When the backend is running, access interactive API documentation:
- **[Swagger UI](http://localhost:8000/docs)** - Interactive API explorer
- **[ReDoc](http://localhost:8000/redoc)** - Alternative API documentation
- **[Health Check](http://localhost:8000/health)** - Backend health status
- **[Admin Dashboard](http://localhost:8000/api/v1/admin/health/detailed)** - Detailed system monitoring

---

## 🔧 Development

### Docker Development Workflow

Start services in development mode with hot reload:

```bash
# Start all services with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in containers
docker-compose exec backend pytest                # Run tests
docker-compose exec backend python scripts/init_db.py  # Reset database
docker-compose exec frontend npm run test         # Frontend tests

# Access container shells
docker-compose exec backend /bin/bash
docker-compose exec frontend /bin/sh

# Rebuild after dependency changes
docker-compose build backend
docker-compose up -d backend
```

### Running Tests

```bash
# Backend tests
cd backend
pytest                          # All tests
pytest tests/test_story.py     # Specific test file
pytest -v                      # Verbose output
pytest --cov=app               # Coverage report

# Frontend tests
cd frontend
npm run test                   # Run tests
npm run test:ui                # Interactive test UI
npm run test:coverage          # Coverage report
```

### Code Quality (Manual Setup)

```bash
# Backend
cd backend
black app/                     # Format code
isort app/                     # Sort imports
mypy app/                      # Type checking
flake8 app/                    # Linting

# Frontend
cd frontend
npm run lint                   # ESLint
npm run lint -- --fix          # Auto-fix issues
```

---

## 🎯 Implementation Status

### ✅ Completed Phases

#### Phase 1: Story Format & API Contract
- ✅ Pydantic data models for stories, scenes, and choices
- ✅ REST API endpoint definitions
- ✅ LLM prompt templates with safety guidelines

#### Phase 2: LLM Abstraction Layer
- ✅ Abstract provider interface for extensibility
- ✅ Ollama provider (local LLM support)
- ✅ OpenAI provider (GPT-4o-mini, GPT-3.5-turbo)
- ✅ Anthropic provider (Claude 3 Haiku, Sonnet)
- ✅ Google Gemini provider (Gemini 1.5 Flash)
- ✅ OpenRouter provider (multi-model aggregator)
- ✅ YAML-based configuration system
- ✅ Factory pattern for provider selection
- ✅ Error handling and retry logic

#### Phase 3: Core Story Engine
- ✅ SQLAlchemy database models and migrations
- ✅ Database connection management (sync & async)
- ✅ Story Engine with LLM orchestration
- ✅ Safety Filter with content moderation
- ✅ Fully functional REST API endpoints
- ✅ Error handling and fallback responses
- ✅ Database initialization scripts
- ✅ Session and story history tracking

#### Phase 4: Web UI (React)
- ✅ React 18 + TypeScript + Vite setup
- ✅ Tailwind CSS styling system
- ✅ Theme selection interface
- ✅ Interactive story view with choices
- ✅ Custom input for creative responses
- ✅ Story history viewer
- ✅ Loading states and error handling
- ✅ Responsive, kid-friendly design
- ✅ Accessibility (ARIA labels, keyboard nav)
- ✅ React Query for state management
- ✅ Framer Motion animations
- ✅ Toast notifications

#### Phase 5: iOS/iPadOS App (SwiftUI)
- ✅ Complete SwiftUI app architecture
- ✅ MVVM pattern implementation
- ✅ Theme selection with beautiful cards
- ✅ Story gameplay interface
- ✅ Real-time streaming support
- ✅ Text-to-speech integration
- ✅ Core Data persistence
- ✅ Client-side rate limiting
- ✅ Error handling and recovery
- ✅ iPad-optimized layouts
- ✅ Accessibility support
- ✅ Offline story viewing

#### Phase 6: Enhanced Safety & Guardrails
- ✅ Comprehensive safety filter (100+ banned words)
- ✅ Sentiment analysis (positive/negative scoring)
- ✅ Age-appropriate content filtering (6-8 vs 9-12)
- ✅ OpenAI Moderation API integration (optional)
- ✅ Multi-layer rate limiting system
- ✅ Violation tracking and logging
- ✅ Admin monitoring dashboard
- ✅ Enhanced LLM safety prompts
- ✅ Graceful fallback responses

#### DevOps & Deployment
- ✅ Complete Docker setup (backend + frontend + TTS)
- ✅ Docker Compose orchestration
- ✅ Multi-stage builds for optimization
- ✅ Health checks and auto-restart
- ✅ Development mode with hot reload
- ✅ Production-ready Nginx configuration
- ✅ Environment-based configuration
- ✅ Non-root container security

#### Text-to-Speech Integration
- ✅ Kokoro TTS service (CPU/MPS optimized, 44+ voices)
- ✅ Chatterbox TTS service (CUDA GPU, voice cloning)
- ✅ Web UI speaker button for narration
- ✅ Audio caching for instant replay
- ✅ Configurable voice and speed settings

### 📋 Planned Enhancements

#### Phase 7: Extended Features
- [ ] Image generation for story scenes (DALL-E, Stable Diffusion)
- [ ] Achievement system and badges
- [ ] Story export (PDF, EPUB)
- [ ] Multi-language support
- [ ] Parent dashboard and controls
- [ ] Story sharing (with parental approval)

#### Phase 8: Testing & Polish
- [ ] Comprehensive end-to-end tests
- [ ] Load testing and performance optimization
- [ ] Security audit
- [ ] User testing with children
- [ ] Production deployment guide
- [ ] CI/CD pipeline

---

## 🤝 Contributing

StoryQuest is a personal/educational project, but contributions, suggestions, and feedback are welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Keep commits focused and atomic

---

## 📝 License

To be determined. This is currently a personal/educational project.

---

## 🗺️ Roadmap

- [x] **Phase 1**: API contract & data models
- [x] **Phase 2**: LLM abstraction layer with multiple providers
- [x] **Phase 3**: Story engine and core backend
- [x] **Phase 4**: React web UI
- [x] **Phase 5**: Native iOS/iPadOS app
- [x] **Phase 6**: Enhanced safety and content moderation
- [x] **DevOps**: Docker deployment and orchestration
- [x] **TTS**: Text-to-speech narration (Kokoro + Chatterbox)
- [ ] **Phase 7**: Image generation, achievements, and extended features
- [ ] **Phase 8**: Comprehensive testing and production deployment
- [ ] **Future**: Mobile apps for Android, story sharing, multiplayer stories

---

## 🌟 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [SwiftUI](https://developer.apple.com/xwidgets/swiftui/) - iOS UI framework
- [Ollama](https://ollama.ai/) - Local LLM platform
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://www.anthropic.com/) - Claude models
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - Fast, lightweight text-to-speech
- [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) - High-quality TTS with voice cloning
- [Docker](https://www.docker.com/) - Containerization platform
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

---

## 📞 Support

For questions, issues, or feedback:
- Open an issue on GitHub
- Check the [documentation](GETTING_STARTED.md)
- Review the [API docs](http://localhost:8000/docs) when running

---

## ⚡ Performance

StoryQuest is optimized for speed and efficiency:
- **Streaming Throttling**: 50ms update intervals reduce React re-renders by 80%
- **CSS-Only Animations**: GPU-accelerated sparkle effects without JavaScript overhead
- **Database Indexes**: Composite indexes for O(log n) query performance
- **SQLite WAL Mode**: 50% faster writes with concurrent reader support
- **Docker Multi-Stage Builds**: Minimal production images
- **React Query Caching**: Reduced API calls
- **Health Monitoring**: Automatic recovery and self-healing

For detailed performance documentation, see **[PERFORMANCE.md](PERFORMANCE.md)**.

---

**Ready to embark on an adventure?** Get started with [Docker Quick Start](#using-docker-recommended) or explore the [full documentation](GETTING_STARTED.md)!

---

<div align="center">

**[⬆ Back to Top](#-storyquest)**

Made with ❤️ for young storytellers everywhere

</div>
