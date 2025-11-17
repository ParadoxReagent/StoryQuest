# StoryQuest iOS/iPadOS Plan (Revised)

## Purpose
Create a native SwiftUI iPad experience that matches the current StoryQuest backend (FastAPI with multiple LLM providers, safety filters, and SQL-backed story sessions) and complements the existing web frontend. The plan prioritizes fast delivery of a playable beta, reuse of backend contracts, and a clear path to App Store readiness.

## Guiding Principles
- **Kid-first UX:** big tap targets, friendly tone, VoiceOver-ready, and low cognitive load.
- **Reuse the backend contract:** follow the existing REST models for sessions, turns, safety messages, and health checks.
- **Offline-aware:** graceful handling of flaky connectivity with resumable sessions and local caching of history.
- **Safety-first:** surface backend safety messages and keep all user-generated inputs within policy.
- **Incremental delivery:** ship in vertical slices (API → Theme picker → Storyplay) to keep the app always demoable.

## Architecture Snapshot
- **Framework:** SwiftUI + Combine (iOS 16+).
- **Project layout:**
  - `App/` entry + DI bootstrap
  - `Features/ThemeSelection`, `Features/Story`, `Features/History`, `Features/Settings`
  - `Core/Networking`, `Core/Models` (mirroring backend schemas), `Core/Services`, `Core/Storage`
  - `Resources/` for assets, colors, and localized strings
- **Networking:** `APIClient` using `URLSession` with async/await, request builders that mirror backend routes (`/health`, `/sessions`, `/sessions/{id}/turns`).
- **State:** Feature-specific `ObservableObject` view models; shared `AppState` for auth/config and active session.
- **Storage:** Core Data for saved sessions/turns, plus lightweight on-disk cache for preferences.
- **TTS:** AVSpeechSynthesizer wrapper with per-story settings.
- **Testing:** XCTest + ViewInspector for SwiftUI views; integration tests hitting a local backend.

## Milestones

### M1 – Project Bootstrap (Week 1)
- Create Xcode project (SwiftUI, iOS 16+), set up bundle identifiers, SwiftLint/SwiftFormat.
- Add shared design tokens (colors, typography), SF Symbols set, and sample themes.
- Implement `APIConfig` (base URL, API key if used) and `HealthCheckService`.
- Deliverable: Compiles on device/simulator; health check succeeds against backend.

### M2 – Backend Contract & Models (Week 1-2)
- Define Codable models matching backend responses: Session, StoryTurn, Choice, SafetyStatus, ErrorEnvelope.
- Implement `StoryAPI` client methods: create session, submit choice, submit custom input, fetch history if available.
- Add stubbed API fixtures for offline UI previews and unit tests.
- Deliverable: Network layer with unit tests that decode current backend samples.

### M3 – Theme Selection (Week 2)
- Build `ThemeSelectionView` with grid layout, age range selector, player name entry, and Start button.
- Wire to `ThemeSelectionViewModel` that calls `createSession(theme, ageRange, name)`.
- Handle loading/error states and surface backend safety responses gracefully.
- Deliverable: Start flow creates a session and navigates to Story view.

### M4 – Story Experience (Week 3)
- Implement `StoryView` showing current scene text, three choice buttons, and optional freeform input.
- Add turn history panel/modal; smooth transition animations between turns.
- Connect `StoryViewModel` to `StoryAPI` for posting choices/inputs and updating story state.
- Integrate optimistic updates with backend fallbacks and error retry.
- Deliverable: End-to-end playable story with backend responses.

### M5 – Text-to-Speech & Accessibility (Week 4)
- Add `TTSService` with play/pause/stop, voice selection, speed slider, and text highlighting while speaking (if feasible).
- Apply accessibility traits: VoiceOver labels, Dynamic Type where possible, color contrast checks, haptics for key actions.
- Deliverable: Read-aloud flow working in StoryView with persisted preferences.

### M6 – Offline & Persistence (Week 5)
- Design Core Data schema for sessions/turns aligning with backend IDs.
- Auto-save turns after each backend response; allow resuming last session offline with cached text.
- Create `HistoryListView` and `HistoryDetailView` for browsing and replaying saved stories.
- Deliverable: Offline viewing of prior sessions; storage limits and deletion supported.

### M7 – Settings & Safety (Week 6)
- Add Settings screen for model/provider selection (if exposed), content filters, TTS defaults, analytics opt-in, and clear data.
- Show safety notices inline (e.g., if backend returns filtered content) and log events for troubleshooting.
- Implement parental gate for settings and external links.
- Deliverable: Configurable experience that respects safety and privacy requirements.

### M8 – QA Hardening (Week 7)
- Unit tests for view models/services; snapshot tests for key views; UI tests for start-to-finish story.
- Performance checks (launch time, turn latency), network resilience tests, and accessibility audit.
- Deliverable: Test suite with >70% coverage on core logic and passing smoke tests on iPad models.

### M9 – Release Prep (Week 8)
- App icon, launch screen, App Store metadata, and privacy details.
- TestFlight build with release notes and parent tester cohort; capture feedback survey.
- Finalize crash/analytics tooling (if allowed) and ensure safety/privacy documentation matches implementation.
- Deliverable: Submission-ready build.

## Data & API Notes
- Ensure request/response payloads mirror the FastAPI backend (Pydantic schemas in `backend/app/schemas`).
- Handle safety filter responses explicitly (blocked content, age gating) with friendly UI messages.
- Prefer streaming responses if exposed; otherwise use polling with cancellable tasks.

## Risks & Mitigations
- **LLM latency:** cache last turn, show playful loaders, and keep choice buttons responsive; consider abbreviated summaries for long history.
- **Offline gaps:** queue user inputs until online; mark unsent turns and reconcile when connectivity returns.
- **App review sensitivities:** enforce parental gate, disable external sharing by default, ensure COPPA-friendly language.

## Definition of Done (per milestone)
- Feature implemented with SwiftUI and unit/UI tests where applicable.
- Works on latest iPadOS simulator and at least one physical device target.
- Respects accessibility, safety, and performance guidelines.
- Documented in `README` or inline comments where behavior is non-obvious.

## Next Steps
1. Generate sample JSON from current backend endpoints to lock codecs/tests.
2. Create Xcode project skeleton with modules and SwiftLint/SwiftFormat.
3. Implement health check + Theme selection slice and demo against running backend.
