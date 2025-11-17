# StoryQuest iOS/iPadOS App - Implementation Plan (Revised for Phase 6)
## Native iPad Application with Enhanced Backend Integration

---

## Table of Contents

1. [Revision Overview](#revision-overview)
2. [Updated Backend Capabilities](#updated-backend-capabilities)
3. [Technology Stack](#technology-stack)
4. [Architecture](#architecture)
5. [Updated Data Models](#updated-data-models)
6. [Updated API Integration](#updated-api-integration)
7. [Streaming Implementation](#streaming-implementation)
8. [Enhanced Rate Limiting Handling](#enhanced-rate-limiting-handling)
9. [Dynamic Theme Generation](#dynamic-theme-generation)
10. [Implementation Phases](#implementation-phases)
11. [UI/UX Design Updates](#uiux-design-updates)
12. [Core Features](#core-features)
13. [Testing Strategy](#testing-strategy)
14. [Deployment](#deployment)

---

## Revision Overview

### What Changed Since Original Plan

The StoryQuest backend has evolved significantly since the original iOS plan:

**Major Backend Enhancements:**
- ✅ **Server-Sent Events (SSE)** streaming for real-time story generation
- ✅ **Dynamic theme generation** endpoint (`/generate-themes`)
- ✅ **Enhanced safety system** with 130+ banned words and sentiment analysis
- ✅ **Sophisticated rate limiting** (6 different limit types)
- ✅ **6 LLM providers** (Ollama, OpenAI, Anthropic, Gemini, OpenRouter, LM Studio)
- ✅ **Dynamic max turns** (8-15 per session, deterministic based on session_id)
- ✅ **story_summary requirement** for stateless continuation
- ✅ **Enhanced metadata** with `max_turns` and `is_finished` fields
- ✅ **Session history endpoint** for retrieving full story playback

**Impact on iOS App:**
- Must support SSE streaming for better UX (show text as it generates)
- Can fetch themes dynamically instead of hardcoding
- Must handle 429 rate limit errors with retry logic
- Must track and pass `story_summary` with continuation requests
- Must display dynamic max turns and completion status
- Better error handling for safety violations

### Revised Goals

1. ✅ **Stream story generation** in real-time using SSE
2. ✅ **Dynamic theme loading** from backend
3. ✅ **Robust rate limit handling** with user-friendly messaging
4. ✅ **Enhanced metadata tracking** (max_turns, is_finished, etc.)
5. ✅ **Maintain original vision** (TTS, offline, kid-friendly)

---

## Updated Backend Capabilities

### Available API Endpoints

#### Story Endpoints (Base: `/api/v1/story`)

1. **POST /start** - Start new story (non-streaming)
   - Request: `{player_name, age_range, theme}`
   - Response: `StoryResponse` with session_id, scene, choices, metadata
   - Rate Limit: 10 starts/hour per IP

2. **POST /start/stream** - Start new story with SSE streaming ⭐ NEW
   - Same request format
   - Streams: `session_start`, `text_chunk`, `complete` events
   - Better UX: Show text as it generates

3. **POST /continue** - Continue story (non-streaming)
   - Request: `{session_id, choice_id?, choice_text?, custom_input?, story_summary}` ⚠️ story_summary required
   - Response: `StoryResponse` with next scene
   - Rate Limits: 20 turns/hour, 100 turns/day per session

4. **POST /continue/stream** - Continue story with SSE streaming ⭐ NEW
   - Same request format
   - Streams text in real-time

5. **GET /session/{session_id}** - Get session history ⭐ NEW
   - Returns full session with all turns
   - Useful for offline replay and debugging

6. **POST /reset** - Reset/abandon session
   - Sets session to inactive

7. **POST /generate-themes** - Generate dynamic themes ⭐ NEW
   - Request: `{age_range}`
   - Response: 6 themes with `{id, name, description, emoji, color}`
   - Allows fresh themes without app updates

### Response Structure Changes

**Enhanced StoryMetadata:**
```json
{
  "turns": 3,
  "theme": "space_adventure",
  "age_range": "6-8",
  "max_turns": 12,        // ⭐ NEW: Dynamic max (8-15)
  "is_finished": false    // ⭐ NEW: Story completion flag
}
```

**StoryResponse now includes:**
- `story_summary`: Required for continuation requests
- `metadata.max_turns`: Deterministic max for this session
- `metadata.is_finished`: True when story is complete

### Rate Limiting Details

**6 Rate Limit Types:**
1. Start per IP: 10/hour
2. Session turns: 20/hour, 100/day
3. Custom input: 5/10 minutes (stricter)
4. IP general: 50/hour, 200/day
5. Session-based tracking
6. IP-based tracking

**iOS App Must Handle:**
- 429 HTTP responses with `Retry-After` header
- Graceful degradation (disable buttons, show countdown)
- User-friendly error messages ("Try again in 45 seconds")

---

## Technology Stack

### Core Technologies (Unchanged)

- **Swift 5.9+**: Modern, type-safe language
- **SwiftUI**: Declarative UI framework
- **Combine**: Reactive programming for data flow
- **AVFoundation**: Text-to-speech synthesis
- **Core Data**: Local persistence
- **URLSession**: Networking and API calls

### New/Updated Components

- ✅ **URLSessionStreamDelegate**: For SSE event handling
- ✅ **AsyncStream**: Swift concurrency for streaming
- ✅ **@MainActor**: Thread-safe UI updates from streams
- ✅ **TaskGroup**: Concurrent operations (theme loading + health check)

### No External Dependencies

All features implemented with native iOS frameworks.

---

## Architecture

### MVVM Pattern (Enhanced for Streaming)

```
┌─────────────────────────────────────────────────────┐
│                    Views (SwiftUI)                  │
│  ThemeSelectionView, StoryView, StreamingTextView  │
└────────────────┬────────────────────────────────────┘
                 │ @Published bindings
┌────────────────▼────────────────────────────────────┐
│              ViewModels (@MainActor)                │
│  StoryViewModel, ThemeViewModel (async/await)       │
└────────────────┬────────────────────────────────────┘
                 │ Uses
┌────────────────▼────────────────────────────────────┐
│                 Services                            │
│  APIService (streaming), TTSService, StorageService │
└────────────────┬────────────────────────────────────┘
                 │ Operates on
┌────────────────▼────────────────────────────────────┐
│                  Models                             │
│  Story, Scene, Choice, Theme, StoryMetadata         │
└─────────────────────────────────────────────────────┘
```

### Updated Project Structure

```
StoryQuest-iOS/
├── StoryQuest/
│   ├── App/
│   │   ├── StoryQuestApp.swift
│   │   └── AppEnvironment.swift
│   ├── Models/
│   │   ├── Story.swift                   # Updated with new metadata
│   │   ├── Scene.swift
│   │   ├── Choice.swift
│   │   ├── Session.swift                 # Updated for session history
│   │   ├── Theme.swift                   # Dynamic theme support
│   │   └── StreamEvent.swift            ⭐ NEW: SSE event models
│   ├── ViewModels/
│   │   ├── StoryViewModel.swift          # Updated for streaming
│   │   ├── ThemeViewModel.swift          # Dynamic theme loading
│   │   └── HistoryViewModel.swift
│   ├── Views/
│   │   ├── Theme/
│   │   │   ├── ThemeSelectionView.swift
│   │   │   └── ThemeCard.swift          # Dynamic themes
│   │   ├── Story/
│   │   │   ├── StoryView.swift
│   │   │   ├── StreamingSceneView.swift ⭐ NEW: Streaming text display
│   │   │   ├── ChoiceButtonView.swift
│   │   │   ├── CustomInputView.swift
│   │   │   └── MetadataView.swift       ⭐ NEW: Shows turns/max_turns
│   │   ├── Shared/
│   │   │   ├── LoadingView.swift
│   │   │   ├── ErrorView.swift
│   │   │   └── RateLimitView.swift      ⭐ NEW: Rate limit messaging
│   ├── Services/
│   │   ├── APIService.swift              # Updated with streaming
│   │   ├── StreamingService.swift       ⭐ NEW: SSE handling
│   │   ├── TTSService.swift
│   │   └── StorageService.swift
│   └── Utilities/
│       ├── Constants.swift
│       ├── Extensions.swift
│       └── RateLimitTracker.swift       ⭐ NEW: Client-side rate limit tracking
```

---

## Updated Data Models

### Core Models with Backend Changes

```swift
import Foundation

// MARK: - Story Metadata (Updated)

struct StoryMetadata: Codable {
    let turns: Int
    let theme: String
    let ageRange: String
    let maxTurns: Int              // ⭐ NEW: Dynamic max (8-15)
    let isFinished: Bool            // ⭐ NEW: Completion status

    enum CodingKeys: String, CodingKey {
        case turns
        case theme
        case ageRange = "age_range"
        case maxTurns = "max_turns"
        case isFinished = "is_finished"
    }
}

// MARK: - Story Response (Updated)

struct StoryResponse: Codable {
    let sessionId: UUID
    let storySummary: String        // ⭐ REQUIRED for continue requests
    let currentScene: Scene
    let choices: [Choice]
    let metadata: StoryMetadata

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case storySummary = "story_summary"
        case currentScene = "current_scene"
        case choices
        case metadata
    }
}

// MARK: - Continue Request (Updated)

struct ContinueStoryRequest: Codable {
    let sessionId: UUID
    let choiceId: String?
    let choiceText: String?
    let customInput: String?
    let storySummary: String        // ⭐ REQUIRED

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case choiceId = "choice_id"
        case choiceText = "choice_text"
        case customInput = "custom_input"
        case storySummary = "story_summary"
    }
}

// MARK: - Dynamic Theme (New)

struct Theme: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
    let emoji: String               // ⭐ NEW: Backend provides emoji
    let color: String               // ⭐ NEW: Tailwind gradient class

    // Convert Tailwind gradient to SwiftUI gradient
    var gradient: LinearGradient {
        // Parse "from-indigo-400 to-purple-500" -> SwiftUI gradient
        // Implementation in Extensions.swift
        GradientParser.parse(color)
    }
}

// MARK: - Theme Generation Request/Response

struct GenerateThemesRequest: Codable {
    let ageRange: String

    enum CodingKeys: String, CodingKey {
        case ageRange = "age_range"
    }
}

struct GenerateThemesResponse: Codable {
    let themes: [Theme]
}

// MARK: - Session History (New)

struct SessionHistory: Codable {
    let sessionId: UUID
    let playerName: String
    let ageRange: String
    let theme: String
    let createdAt: Date
    let lastActivity: Date
    let totalTurns: Int
    let isActive: Bool
    let turns: [SessionTurn]

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case playerName = "player_name"
        case ageRange = "age_range"
        case theme
        case createdAt = "created_at"
        case lastActivity = "last_activity"
        case totalTurns = "total_turns"
        case isActive = "is_active"
        case turns
    }
}

struct SessionTurn: Codable, Identifiable {
    let id: UUID
    let turnNumber: Int
    let sceneText: String
    let sceneId: String
    let playerChoice: String?
    let customInput: String?
    let storySummary: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case turnNumber = "turn_number"
        case sceneText = "scene_text"
        case sceneId = "scene_id"
        case playerChoice = "player_choice"
        case customInput = "custom_input"
        case storySummary = "story_summary"
        case createdAt = "created_at"
    }
}

// MARK: - Streaming Events (New)

enum StreamEventType: String, Codable {
    case sessionStart = "session_start"
    case textChunk = "text_chunk"
    case complete = "complete"
    case error = "error"
}

struct StreamEvent: Codable {
    let type: StreamEventType
    let sessionId: UUID?
    let content: String?
    let sceneText: String?
    let choices: [Choice]?
    let metadata: StoryMetadata?
    let storySummary: String?
    let message: String?

    enum CodingKeys: String, CodingKey {
        case type
        case sessionId = "session_id"
        case content
        case sceneText = "scene_text"
        case choices
        case metadata
        case storySummary = "story_summary"
        case message
    }
}

// MARK: - Error Response

struct ErrorResponse: Codable {
    let detail: String
}

// MARK: - Rate Limit Error

struct RateLimitError: Error {
    let retryAfter: Int  // seconds
    let message: String
}
```

---

## Updated API Integration

### APIService with Streaming Support

```swift
import Foundation
import Combine

enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case serverError(String)
    case rateLimitExceeded(retryAfter: Int)
    case safetyViolation(String)
}

@MainActor
class APIService: ObservableObject {
    static let shared = APIService()

    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()

    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 90  // LLM can be slow
        config.timeoutIntervalForResource = 120
        self.session = URLSession(configuration: config)
    }

    // MARK: - Non-Streaming Endpoints

    func startStory(request: StartStoryRequest) async throws -> StoryResponse {
        let url = URL(string: "\(baseURL)/api/v1/story/start")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        return try JSONDecoder.storyQuestDecoder.decode(StoryResponse.self, from: data)
    }

    func continueStory(request: ContinueStoryRequest) async throws -> StoryResponse {
        let url = URL(string: "\(baseURL)/api/v1/story/continue")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        return try JSONDecoder.storyQuestDecoder.decode(StoryResponse.self, from: data)
    }

    // ⭐ NEW: Dynamic Theme Generation
    func generateThemes(ageRange: String) async throws -> [Theme] {
        let url = URL(string: "\(baseURL)/api/v1/story/generate-themes")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let request = GenerateThemesRequest(ageRange: ageRange)
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        let result = try JSONDecoder.storyQuestDecoder.decode(GenerateThemesResponse.self, from: data)
        return result.themes
    }

    // ⭐ NEW: Get Session History
    func getSessionHistory(sessionId: UUID) async throws -> SessionHistory {
        let url = URL(string: "\(baseURL)/api/v1/story/session/\(sessionId.uuidString)")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        return try JSONDecoder.storyQuestDecoder.decode(SessionHistory.self, from: data)
    }

    func resetSession(sessionId: UUID) async throws {
        let url = URL(string: "\(baseURL)/api/v1/story/reset")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let request = ["session_id": sessionId.uuidString]
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: request)

        let (_, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)
    }

    // MARK: - HTTP Response Handling

    private func handleHTTPResponse(_ response: URLResponse) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return

        case 400:
            // Safety violation or validation error
            throw APIError.safetyViolation("Your input was filtered for safety. Please try something else!")

        case 404:
            throw APIError.serverError("Session not found")

        case 429:
            // Rate limit exceeded
            let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After")
            let seconds = Int(retryAfter ?? "60") ?? 60
            throw APIError.rateLimitExceeded(retryAfter: seconds)

        case 500...599:
            throw APIError.serverError("Server error. Please try again later.")

        default:
            throw APIError.invalidResponse
        }
    }

    func healthCheck() async throws -> Bool {
        let url = URL(string: "\(baseURL)/health")!
        let (_, response) = try await session.data(from: url)
        return (response as? HTTPURLResponse)?.statusCode == 200
    }
}

// MARK: - JSON Decoder Extension

extension JSONDecoder {
    static var storyQuestDecoder: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}
```

---

## Streaming Implementation

### StreamingService for SSE

```swift
import Foundation

@MainActor
class StreamingService: ObservableObject {
    @Published var streamingText: String = ""
    @Published var isStreaming: Bool = false
    @Published var streamError: String?

    private let baseURL: String
    private var streamTask: URLSessionDataTask?

    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL
    }

    // MARK: - Start Story Stream

    func startStoryStream(
        request: StartStoryRequest,
        onSessionStart: @escaping (UUID) -> Void,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        let url = URL(string: "\(baseURL)/api/v1/story/start/stream")!
        streamStory(url: url, request: request, onSessionStart: onSessionStart, onComplete: onComplete)
    }

    // MARK: - Continue Story Stream

    func continueStoryStream(
        request: ContinueStoryRequest,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        let url = URL(string: "\(baseURL)/api/v1/story/continue/stream")!
        streamStory(url: url, request: request, onSessionStart: { _ in }, onComplete: onComplete)
    }

    // MARK: - Generic Stream Handler

    private func streamStory<T: Encodable>(
        url: URL,
        request: T,
        onSessionStart: @escaping (UUID) -> Void,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        streamingText = ""
        isStreaming = true
        streamError = nil

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("text/event-stream", forHTTPHeaderField: "Accept")

        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            streamError = "Failed to encode request"
            isStreaming = false
            return
        }

        let session = URLSession.shared
        streamTask = session.dataTask(with: urlRequest) { [weak self] data, response, error in
            guard let self = self else { return }

            Task { @MainActor in
                if let error = error {
                    self.streamError = error.localizedDescription
                    self.isStreaming = false
                    return
                }

                guard let data = data else {
                    self.streamError = "No data received"
                    self.isStreaming = false
                    return
                }

                self.processSSEData(data, onSessionStart: onSessionStart, onComplete: onComplete)
            }
        }

        streamTask?.resume()
    }

    // MARK: - SSE Data Processing

    private func processSSEData(
        _ data: Data,
        onSessionStart: @escaping (UUID) -> Void,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        guard let text = String(data: data, encoding: .utf8) else {
            streamError = "Failed to decode stream data"
            isStreaming = false
            return
        }

        let lines = text.components(separatedBy: "\n")
        var accumulatedText = ""

        for line in lines {
            // SSE format: "data: {json}"
            if line.hasPrefix("data: ") {
                let jsonString = String(line.dropFirst(6))  // Remove "data: "

                do {
                    let event = try JSONDecoder.storyQuestDecoder.decode(StreamEvent.self, from: jsonString.data(using: .utf8)!)

                    switch event.type {
                    case .sessionStart:
                        if let sessionId = event.sessionId {
                            onSessionStart(sessionId)
                        }

                    case .textChunk:
                        if let content = event.content {
                            accumulatedText += content
                            streamingText = accumulatedText
                        }

                    case .complete:
                        // Build StoryResponse from complete event
                        if let sceneText = event.sceneText,
                           let choices = event.choices,
                           let metadata = event.metadata,
                           let storySummary = event.storySummary,
                           let sessionId = event.sessionId {

                            let scene = Scene(
                                id: "scene_\(sessionId)_\(metadata.turns)",
                                text: sceneText,
                                timestamp: Date()
                            )

                            let response = StoryResponse(
                                sessionId: sessionId,
                                storySummary: storySummary,
                                currentScene: scene,
                                choices: choices,
                                metadata: metadata
                            )

                            onComplete(response)
                        }

                        isStreaming = false

                    case .error:
                        streamError = event.message ?? "Unknown error"
                        isStreaming = false
                    }
                } catch {
                    print("Failed to decode SSE event: \(error)")
                }
            }
        }
    }

    // MARK: - Cancel Stream

    func cancelStream() {
        streamTask?.cancel()
        isStreaming = false
        streamingText = ""
    }
}
```

### StreamingSceneView

```swift
import SwiftUI

struct StreamingSceneView: View {
    @ObservedObject var streamingService: StreamingService

    var body: some View {
        VStack(spacing: 20) {
            if streamingService.isStreaming {
                // Show streaming text with typing animation
                HStack(spacing: 8) {
                    Text(streamingService.streamingText)
                        .font(.sqBodyLarge)
                        .foregroundColor(.sqTextPrimary)
                        .multilineTextAlignment(.center)
                        .animation(.easeIn(duration: 0.1), value: streamingService.streamingText)

                    // Blinking cursor
                    Text("|")
                        .font(.sqBodyLarge)
                        .foregroundColor(.sqPrimary)
                        .opacity(cursorOpacity)
                        .onAppear {
                            withAnimation(.easeInOut(duration: 0.5).repeatForever()) {
                                cursorOpacity = 0.0
                            }
                        }
                }

                // Loading indicator
                ProgressView()
                    .scaleEffect(1.5)
                    .padding()

                Text("Creating your story...")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)
            }
        }
        .padding()
        .frame(maxWidth: 600)
    }

    @State private var cursorOpacity: Double = 1.0
}
```

---

## Enhanced Rate Limiting Handling

### RateLimitTracker (Client-Side)

```swift
import Foundation

class RateLimitTracker: ObservableObject {
    @Published var isRateLimited: Bool = false
    @Published var retryAfter: Int = 0
    @Published var retryMessage: String = ""

    private var retryTimer: Timer?

    func setRateLimit(retryAfter: Int) {
        self.retryAfter = retryAfter
        self.isRateLimited = true
        self.retryMessage = formatRetryMessage(seconds: retryAfter)

        // Start countdown timer
        retryTimer?.invalidate()
        retryTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }

            self.retryAfter -= 1

            if self.retryAfter <= 0 {
                self.clearRateLimit()
            } else {
                self.retryMessage = self.formatRetryMessage(seconds: self.retryAfter)
            }
        }
    }

    func clearRateLimit() {
        retryTimer?.invalidate()
        retryTimer = nil
        isRateLimited = false
        retryAfter = 0
        retryMessage = ""
    }

    private func formatRetryMessage(seconds: Int) -> String {
        if seconds < 60 {
            return "Try again in \(seconds) seconds"
        } else {
            let minutes = seconds / 60
            let remainingSeconds = seconds % 60
            return "Try again in \(minutes)m \(remainingSeconds)s"
        }
    }
}
```

### RateLimitView

```swift
import SwiftUI

struct RateLimitView: View {
    let retryAfter: Int
    let message: String

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "clock.badge.exclamationmark")
                .font(.system(size: 60))
                .foregroundColor(.orange)

            Text("Whoa, slow down!")
                .font(.sqHeadline)
                .foregroundColor(.sqTextPrimary)

            Text(message)
                .font(.sqBody)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)

            Text("This helps keep StoryQuest running smoothly for everyone!")
                .font(.sqCaption)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.orange.opacity(0.1))
        )
        .padding()
    }
}
```

### Usage in StoryViewModel

```swift
@MainActor
class StoryViewModel: ObservableObject {
    @Published var currentStory: StoryResponse?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private let apiService = APIService.shared
    private let rateLimitTracker = RateLimitTracker()

    func continueStory(choice: Choice) async {
        guard let story = currentStory else { return }

        isLoading = true
        errorMessage = nil

        do {
            let request = ContinueStoryRequest(
                sessionId: story.sessionId,
                choiceId: choice.id,
                choiceText: choice.text,
                customInput: nil,
                storySummary: story.storySummary  // ⭐ Required
            )

            let response = try await apiService.continueStory(request: request)
            currentStory = response

        } catch let error as APIError {
            switch error {
            case .rateLimitExceeded(let retryAfter):
                rateLimitTracker.setRateLimit(retryAfter: retryAfter)
                errorMessage = "Rate limit exceeded"

            case .safetyViolation(let message):
                errorMessage = message

            default:
                errorMessage = "Something went wrong. Please try again!"
            }
        } catch {
            errorMessage = "Network error. Check your connection!"
        }

        isLoading = false
    }
}
```

---

## Dynamic Theme Generation

### ThemeViewModel

```swift
@MainActor
class ThemeViewModel: ObservableObject {
    @Published var themes: [Theme] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private let apiService = APIService.shared

    // Fallback themes (used if dynamic generation fails)
    private let fallbackThemes: [Theme] = [
        Theme(id: "space_adventure", name: "Space Adventure", description: "Explore the stars!", emoji: "🚀", color: "from-indigo-400 to-purple-500"),
        Theme(id: "magical_forest", name: "Magical Forest", description: "Meet forest friends!", emoji: "🌲", color: "from-green-400 to-emerald-500"),
        Theme(id: "underwater_quest", name: "Underwater Quest", description: "Dive into the ocean!", emoji: "🌊", color: "from-blue-400 to-cyan-500"),
        Theme(id: "dinosaur_discovery", name: "Dinosaur Discovery", description: "Find ancient creatures!", emoji: "🦕", color: "from-orange-400 to-red-500"),
        Theme(id: "castle_quest", name: "Castle Quest", description: "Explore a magical castle!", emoji: "🏰", color: "from-purple-400 to-pink-500"),
        Theme(id: "robot_city", name: "Robot City", description: "Visit a futuristic city!", emoji: "🤖", color: "from-gray-400 to-blue-500")
    ]

    func loadThemes(for ageRange: String) async {
        isLoading = true
        errorMessage = nil

        do {
            // Try to generate dynamic themes
            themes = try await apiService.generateThemes(ageRange: ageRange)
        } catch {
            // Fall back to hardcoded themes
            print("Failed to load dynamic themes, using fallback: \(error)")
            themes = fallbackThemes
        }

        isLoading = false
    }
}
```

### Usage in ThemeSelectionView

```swift
struct ThemeSelectionView: View {
    @StateObject private var themeViewModel = ThemeViewModel()
    @State private var selectedAgeRange: String = "6-8"
    @State private var playerName: String = ""

    var body: some View {
        VStack(spacing: 24) {
            // Age selector
            Picker("Age Range", selection: $selectedAgeRange) {
                Text("Ages 6-8").tag("6-8")
                Text("Ages 9-12").tag("9-12")
            }
            .pickerStyle(.segmented)
            .padding()
            .onChange(of: selectedAgeRange) { newValue in
                Task {
                    await themeViewModel.loadThemes(for: newValue)
                }
            }

            // Theme grid
            if themeViewModel.isLoading {
                ProgressView("Loading themes...")
            } else {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 300))], spacing: 24) {
                    ForEach(themeViewModel.themes) { theme in
                        ThemeCard(theme: theme) {
                            // Start story with selected theme
                        }
                    }
                }
            }
        }
        .onAppear {
            Task {
                await themeViewModel.loadThemes(for: selectedAgeRange)
            }
        }
    }
}
```

---

## Implementation Phases

### Phase 5.1: Foundation & Updated Models (Week 1-2)

**Goal**: Set up project with updated backend integration

**Tasks**:
1. ✅ Create Xcode project with SwiftUI + Core Data
2. ✅ Define updated Swift models (with max_turns, is_finished, etc.)
3. ✅ Implement APIService with new endpoints
4. ✅ Add RateLimitTracker for client-side tracking
5. ✅ Create StreamEvent models for SSE
6. ✅ Set up Core Data schema
7. ✅ Basic error handling for rate limits and safety violations

**Deliverables**:
- Xcode project structure
- All models matching Phase 6 backend
- APIService with health check, start, continue, generate-themes
- Rate limit handling utilities

### Phase 5.2: Streaming Implementation (Week 3)

**Goal**: Add SSE streaming support

**Tasks**:
1. ✅ Create StreamingService for SSE handling
2. ✅ Implement SSE parsing (data: {json} format)
3. ✅ Create StreamingSceneView with typing animation
4. ✅ Add blinking cursor effect during streaming
5. ✅ Handle session_start, text_chunk, complete, error events
6. ✅ Test streaming with backend
7. ✅ Add stream cancellation support

**Deliverables**:
- Working SSE streaming
- Real-time text display
- Smooth animations

### Phase 5.3: UI - Theme Selection (Week 4)

**Goal**: Build dynamic theme selection

**Tasks**:
1. ✅ Create ThemeViewModel with dynamic theme loading
2. ✅ Implement fallback themes
3. ✅ Create ThemeCard with emoji and gradient
4. ✅ Add player name input
5. ✅ Add age range selector (triggers theme reload)
6. ✅ Implement "Start Adventure" action
7. ✅ Handle loading states and errors

**Deliverables**:
- Dynamic theme selection
- Age-based theme generation
- Graceful fallback

### Phase 5.4: UI - Story View (Week 5)

**Goal**: Build main story interface with streaming

**Tasks**:
1. ✅ Create StoryView layout
2. ✅ Integrate StreamingSceneView
3. ✅ Create ChoiceButtonView (disabled during streaming)
4. ✅ Add MetadataView (shows "Turn 3/12", progress bar)
5. ✅ Implement CustomInputView with safety messaging
6. ✅ Add "New Story" and "Menu" buttons
7. ✅ Handle is_finished state (show completion UI)
8. ✅ Add smooth transitions

**Deliverables**:
- Complete story interface
- Streaming text display
- Turn progress indicator
- Story completion UI

### Phase 5.5: Rate Limit Handling (Week 5)

**Goal**: User-friendly rate limit UX

**Tasks**:
1. ✅ Implement RateLimitTracker with countdown
2. ✅ Create RateLimitView
3. ✅ Disable buttons when rate limited
4. ✅ Show retry countdown
5. ✅ Clear rate limit after countdown
6. ✅ Handle Retry-After header
7. ✅ Test with multiple rate limit scenarios

**Deliverables**:
- Graceful rate limit handling
- User-friendly messaging
- Countdown timer

### Phase 5.6: Text-to-Speech (Week 6)

**Goal**: Add read-aloud functionality

**Tasks**:
1. ✅ Create TTSService using AVSpeechSynthesizer
2. ✅ Add play/pause/stop TTS controls
3. ✅ Implement voice selection
4. ✅ Add reading speed control
5. ✅ Handle TTS during streaming (disable until complete)
6. ✅ Save TTS preferences
7. ✅ Handle interruptions

**Deliverables**:
- Working TTS for scenes
- TTS controls in UI
- Persistent preferences

### Phase 5.7: Offline & Storage (Week 7)

**Goal**: Local story saving and replay

**Tasks**:
1. ✅ Implement Core Data entities (SavedSession, SavedTurn)
2. ✅ Auto-save stories to Core Data
3. ✅ Create HistoryListView
4. ✅ Implement HistoryDetailView with replay
5. ✅ Use GET /session/{id} for history refresh
6. ✅ Add export functionality (PDF, text)
7. ✅ Implement story deletion
8. ✅ Add storage management

**Deliverables**:
- Saved story history
- Offline replay
- Export to PDF/text

### Phase 5.8: Polish & Enhancements (Week 8)

**Goal**: Refine UX

**Tasks**:
1. ✅ Add haptic feedback
2. ✅ Improve animations (scene transitions, choice buttons)
3. ✅ Add sound effects (optional)
4. ✅ Create onboarding tutorial
5. ✅ Implement parental gate
6. ✅ Add app icon and launch screen
7. ✅ Performance optimization
8. ✅ Test on multiple iPads

**Deliverables**:
- Polished, production-ready app
- Delightful micro-interactions

### Phase 5.9: Testing & QA (Week 9)

**Goal**: Comprehensive testing

**Tasks**:
1. ✅ Unit tests for ViewModels
2. ✅ Unit tests for Services (API, Streaming, TTS)
3. ✅ UI tests for critical flows
4. ✅ Test streaming on slow networks
5. ✅ Test rate limiting scenarios
6. ✅ Test with different age ranges
7. ✅ Performance testing with Instruments
8. ✅ Accessibility testing

**Deliverables**:
- Test coverage >70%
- Bug-free critical flows

### Phase 5.10: Deployment (Week 10)

**Goal**: Submit to App Store

**Tasks**:
1. ✅ Set up App Store Connect
2. ✅ Create app metadata
3. ✅ Prepare privacy details
4. ✅ Beta test with TestFlight
5. ✅ Address feedback
6. ✅ Submit for review
7. ✅ Launch

**Deliverables**:
- App live on App Store

---

## UI/UX Design Updates

### Story Progress Indicator

```swift
struct StoryProgressView: View {
    let currentTurn: Int
    let maxTurns: Int

    var progress: Double {
        Double(currentTurn) / Double(maxTurns)
    }

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text("Turn \(currentTurn) of \(maxTurns)")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)

                Spacer()

                Text("\(Int(progress * 100))%")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)
            }

            ProgressView(value: progress)
                .tint(.sqPrimary)
        }
        .padding()
    }
}
```

### Story Completion View

```swift
struct StoryCompletionView: View {
    let story: StoryResponse

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)

            Text("Story Complete!")
                .font(.sqTitle)
                .foregroundColor(.sqTextPrimary)

            Text("You finished your \(story.metadata.theme) adventure in \(story.metadata.turns) turns!")
                .font(.sqBody)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)

            HStack(spacing: 16) {
                Button("Start New Story") {
                    // Navigate to theme selection
                }
                .buttonStyle(.borderedProminent)

                Button("View History") {
                    // Navigate to history
                }
                .buttonStyle(.bordered)
            }
        }
        .padding()
    }
}
```

---

## Core Features

### MVP Features (Phase 5.1-5.4)

- ✅ Dynamic theme selection with backend generation
- ✅ SSE streaming for real-time story display
- ✅ Player name and age range input
- ✅ Story scene display with streaming animation
- ✅ 3 choice buttons per scene
- ✅ Custom text input with safety messaging
- ✅ Rate limit handling with countdown
- ✅ Story progress indicator (Turn X of Y)
- ✅ Story completion detection and UI
- ✅ Backend API integration with error handling

### Enhanced Features (Phase 5.5-5.8)

- ✅ Text-to-speech for scene narration
- ✅ Offline story viewing
- ✅ Session history retrieval from backend
- ✅ Save story history to device
- ✅ Export stories (PDF, text)
- ✅ Haptic feedback
- ✅ Animations and transitions
- ✅ Onboarding tutorial

### Nice-to-Have (Future)

- ⬜ Story illustrations (AI-generated)
- ⬜ Multiple story save slots
- ⬜ iCloud sync
- ⬜ Dark mode
- ⬜ Localization

---

## Testing Strategy

### Unit Tests

**Models:**
- ✅ Codable encoding/decoding with new fields (max_turns, is_finished)
- ✅ StreamEvent parsing

**ViewModels:**
- ✅ Rate limit state management
- ✅ Streaming state management
- ✅ Story progression with story_summary

**Services:**
- ✅ APIService with new endpoints
- ✅ StreamingService SSE parsing
- ✅ RateLimitTracker countdown

### Integration Tests

- ✅ Streaming with backend
- ✅ Dynamic theme generation
- ✅ Rate limit handling (429 responses)
- ✅ Session history retrieval

### UI Tests

**Critical Flows:**
1. ✅ Load dynamic themes → Select theme → Start streaming story
2. ✅ Select choice → Continue streaming
3. ✅ Hit rate limit → See countdown → Retry after countdown
4. ✅ Complete story (is_finished) → See completion UI
5. ✅ View history → Replay story

---

## Deployment

### App Store Preparation

**Required Assets:**
1. App Icon (1024x1024px)
2. Screenshots (iPad Pro 12.9" and iPad Pro 11")
   - Theme selection with dynamic themes
   - Streaming story display
   - Rate limit UI
   - Story completion
3. App Preview video (optional)
4. Privacy Policy URL
5. App Description
6. Keywords for ASO
7. Age rating (4+)

**App Privacy Details:**
- Data Not Collected
- No tracking
- No third-party advertising
- No analytics

**Updated App Store Description:**

```
StoryQuest - Interactive Adventures for Kids

Create magical stories where YOU are the hero! Watch your story come to life
in real-time as our AI creates unique adventures just for you.

FEATURES:
✨ Fresh themes every time (powered by AI)
📖 Real-time story generation
🎤 Read-aloud mode
💾 Save your favorite stories
✅ 100% Safe & Kid-Friendly
🎨 Beautiful, colorful design

Perfect for ages 6-12. No ads, no in-app purchases, just pure storytelling fun!

Each story is unique and responds to your choices. The possibilities are endless!
```

---

## Summary & Next Steps

### Summary

This revised plan updates the iOS app for StoryQuest Phase 6 backend with:

1. ✅ **SSE Streaming** for real-time story generation
2. ✅ **Dynamic Themes** from backend
3. ✅ **Enhanced Rate Limiting** with user-friendly UX
4. ✅ **Updated Metadata** (max_turns, is_finished)
5. ✅ **story_summary Handling** for stateless continuation
6. ✅ **Session History** retrieval from backend

### Timeline

- **Weeks 1-2**: Foundation with updated models
- **Week 3**: Streaming implementation
- **Week 4**: Dynamic theme selection
- **Week 5**: Story view + rate limiting
- **Week 6**: Text-to-speech
- **Week 7**: Offline storage
- **Week 8**: Polish
- **Week 9**: Testing
- **Week 10**: Deployment

### Next Steps

1. **Create Xcode project** with SwiftUI + Core Data
2. **Implement updated models** (StoryMetadata, StreamEvent, etc.)
3. **Build APIService** with new endpoints
4. **Implement StreamingService** for SSE
5. **Build ThemeSelectionView** with dynamic themes
6. **Build StoryView** with streaming
7. **Test with Phase 6 backend**
8. **Iterate and polish**

### Success Criteria

- ✅ Streaming text displays in real-time
- ✅ Dynamic themes load successfully
- ✅ Rate limits handled gracefully
- ✅ Story completion detected and displayed
- ✅ TTS works with streamed text
- ✅ Offline replay works
- ✅ App launches in <2 seconds
- ✅ No crashes in critical flows
- ✅ Kids love using it! 🎉

---

**Ready to build StoryQuest for iPad with Phase 6 features! 🚀**
