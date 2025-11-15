# StoryQuest – LLM-Powered Kids' Text Adventure
*A phased plan for local + cloud LLMs, with both Web UI and iPad app options*

---

## 0. Vision & Constraints

**Goal:**
Build a kid-friendly, interactive text adventure game where:

- Kids read (or listen to) a short scene.
- They can either:
  - Tap one of several suggested choices **(LLM-generated)**, or
  - Enter their **own** response.
- The story continues in a safe, whimsical, age-appropriate way.

**Key Requirements:**

- ✅ Can run with **local LLM** *or* **cloud LLM via API** (configurable).
- ✅ Future-friendly for **Web UI** *and/or* **iPad app (SwiftUI)**.
- ✅ Story continuity via a compact "hidden state" (story so far).
- ✅ Safe tone: no horror, gore, or adult themes.
- ✅ Easy to extend with:
  - Achievements / badges
  - TTS (narration)
  - Optional images (local diffusion or cloud image APIs)

---

## 1. Architecture Overview

**High-level components:**

1. **LLM Engine Layer**
   - Abstraction that supports:
     - Local LLM (e.g., Ollama, LM Studio, self-hosted API)
     - Cloud LLM (e.g., OpenAI, Anthropic, etc.) via HTTP.
2. **Story Engine / Backend**
   - Stateless REST/JSON API that:
     - Accepts current story state + player choice.
     - Calls LLM and returns the next scene and choices.
   - Written in Python (FastAPI) or Node.js (Express / Nest).
3. **Clients**
   - **Web UI** (React or similar).
   - **iPad App** (SwiftUI).
   - Both talk to the same backend API.
4. **Persistence Layer (Optional early, critical later)**
   - Store sessions, progress, achievements.
   - SQLite/Postgres or even JSON files for v1.

---

## 2. Technology Stack Recommendations

### Backend
**Primary: Python + FastAPI**
- FastAPI for high-performance async API
- Pydantic for data validation
- Python for easy LLM integration (langchain, openai, anthropic libraries)
- Alternative: Node.js + Express/NestJS

### LLM Integration
- **Local**: Ollama (easiest), LM Studio, or llama.cpp
- **Cloud**: OpenAI GPT-4o-mini, Anthropic Claude, or Gemini
- **Library**: LangChain or direct API calls

### Database
- **Phase 1-3**: SQLite (simple, file-based)
- **Production**: PostgreSQL (scalable, robust)
- **ORM**: SQLAlchemy (Python) or Prisma (Node.js)

### Frontend
- **Web**: React + TypeScript + Vite
- **Styling**: Tailwind CSS or Material-UI
- **State Management**: Zustand or React Query
- **iPad**: SwiftUI + Combine

### DevOps
- **Containerization**: Docker + Docker Compose
- **Deployment**:
  - Local: Docker
  - Cloud: Railway, Render, or Fly.io (free tiers available)
- **Monitoring**: Sentry (error tracking), Prometheus (metrics)

---

## 3. Phases Overview

- **Phase 1:** Story format & API contract
- **Phase 2:** LLM abstraction (local + cloud)
- **Phase 3:** Core Story Engine backend
- **Phase 4:** Minimal Web UI (MVP)
- **Phase 5:** iPad App (SwiftUI) client
- **Phase 6:** Safety, guardrails, and kid-friendly constraints
- **Phase 7:** Enhancements (TTS, images, achievements)
- **Phase 8:** Polish, testing, and hardening

---

## Phase 1 – Define Story Format & API Contract

**Goal:** Establish the data structures and API endpoints before writing any code.

### 1.1 Story State Format (JSON)

```json
{
  "session_id": "uuid-v4",
  "story_summary": "A compact summary of the story so far (for LLM context)",
  "current_scene": {
    "scene_id": "unique-scene-id",
    "text": "You stand at the entrance of a magical forest...",
    "timestamp": "2025-11-15T10:30:00Z"
  },
  "choices": [
    {
      "choice_id": "c1",
      "text": "Enter the forest bravely"
    },
    {
      "choice_id": "c2",
      "text": "Look for a guide"
    },
    {
      "choice_id": "c3",
      "text": "Set up camp and wait"
    }
  ],
  "metadata": {
    "turns": 5,
    "theme": "magical_forest",
    "age_range": "6-12"
  }
}
```

### 1.2 API Endpoints

