# StoryQuest – LLM-Powered Kids’ Text Adventure  
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
- ✅ Story continuity via a compact “hidden state” (story so far).
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

## 2. Phases Overview

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

(omitted here for brevity but full content included earlier) 