#### POST /api/v1/story/start
**Request:**
```json
{
  "player_name": "Alex",
  "age_range": "6-8",
  "theme": "space_adventure" // or "magical_forest", "underwater_quest", etc.
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "story_summary": "Alex begins a space adventure.",
  "current_scene": {
    "scene_id": "scene_001",
    "text": "You're a brave space explorer about to launch your first mission...",
    "timestamp": "2025-11-15T10:30:00Z"
  },
  "choices": [
    {"choice_id": "c1", "text": "Check the spaceship controls"},
    {"choice_id": "c2", "text": "Talk to mission control"},
    {"choice_id": "c3", "text": "Look out the window"}
  ]
}
```

#### POST /api/v1/story/continue
**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "choice_id": "c1", // if using suggested choice
  "custom_input": null, // or "I want to find my cat" if free-form
  "story_summary": "Current story summary (sent by client for stateless backend)"
}
```

**Response:** Same format as /start

#### GET /api/v1/story/session/{session_id}
Retrieve full story history (for resume/review)

#### POST /api/v1/story/reset
Reset/abandon current session

### 1.3 LLM Prompt Template

```
You are a creative, kid-friendly storyteller for children aged {age_range}.

STORY SO FAR:
{story_summary}

PLAYER ACTION:
{player_choice}

RULES:
1. Keep content G-rated: no violence, scary themes, or adult content
2. Write 2-4 sentences describing what happens next
3. Generate exactly 3 fun, age-appropriate choices for what to do next
4. Use playful, encouraging language
5. Include learning opportunities (curiosity, problem-solving, kindness)
6. Make the player feel heroic and capable

Respond in this JSON format:
{
  "scene_text": "What happens next...",
  "choices": [
    "Choice 1",
    "Choice 2",
    "Choice 3"
  ],
  "story_summary_update": "Brief update to story summary"
}
```

---

## Phase 2 – LLM Abstraction Layer

**Goal:** Create a swappable interface for local vs. cloud LLMs.

### 2.1 Abstract Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List

class LLMProvider(ABC):
    @abstractmethod
    async def generate_story_continuation(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> Dict:
        """Returns parsed JSON response from LLM"""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if LLM service is available"""
        pass
```

### 2.2 Implementations

#### Local LLM (Ollama)
```python
class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate_story_continuation(self, prompt, max_tokens=500, temperature=0.8):
        # Call Ollama API
        # Parse response, ensure JSON format
        # Handle errors gracefully
        pass
```

#### Cloud LLM (OpenAI/Anthropic)
```python
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def generate_story_continuation(self, prompt, max_tokens=500, temperature=0.8):
        # Call OpenAI API with structured output
        # Parse and validate response
        pass
```

### 2.3 Configuration

```yaml
# config.yaml
llm:
  provider: "ollama"  # or "openai", "anthropic"

  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2:3b"

  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4o-mini"

  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-5-haiku-20241022"

story:
  max_turns: 50
  themes: ["magical_forest", "space_adventure", "underwater_quest", "dinosaur_discovery"]
  default_age_range: "6-12"
```

### 2.4 Factory Pattern

```python
def create_llm_provider(config: Dict) -> LLMProvider:
    provider_type = config["llm"]["provider"]

    if provider_type == "ollama":
        return OllamaProvider(**config["llm"]["ollama"])
    elif provider_type == "openai":
        return OpenAIProvider(**config["llm"]["openai"])
    elif provider_type == "anthropic":
        return AnthropicProvider(**config["llm"]["anthropic"])
    else:
        raise ValueError(f"Unknown provider: {provider_type}")
```

---

## Phase 3 – Core Story Engine Backend

**Goal:** Build the stateless API that orchestrates LLM calls and story logic.

### 3.1 Project Structure

```
storyquest-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Configuration loading
│   ├── models/
│   │   ├── story.py         # Pydantic models
│   │   └── session.py
│   ├── services/
│   │   ├── llm_provider.py  # LLM abstraction
│   │   ├── story_engine.py  # Core story logic
│   │   └── safety_filter.py # Content moderation
│   ├── api/
│   │   └── v1/
│   │       └── story.py     # API endpoints
│   └── db/
│       ├── database.py
│       └── models.py        # SQLAlchemy models
├── tests/
├── config.yaml
├── requirements.txt
└── Dockerfile
```

### 3.2 Core Story Engine Logic

```python
class StoryEngine:
    def __init__(self, llm_provider: LLMProvider, safety_filter: SafetyFilter):
        self.llm = llm_provider
        self.safety = safety_filter

    async def start_story(self, player_name: str, age_range: str, theme: str):
        # Generate initial scene
        # Create session
        # Return story state
        pass

    async def continue_story(self, session_id: str, choice_id: str, custom_input: str):
        # Load session
        # Build prompt from story_summary + choice
        # Filter custom_input through safety check
        # Call LLM
        # Parse and validate response
        # Update session
        # Return new story state
        pass
```

### 3.3 Database Schema

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_name VARCHAR(100),
    age_range VARCHAR(10),
    theme VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    turns INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE story_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    turn_number INTEGER,
    scene_text TEXT,
    player_choice TEXT,
    custom_input TEXT,
    story_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_session_turns ON story_turns(session_id, turn_number);
```

### 3.4 Error Handling

- Implement retry logic for LLM calls (max 3 retries with exponential backoff)
- Fallback responses if LLM fails
- Rate limiting per session (prevent abuse)
- Timeout handling (LLM calls max 30 seconds)
- Graceful degradation if database is unavailable

---

## Phase 4 – Minimal Web UI (MVP)

**Goal:** Build a simple, functional web interface to test the story engine.

### 4.1 Tech Stack
- React 18 + TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Query for API state management

### 4.2 Key Components

```typescript
// Story View
interface StoryViewProps {
  scene: Scene;
  choices: Choice[];
  onChoiceSelect: (choiceId: string) => void;
  onCustomInput: (input: string) => void;
}

// Choice Button
interface ChoiceButtonProps {
  choice: Choice;
  onClick: () => void;
}

// Custom Input Box
interface CustomInputProps {
  onSubmit: (text: string) => void;
  disabled: boolean;
}

// Story History (expandable)
interface StoryHistoryProps {
  turns: Turn[];
}
```

### 4.3 Features

- Start new story with theme selection
- Display current scene with formatted text
- Show 3 suggested choices as buttons
- Custom input text box with character limit
- Loading states while LLM generates
- Error messages with retry button
- Story history (collapsible)
- Reset/restart button
- Responsive design (mobile-friendly)

### 4.4 Accessibility
- Semantic HTML
- ARIA labels for screen readers
- Keyboard navigation
- High contrast mode support
- Large, readable fonts (Comic Sans or similar kid-friendly font)

---

## Phase 5 – iPad App (SwiftUI)

**Goal:** Native iOS/iPadOS experience with offline capability.

### 5.1 Architecture

```
StoryQuestApp/
├── Models/
│   ├── StorySession.swift
│   ├── Scene.swift
│   └── Choice.swift
├── Services/
│   ├── APIClient.swift
│   ├── StorageService.swift (Core Data)
│   └── AudioService.swift (TTS)
├── Views/
│   ├── StoryView.swift
│   ├── ChoiceButtonView.swift
│   ├── ThemeSelectionView.swift
│   └── SettingsView.swift
└── ViewModels/
    └── StoryViewModel.swift
```

### 5.2 Key Features

- Native SwiftUI interface
- Core Data for offline story caching
- AVFoundation for text-to-speech
- Haptic feedback for choices
- Dark mode support
- Parental controls (time limits, content filters)
- iCloud sync for story progress (optional)

### 5.3 Offline Mode

- Cache last 10 scenes locally
- Download LLM responses when online
- Queue user choices when offline
- Sync when connection restored
- Indicate offline status clearly

---

## Phase 6 – Safety, Guardrails & Kid-Friendly Constraints

**Goal:** Ensure all content is age-appropriate and safe.

### 6.1 Content Moderation Pipeline

```python
class SafetyFilter:
    def __init__(self):
        self.banned_words = self.load_banned_words()
        self.inappropriate_patterns = self.load_patterns()

    async def filter_user_input(self, text: str) -> tuple[bool, str]:
        """
        Returns: (is_safe, sanitized_text or reason)
        """
        # Check for banned words
        # Check for inappropriate patterns
        # Use OpenAI Moderation API as backup
        # Return filtered text or rejection reason
        pass

    async def validate_llm_output(self, scene_text: str) -> bool:
        """
        Ensure LLM output is appropriate
        """
        # Check for policy violations
        # Verify tone is positive/encouraging
        # Ensure no scary/violent content
        pass
```

### 6.2 Safety Mechanisms

1. **Input Validation**
   - Max length: 200 characters
   - No URLs or email addresses
   - No personal information (phone numbers, addresses)
   - Banned word list filtering
   - Pattern matching for inappropriate content

2. **LLM System Prompts**
   - Explicit safety rules in every prompt
   - Temperature capping (max 0.9)
   - Include examples of good responses
   - Penalize scary/negative content

3. **Output Validation**
   - Secondary moderation API check (OpenAI Moderation)
   - Regex patterns for violence/horror keywords
   - Sentiment analysis (must be neutral-to-positive)
   - Automatic fallback response if content fails check

4. **Rate Limiting**
   - Max 20 turns per session per hour
   - Max 5 custom inputs per 10 minutes
   - IP-based rate limiting for API

5. **Human Review**
   - Log all flagged content
   - Weekly review of edge cases
   - Community reporting feature (later phase)

### 6.3 Age-Appropriate Themes

**6-8 years:**
- Simple vocabulary
- Clear cause-and-effect
- Friendly characters
- No complex moral dilemmas

**9-12 years:**
- More complex vocabulary
- Light puzzles and challenges
- Character development
- Age-appropriate problem-solving

---

## Phase 7 – Enhancements (TTS, Images, Achievements)

### 7.1 Text-to-Speech (TTS)

**Web:**
- Use Web Speech API (browser-native)
- Fallback: Cloud TTS (Google Cloud TTS, Amazon Polly)
- Voice selection (kid-friendly voices)

**iPad:**
- AVSpeechSynthesizer (native iOS)
- Adjustable speed and pitch
- Read-along highlighting

### 7.2 Image Generation (Optional)

**Local:**
- Stable Diffusion via ComfyUI or Automatic1111
- Generate scene illustrations on-demand
- Cache images per scene

**Cloud:**
- DALL-E 3, Midjourney, or Stable Diffusion API
- Cost consideration: ~$0.04 per image
- Moderation required for all generated images

**Implementation:**
- Async generation (don't block story)
- Show placeholder while generating
- Store images in CDN/S3

### 7.3 Achievements & Badges

```json
{
  "achievement_id": "first_adventure",
  "title": "First Adventure",
  "description": "Completed your first story",
  "icon_url": "/badges/first_adventure.png",
  "unlocked_at": "2025-11-15T10:30:00Z"
}
```

**Achievement Types:**
- Story completion
- Choice variety (try all choices in a scene)
- Custom input usage
- Theme completion (finish story in each theme)
- Kindness choices (select helpful options)
- Curiosity (explore all options)

### 7.4 Parental Dashboard

- View child's story history
- Content filter settings
- Time limit controls
- Activity reports
- Achievement tracking

---

## Phase 8 – Polish, Testing & Hardening

### 8.1 Testing Strategy

**Unit Tests:**
- LLM provider implementations
- Story engine logic
- Safety filter rules
- API request/response validation

**Integration Tests:**
- Full story flow (start to finish)
- LLM provider switching
- Database operations
- API endpoint coverage

**End-to-End Tests:**
- Web UI user flows (Playwright/Cypress)
- iPad app UI tests (XCTest)
- Multi-session handling
- Error recovery scenarios

**Load Testing:**
- 100 concurrent users
- 1000 requests/minute
- Database connection pooling
- LLM rate limit handling

### 8.2 Performance Optimization

- Response caching (Redis)
- Database query optimization (indexes)
- LLM response streaming (SSE)
- Image lazy loading
- CDN for static assets
- Compression (gzip/brotli)

### 8.3 Monitoring & Observability

```yaml
Metrics to Track:
  - API response times (p50, p95, p99)
  - LLM call duration
  - Error rates per endpoint
  - Active sessions
  - Database query performance
  - Custom input safety rejections
  - User engagement (turns per session)

Logging:
  - Structured JSON logs
  - Log levels: DEBUG, INFO, WARN, ERROR
  - Correlation IDs for request tracing
  - PII scrubbing (never log user input verbatim in prod)

Alerting:
  - API error rate > 5%
  - LLM provider downtime
  - Database connection failures
  - Safety filter violations > threshold
```

### 8.4 Security Hardening

- HTTPS only (TLS 1.3)
- CORS configuration (whitelist domains)
- API key rotation strategy
- Environment variable management (never commit secrets)
- Input sanitization (prevent XSS, SQL injection)
- Rate limiting (per IP, per session)
- OWASP Top 10 compliance
- Regular dependency updates
- Security audit before launch

### 8.5 Documentation

- API documentation (OpenAPI/Swagger)
- Deployment guide (Docker, cloud platforms)
- Development setup (local LLM installation)
- Architecture decision records (ADRs)
- User guide for parents
- Troubleshooting guide

---

## 9. Deployment Strategy

### 9.1 Local Development

```bash
# Backend
cd storyquest-backend
docker-compose up  # Starts FastAPI + PostgreSQL + Ollama

# Frontend
cd storyquest-web
npm run dev
```

### 9.2 Production Deployment

**Option A: Docker Compose (VPS)**
```yaml
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/storyquest
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
```

**Option B: Cloud Platform (Render/Railway)**
- Backend: Deploy as Web Service
- Frontend: Deploy as Static Site
- Database: Managed PostgreSQL
- Environment variables in dashboard

**Option C: Kubernetes (Scalable)**
- Use Helm charts
- Auto-scaling based on load
- Managed database (AWS RDS, Google Cloud SQL)

### 9.3 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend && pytest
          cd frontend && npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          # Trigger Render deployment
```

---

## 10. Cost Estimation

### Local Deployment
- Server: $5-20/month (VPS like DigitalOcean, Hetzner)
- Domain: $12/year
- SSL: Free (Let's Encrypt)
- **Total: ~$10-25/month**

### Cloud LLM (OpenAI GPT-4o-mini)
- ~500 tokens per story turn
- $0.15 per 1M input tokens, $0.60 per 1M output tokens
- 10,000 turns/month ≈ $5-10/month
- **Total: ~$20-40/month** (including hosting)

### Scaling (1000 active users)
- Database: $25/month (managed PostgreSQL)
- Backend: $50/month (auto-scaling)
- LLM costs: $200-500/month
- CDN: $10/month
- **Total: ~$300-600/month**

---

## 11. Success Metrics

### Technical Metrics
- API uptime: >99.5%
- Median response time: <2 seconds
- LLM generation time: <5 seconds
- Error rate: <1%

### User Engagement
- Average session length: >10 turns
- Return rate: >30% (users come back)
- Custom input usage: >20% of turns
- Story completion rate: >40%

### Safety Metrics
- Safety filter accuracy: >98%
- False positive rate: <5%
- Zero policy violations reaching users

---

## 12. Future Enhancements (Post-Launch)

- **Multiplayer stories** (collaborative adventures with friends)
- **Story sharing** (publish favorite adventures)
- **Custom themes** (parents create themed stories)
- **Educational content** (math, science, history themes)
- **Voice input** (kids speak their choices)
- **Multilingual support** (Spanish, French, Mandarin)
- **AR mode** (visualize scenes in AR on iPad)
- **Story remix** (replay with different choices)
- **Character customization** (choose avatar, personality traits)

---

## 13. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM generates inappropriate content | Medium | High | Multi-layer safety filters, human review, fallback responses |
| LLM API costs exceed budget | Medium | Medium | Rate limiting, local LLM fallback, usage caps |
| User privacy concerns | Low | High | Minimal data collection, clear privacy policy, no PII storage |
| Technical complexity too high | Medium | Medium | Phased approach, MVP first, iterate based on feedback |
| Low user engagement | Medium | Medium | Focus on fun, test with kids early, iterate on feedback |
| Platform policy violations (App Store) | Low | High | Follow guidelines strictly, content moderation, age ratings |

---

## 14. Timeline Estimate

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: API Design | 3-5 days | 1 developer |
| Phase 2: LLM Layer | 5-7 days | 1 developer |
| Phase 3: Backend | 10-14 days | 1-2 developers |
| Phase 4: Web UI | 7-10 days | 1 frontend developer |
| Phase 5: iPad App | 14-21 days | 1 iOS developer |
| Phase 6: Safety | 7-10 days | 1 developer + testing |
| Phase 7: Enhancements | 10-14 days | 1-2 developers |
| Phase 8: Testing & Polish | 14-21 days | Full team |

**Total: ~3-4 months with 2-3 developers**

**MVP (Phases 1-4 + basic Phase 6): ~6-8 weeks**

---

## Conclusion

This plan provides a complete roadmap for building StoryQuest, a safe, engaging text adventure game for kids. The architecture is flexible (local or cloud LLMs), scalable (stateless API), and multi-platform (web + iPad).

**Key Success Factors:**
1. **Safety first** – Multiple layers of content moderation
2. **Start small** – MVP with web UI before iPad app
3. **Iterate fast** – Test with real kids early and often
4. **Keep it simple** – Focus on core experience before adding features
5. **Measure everything** – Track engagement and safety metrics

**Next Steps:**
1. Set up development environment
2. Implement Phase 1 (API contract)
3. Build Phase 2 (LLM abstraction with Ollama)
4. Test with local LLM before cloud deployment
5. Iterate based on user feedback

Good luck building StoryQuest! 🚀
