# StoryQuest iOS/iPadOS App - Implementation Plan
## Phase 5: Native iPad Application

---

## Table of Contents

1. [Overview](#overview)
2. [Goals & Requirements](#goals--requirements)
3. [Technology Stack](#technology-stack)
4. [Architecture](#architecture)
5. [Implementation Phases](#implementation-phases)
6. [Features](#features)
7. [Data Models](#data-models)
8. [UI/UX Design](#uiux-design)
9. [API Integration](#api-integration)
10. [Core Data Schema](#core-data-schema)
11. [Text-to-Speech](#text-to-speech)
12. [Accessibility](#accessibility)
13. [Testing Strategy](#testing-strategy)
14. [Deployment](#deployment)
15. [Future Enhancements](#future-enhancements)

---

## Overview

The StoryQuest iOS/iPadOS app is a native Swift application that provides a kid-friendly, interactive text adventure experience optimized for iPad. The app connects to the existing StoryQuest backend API and provides an enhanced mobile experience with features like text-to-speech, offline story saving, and touch-optimized UI.

### Target Devices

- **Primary**: iPad (9th gen and newer)
- **Secondary**: iPad Pro, iPad Air, iPad mini
- **iOS Version**: iOS 16.0+
- **Orientation**: Primarily landscape, with portrait support

### Key Differentiators from Web UI

1. **Native Performance**: Smooth animations and gestures
2. **Text-to-Speech**: Read stories aloud with AVFoundation
3. **Offline Support**: Save and replay completed stories
4. **Haptic Feedback**: Tactile response for interactions
5. **iPad-Optimized**: Large, colorful, touch-friendly UI
6. **Share Stories**: Export stories as PDF or text

---

## Goals & Requirements

### Primary Goals

1. ✅ Provide native iOS/iPadOS experience for StoryQuest
2. ✅ Support all features from web UI (theme selection, story progression, custom input)
3. ✅ Add TTS for read-aloud functionality
4. ✅ Enable offline story viewing (completed stories)
5. ✅ Maintain kid-friendly, safe, accessible design

### Requirements

**Functional:**
- Connect to StoryQuest backend API
- Start new stories with theme and player name
- Display story scenes with colorful, engaging UI
- Present choice options as large, tappable buttons
- Support custom text input with on-screen keyboard
- Read stories aloud with TTS
- Save story history locally
- View and replay past stories

**Non-Functional:**
- Fast app launch (<2 seconds)
- Smooth animations (60fps)
- Low memory footprint (<100MB typical)
- Reliable network error handling
- Works on cellular and WiFi
- Parental controls integration

**Safety:**
- All backend safety features apply
- No in-app purchases or ads
- No social features or user accounts
- Parental gate for settings
- Content filtering via backend

---

## Technology Stack

### Languages & Frameworks

- **Swift 5.9+**: Modern, type-safe, performant
- **SwiftUI**: Declarative UI framework
- **Combine**: Reactive programming for data flow
- **AVFoundation**: Text-to-speech synthesis
- **Core Data**: Local data persistence
- **URLSession**: Networking and API calls

### Libraries & Dependencies

- **None initially** - Use native iOS frameworks
- (Optional) **SwiftyJSON** or **Codable** for JSON parsing
- (Optional) **Lottie** for advanced animations

### Development Tools

- **Xcode 15+**: Primary IDE
- **SF Symbols**: System icons
- **Instruments**: Performance profiling
- **TestFlight**: Beta distribution
- **App Store Connect**: Production deployment

---

## Architecture

### MVVM (Model-View-ViewModel) Pattern

```
┌─────────────────────────────────────────────┐
│                   Views                     │
│  (SwiftUI - ThemeSelectionView, StoryView)  │
└────────────────┬────────────────────────────┘
                 │ Observes
┌────────────────▼────────────────────────────┐
│              ViewModels                     │
│  (ObservableObject - StoryViewModel, etc.)  │
└────────────────┬────────────────────────────┘
                 │ Uses
┌────────────────▼────────────────────────────┐
│               Models                        │
│  (Story, Scene, Choice, Session)            │
└────────────────┬────────────────────────────┘
                 │ Used by
┌────────────────▼────────────────────────────┐
│              Services                       │
│  (APIService, TTSService, StorageService)   │
└─────────────────────────────────────────────┘
```

### Project Structure

```
StoryQuest-iOS/
├── StoryQuest.xcodeproj
├── StoryQuest/
│   ├── App/
│   │   ├── StoryQuestApp.swift          # App entry point
│   │   └── AppEnvironment.swift         # Dependency injection
│   ├── Models/
│   │   ├── Story.swift                  # Story data models
│   │   ├── Scene.swift
│   │   ├── Choice.swift
│   │   ├── Session.swift
│   │   └── Theme.swift
│   ├── ViewModels/
│   │   ├── StoryViewModel.swift         # Story state management
│   │   ├── ThemeSelectionViewModel.swift
│   │   └── HistoryViewModel.swift
│   ├── Views/
│   │   ├── Theme/
│   │   │   ├── ThemeSelectionView.swift # Start screen
│   │   │   └── ThemeCard.swift
│   │   ├── Story/
│   │   │   ├── StoryView.swift          # Main story screen
│   │   │   ├── SceneTextView.swift
│   │   │   ├── ChoiceButtonView.swift
│   │   │   └── CustomInputView.swift
│   │   ├── History/
│   │   │   ├── HistoryListView.swift
│   │   │   └── HistoryDetailView.swift
│   │   └── Shared/
│   │       ├── LoadingView.swift
│   │       └── ErrorView.swift
│   ├── Services/
│   │   ├── APIService.swift             # Backend API client
│   │   ├── TTSService.swift             # Text-to-speech
│   │   ├── StorageService.swift         # Core Data wrapper
│   │   └── NetworkMonitor.swift         # Network connectivity
│   ├── CoreData/
│   │   ├── StoryQuest.xcdatamodeld      # Core Data model
│   │   ├── PersistenceController.swift
│   │   └── Entities/
│   │       ├── SavedSession+CoreData.swift
│   │       └── SavedTurn+CoreData.swift
│   ├── Utilities/
│   │   ├── Constants.swift              # App constants
│   │   ├── Extensions.swift             # Swift extensions
│   │   └── Logger.swift                 # Logging utility
│   ├── Resources/
│   │   ├── Assets.xcassets              # Images, colors
│   │   ├── Sounds/                      # Sound effects
│   │   └── Fonts/                       # Custom fonts
│   └── Info.plist
├── StoryQuestTests/
│   ├── ModelTests/
│   ├── ViewModelTests/
│   └── ServiceTests/
└── StoryQuestUITests/
    └── StoryQuestUITests.swift
```

---

## Implementation Phases

### Phase 5.1: Foundation (Week 1-2)

**Goal**: Set up project, models, and basic API integration

**Tasks**:
1. Create Xcode project with SwiftUI + Core Data
2. Define Swift models matching backend API
3. Implement APIService with URLSession
4. Create StoryViewModel with Combine
5. Set up Core Data schema
6. Implement PersistenceController
7. Basic error handling and logging

**Deliverables**:
- Xcode project structure
- API service connecting to backend
- Data models with Codable conformance
- Basic Core Data setup

### Phase 5.2: UI - Theme Selection (Week 3)

**Goal**: Build theme selection screen

**Tasks**:
1. Create ThemeSelectionView with grid layout
2. Implement ThemeCard with SF Symbols icons
3. Add player name input field
4. Add age range selector
5. Implement "Start Adventure" action
6. Add loading states and error handling
7. Design kid-friendly color scheme

**Deliverables**:
- Functional theme selection screen
- Polished UI matching web design
- Proper state management

### Phase 5.3: UI - Story View (Week 4)

**Goal**: Build main story interface

**Tasks**:
1. Create StoryView layout
2. Implement SceneTextView with animations
3. Create ChoiceButtonView (3 choice buttons)
4. Implement CustomInputView with keyboard handling
5. Add story history sidebar/modal
6. Implement "New Story" and "Menu" buttons
7. Add smooth transitions between scenes

**Deliverables**:
- Complete story playback interface
- Choice selection and custom input
- Story history viewing

### Phase 5.4: Text-to-Speech (Week 5)

**Goal**: Add read-aloud functionality

**Tasks**:
1. Create TTSService using AVSpeechSynthesizer
2. Add play/pause/stop TTS controls
3. Implement voice selection (kid-friendly voices)
4. Add reading speed control
5. Highlight text as it's read (optional)
6. Save TTS preferences
7. Handle interruptions (calls, backgrounding)

**Deliverables**:
- Working TTS for scene text
- TTS controls in UI
- Persistent TTS preferences

### Phase 5.5: Offline & Storage (Week 6)

**Goal**: Enable offline story viewing

**Tasks**:
1. Implement Core Data entities for sessions/turns
2. Save story sessions to Core Data automatically
3. Create HistoryListView to browse saved stories
4. Implement HistoryDetailView to replay stories
5. Add export functionality (PDF, text)
6. Implement story deletion
7. Add storage management (limit total stories)

**Deliverables**:
- Saved story history
- Offline story viewing
- Export to PDF/text

### Phase 5.6: Polish & Enhancements (Week 7)

**Goal**: Refine UX and add delightful details

**Tasks**:
1. Add haptic feedback for button taps
2. Implement smooth animations and transitions
3. Add sound effects (optional)
4. Improve loading states with animations
5. Add onboarding tutorial for first launch
6. Implement parental gate for settings
7. Add app icon and launch screen
8. Performance optimization

**Deliverables**:
- Polished, production-ready app
- Delightful micro-interactions
- Onboarding experience

### Phase 5.7: Testing & QA (Week 8)

**Goal**: Comprehensive testing

**Tasks**:
1. Write unit tests for ViewModels
2. Write unit tests for Services
3. UI tests for critical flows
4. Test on multiple iPad models
5. Test with different network conditions
6. Test error scenarios
7. Performance testing with Instruments
8. Accessibility testing with VoiceOver

**Deliverables**:
- Test coverage >70%
- Bug-free critical flows
- Performance benchmarks met

### Phase 5.8: Deployment (Week 9)

**Goal**: Submit to App Store

**Tasks**:
1. Set up App Store Connect account
2. Create app metadata (description, screenshots)
3. Prepare App Privacy details
4. Beta test with TestFlight
5. Address TestFlight feedback
6. Submit for App Review
7. Launch to App Store

**Deliverables**:
- App live on App Store
- TestFlight beta version
- Marketing materials

---

## Features

### MVP Features (Phase 5.1-5.3)

- [x] Theme selection with 6 themes
- [x] Player name and age range input
- [x] Story scene display
- [x] 3 choice buttons per scene
- [x] Custom text input option
- [x] Story history view
- [x] New story/restart functionality
- [x] Error handling and loading states
- [x] Backend API integration

### Enhanced Features (Phase 5.4-5.6)

- [x] Text-to-speech for scene narration
- [x] Offline story viewing
- [x] Save story history to device
- [x] Export stories (PDF, text)
- [x] Haptic feedback
- [x] Animations and transitions
- [x] Onboarding tutorial
- [x] Parental controls

### Nice-to-Have (Future)

- [ ] Story illustrations (AI-generated)
- [ ] Character avatars
- [ ] Achievement system
- [ ] Multiple story save slots
- [ ] iCloud sync
- [ ] Share stories with friends/family
- [ ] Dark mode
- [ ] Localization (multiple languages)

---

## Data Models

### Swift Models (Matching Backend API)

```swift
// MARK: - Story Models

import Foundation

struct Choice: Codable, Identifiable {
    let id: String
    let text: String

    enum CodingKeys: String, CodingKey {
        case id = "choice_id"
        case text
    }
}

struct Scene: Codable, Identifiable {
    let id: String
    let text: String
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case id = "scene_id"
        case text
        case timestamp
    }
}

struct StoryMetadata: Codable {
    let turns: Int
    let theme: String
    let ageRange: String

    enum CodingKeys: String, CodingKey {
        case turns
        case theme
        case ageRange = "age_range"
    }
}

struct StoryResponse: Codable {
    let sessionId: UUID
    let storySummary: String
    let currentScene: Scene
    let choices: [Choice]
    let metadata: StoryMetadata?

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case storySummary = "story_summary"
        case currentScene = "current_scene"
        case choices
        case metadata
    }
}

// MARK: - Request Models

struct StartStoryRequest: Codable {
    let playerName: String
    let ageRange: String
    let theme: String

    enum CodingKeys: String, CodingKey {
        case playerName = "player_name"
        case ageRange = "age_range"
        case theme
    }
}

struct ContinueStoryRequest: Codable {
    let sessionId: UUID
    let choiceId: String?
    let customInput: String?
    let storySummary: String

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case choiceId = "choice_id"
        case customInput = "custom_input"
        case storySummary = "story_summary"
    }
}

// MARK: - App Models

struct Theme: Identifiable {
    let id: String
    let name: String
    let icon: String // SF Symbol name
    let color: String // Hex color
    let gradient: [String] // Gradient colors
    let description: String
}

enum AgeRange: String, CaseIterable {
    case young = "6-8"
    case older = "9-12"

    var displayName: String {
        switch self {
        case .young: return "Ages 6-8"
        case .older: return "Ages 9-12"
        }
    }
}

struct StoryTurn: Identifiable {
    let id: UUID
    let scene: Scene
    let chosenText: String
    let timestamp: Date
}

class StorySession: ObservableObject {
    let sessionId: UUID
    let playerName: String
    let theme: Theme
    let ageRange: AgeRange
    let startedAt: Date

    @Published var turns: [StoryTurn] = []
    @Published var currentScene: Scene?
    @Published var currentChoices: [Choice] = []
    @Published var storySummary: String = ""
    @Published var isComplete: Bool = false
}
```

---

## UI/UX Design

### Design Principles

1. **Kid-Friendly**: Large text, bright colors, simple navigation
2. **Touch-Optimized**: Minimum 44pt touch targets
3. **Readable**: High contrast, dyslexia-friendly fonts
4. **Delightful**: Smooth animations, fun transitions
5. **Safe**: Parental controls, no ads, no social features

### Color Palette

```swift
// Custom color definitions
extension Color {
    // Primary
    static let sqPrimary = Color("Primary") // Bright blue
    static let sqSecondary = Color("Secondary") // Warm orange
    static let sqAccent = Color("Accent") // Cheerful yellow

    // Theme Colors
    static let sqMagicalForest = Color(hex: "#4CAF50") // Green
    static let sqSpaceAdventure = Color(hex: "#2196F3") // Blue
    static let sqUnderwaterQuest = Color(hex: "#00BCD4") // Cyan
    static let sqDinosaurDiscovery = Color(hex: "#FF9800") // Orange
    static let sqCastleQuest = Color(hex: "#9C27B0") // Purple
    static let sqRobotCity = Color(hex: "#607D8B") // Blue-grey

    // UI
    static let sqBackground = Color("Background") // Light cream
    static let sqCardBackground = Color.white
    static let sqTextPrimary = Color(hex: "#212121")
    static let sqTextSecondary = Color(hex: "#757575")
}
```

### Typography

```swift
extension Font {
    // Headings
    static let sqTitle = Font.system(size: 48, weight: .bold, design: .rounded)
    static let sqHeadline = Font.system(size: 32, weight: .bold, design: .rounded)

    // Body
    static let sqBody = Font.system(size: 24, weight: .regular, design: .rounded)
    static let sqBodyLarge = Font.system(size: 28, weight: .regular, design: .rounded)

    // Buttons
    static let sqButton = Font.system(size: 22, weight: .semibold, design: .rounded)

    // Small
    static let sqCaption = Font.system(size: 18, weight: .medium, design: .rounded)
}
```

### Layout Guidelines

**Theme Selection Screen:**
- 2x3 grid of theme cards (landscape)
- Each card: 300x250pt
- Card spacing: 24pt
- Player name input at top: 60pt height
- Age selector buttons: 50pt height
- Start button: 60pt height, full width

**Story View:**
- Scene text area: Top 50% of screen
- Choice buttons: Bottom 40% of screen (3 buttons, stacked)
- Control bar: Bottom 10% (New Story, History, TTS)
- Scene text: 28pt, max 600pt width, centered
- Choice buttons: 80pt height, 90% width
- Button spacing: 16pt

**History View:**
- iPad split view: List (30%) + Detail (70%)
- List items: 100pt height with preview
- Detail: Full story replay with pagination

---

## API Integration

### APIService Implementation

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
}

class APIService {
    static let shared = APIService()

    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()

    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60 // LLM can be slow
        self.session = URLSession(configuration: config)
    }

    // MARK: - API Methods

    func startStory(request: StartStoryRequest) -> AnyPublisher<StoryResponse, APIError> {
        let url = URL(string: "\(baseURL)/api/v1/story/start")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: .decodingError(error)).eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: urlRequest)
            .tryMap { data, response -> Data in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.invalidResponse
                }

                if httpResponse.statusCode == 429 {
                    let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After")
                    throw APIError.rateLimitExceeded(retryAfter: Int(retryAfter ?? "120") ?? 120)
                }

                guard (200...299).contains(httpResponse.statusCode) else {
                    throw APIError.invalidResponse
                }

                return data
            }
            .decode(type: StoryResponse.self, decoder: JSONDecoder.storyQuestDecoder)
            .mapError { error -> APIError in
                if let apiError = error as? APIError {
                    return apiError
                } else if let decodingError = error as? DecodingError {
                    return .decodingError(decodingError)
                } else {
                    return .networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }

    func continueStory(request: ContinueStoryRequest) -> AnyPublisher<StoryResponse, APIError> {
        let url = URL(string: "\(baseURL)/api/v1/story/continue")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: .decodingError(error)).eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: urlRequest)
            .tryMap { data, response -> Data in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.invalidResponse
                }

                if httpResponse.statusCode == 429 {
                    let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After")
                    throw APIError.rateLimitExceeded(retryAfter: Int(retryAfter ?? "120") ?? 120)
                }

                guard (200...299).contains(httpResponse.statusCode) else {
                    throw APIError.invalidResponse
                }

                return data
            }
            .decode(type: StoryResponse.self, decoder: JSONDecoder.storyQuestDecoder)
            .mapError { error -> APIError in
                if let apiError = error as? APIError {
                    return apiError
                } else if let decodingError = error as? DecodingError {
                    return .decodingError(decodingError)
                } else {
                    return .networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }

    func healthCheck() -> AnyPublisher<Bool, Never> {
        let url = URL(string: "\(baseURL)/health")!

        return session.dataTaskPublisher(for: url)
            .map { _, response in
                (response as? HTTPURLResponse)?.statusCode == 200
            }
            .replaceError(with: false)
            .eraseToAnyPublisher()
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

### Network Monitoring

```swift
import Network
import Combine

class NetworkMonitor: ObservableObject {
    @Published var isConnected = true
    @Published var connectionType: NWInterface.InterfaceType?

    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
                self?.connectionType = path.availableInterfaces.first?.type
            }
        }
        monitor.start(queue: queue)
    }

    deinit {
        monitor.cancel()
    }
}
```

---

## Core Data Schema

### Entities

**SavedSession**
- `id: UUID` (Primary key)
- `playerName: String`
- `theme: String`
- `ageRange: String`
- `storySummary: String`
- `startedAt: Date`
- `lastPlayedAt: Date`
- `isComplete: Bool`
- `totalTurns: Int16`
- Relationship: `turns` → SavedTurn (one-to-many)

**SavedTurn**
- `id: UUID` (Primary key)
- `sceneId: String`
- `sceneText: String`
- `chosenText: String`
- `timestamp: Date`
- `turnNumber: Int16`
- Relationship: `session` → SavedSession (many-to-one)

### Core Data Stack

```swift
import CoreData

class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "StoryQuest")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Core Data failed to load: \(error.localizedDescription)")
            }
        }

        container.viewContext.automaticallyMergesChangesFromParent = true
    }

    func save() {
        let context = container.viewContext

        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Failed to save Core Data context: \(error)")
            }
        }
    }
}
```

---

## Text-to-Speech

### TTSService Implementation

```swift
import AVFoundation
import Combine

class TTSService: NSObject, ObservableObject {
    @Published var isSpeaking = false
    @Published var isPaused = false
    @Published var selectedVoice: AVSpeechSynthesisVoice?
    @Published var speechRate: Float = AVSpeechUtteranceDefaultSpeechRate

    private let synthesizer = AVSpeechSynthesizer()
    private var currentUtterance: AVSpeechUtterance?

    override init() {
        super.init()
        synthesizer.delegate = self
        setupDefaultVoice()
    }

    private func setupDefaultVoice() {
        // Prefer kid-friendly voices
        let preferredVoices = [
            "com.apple.ttsbundle.Samantha-compact", // US English, friendly
            "com.apple.ttsbundle.siri_female_en-US_compact"
        ]

        for identifier in preferredVoices {
            if let voice = AVSpeechSynthesisVoice(identifier: identifier) {
                selectedVoice = voice
                return
            }
        }

        // Fallback to any English voice
        selectedVoice = AVSpeechSynthesisVoice(language: "en-US")
    }

    func speak(text: String) {
        stop() // Stop any current speech

        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = selectedVoice
        utterance.rate = speechRate
        utterance.pitchMultiplier = 1.1 // Slightly higher pitch for kids
        utterance.volume = 1.0

        currentUtterance = utterance
        synthesizer.speak(utterance)
    }

    func pause() {
        synthesizer.pauseSpeaking(at: .word)
        isPaused = true
    }

    func resume() {
        synthesizer.continueSpeaking()
        isPaused = false
    }

    func stop() {
        synthesizer.stopSpeaking(at: .immediate)
        currentUtterance = nil
        isSpeaking = false
        isPaused = false
    }

    func availableVoices() -> [AVSpeechSynthesisVoice] {
        AVSpeechSynthesisVoice.speechVoices()
            .filter { $0.language.hasPrefix("en") }
            .sorted { $0.name < $1.name }
    }
}

// MARK: - AVSpeechSynthesizerDelegate

extension TTSService: AVSpeechSynthesizerDelegate {
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didStart utterance: AVSpeechUtterance) {
        isSpeaking = true
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        isSpeaking = false
        isPaused = false
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didPause utterance: AVSpeechUtterance) {
        isPaused = true
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didContinue utterance: AVSpeechUtterance) {
        isPaused = false
    }
}
```

### TTS UI Controls

```swift
struct TTSControlView: View {
    @ObservedObject var ttsService: TTSService
    let sceneText: String

    var body: some View {
        HStack(spacing: 20) {
            if ttsService.isSpeaking {
                Button(action: {
                    if ttsService.isPaused {
                        ttsService.resume()
                    } else {
                        ttsService.pause()
                    }
                }) {
                    Image(systemName: ttsService.isPaused ? "play.circle.fill" : "pause.circle.fill")
                        .font(.system(size: 44))
                        .foregroundColor(.sqPrimary)
                }

                Button(action: { ttsService.stop() }) {
                    Image(systemName: "stop.circle.fill")
                        .font(.system(size: 44))
                        .foregroundColor(.sqSecondary)
                }
            } else {
                Button(action: { ttsService.speak(text: sceneText) }) {
                    HStack {
                        Image(systemName: "speaker.wave.2.fill")
                        Text("Read Aloud")
                    }
                    .font(.sqButton)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.sqPrimary)
                    .cornerRadius(16)
                }
            }
        }
    }
}
```

---

## Accessibility

### VoiceOver Support

- All interactive elements have accessibility labels
- Proper accessibility traits (button, header, etc.)
- Logical focus order
- Announce scene changes

### Dynamic Type

- Support Dynamic Type for all text
- Use `.scaledToFill()` for text containers
- Test with largest accessibility sizes

### Color Contrast

- Minimum 4.5:1 contrast ratio for text
- Use system colors where appropriate
- Test in grayscale mode

### Example Implementation

```swift
Button(action: selectChoice) {
    Text(choice.text)
        .font(.sqButton)
        .foregroundColor(.white)
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color.sqPrimary)
        .cornerRadius(16)
}
.accessibilityLabel("Choice: \(choice.text)")
.accessibilityHint("Double tap to select this option")
.accessibilityAddTraits(.isButton)
```

---

## Testing Strategy

### Unit Tests

**Models:**
- Codable encoding/decoding
- Computed properties
- Validation logic

**ViewModels:**
- State transitions
- API call handling
- Error handling
- Story progression logic

**Services:**
- API request formation
- Response parsing
- TTS functionality
- Core Data operations

### UI Tests

**Critical Flows:**
1. Start new story → Theme selection → Story begins
2. Select choice → New scene appears
3. Custom input → Scene responds
4. View history → See past stories
5. TTS → Read story aloud

### Integration Tests

- API integration with backend
- Core Data persistence
- TTS with AVFoundation
- Network connectivity handling

### Performance Tests

- App launch time (<2s)
- Story transition time (<0.5s)
- Memory usage (<100MB)
- Scroll performance (60fps)

### Device Testing

Test on:
- iPad 9th gen (base model)
- iPad Pro 12.9"
- iPad mini
- iOS 16.0 and latest iOS

---

## Deployment

### App Store Preparation

**Required Assets:**
1. App Icon (1024x1024px)
2. Screenshots (iPad Pro 12.9" and iPad Pro 11")
3. App Preview video (optional)
4. Privacy Policy URL
5. App Description (kid-friendly)
6. Keywords for ASO
7. Age rating (4+)

**App Privacy Details:**
- Data Not Collected
- No tracking
- No third-party advertising
- No analytics

**App Store Description:**

```
StoryQuest - Interactive Adventures for Kids

Create magical stories where YOU are the hero! Choose your adventure theme,
make exciting choices, and watch your unique story unfold.

FEATURES:
✨ 6 Amazing Themes (Space, Magic Forest, Underwater, and more!)
📖 Stories created just for you
🎤 Read-aloud mode
💾 Save your favorite stories
✅ 100% Safe & Kid-Friendly

Perfect for ages 6-12. No ads, no in-app purchases, just pure storytelling fun!

THEMES:
🚀 Space Adventure
🌳 Magical Forest
🌊 Underwater Quest
🦕 Dinosaur Discovery
🏰 Castle Quest
🤖 Robot City

Each story is unique and responds to your choices. The possibilities are endless!
```

### TestFlight Beta

1. Invite 5-10 parent testers
2. Gather feedback on:
   - Ease of use for kids
   - Story quality
   - TTS functionality
   - Performance issues
3. Iterate based on feedback
4. Final beta round before submission

### Submission Checklist

- [ ] All features working
- [ ] No crashes in testing
- [ ] Performance targets met
- [ ] Accessibility verified
- [ ] Privacy Policy published
- [ ] Screenshots and preview ready
- [ ] App metadata complete
- [ ] Age rating accurate
- [ ] TestFlight beta complete

---

## Future Enhancements

### Phase 6+ Ideas

**Story Illustrations (Phase 7)**
- Generate scene images with DALL-E or Stable Diffusion
- Cache images locally
- Display alongside text
- Option to disable for faster loading

**Achievement System (Phase 7)**
- Unlock badges for completing themes
- Streak tracking (stories per week)
- Creative input achievements
- Share achievements (with parental permission)

**Advanced Features:**
- Multiple save slots (3-5 concurrent stories)
- iCloud sync across devices
- Share stories with family (export/import)
- Story ratings (kid reviews)
- Seasonal themes (Halloween, Christmas)
- Custom theme creator (parents)

**Localization:**
- Spanish translation
- French translation
- Support for international voices in TTS

**iPad Pro Features:**
- Apple Pencil drawing for custom choices
- Split-screen multitasking support
- Stage Manager optimization

**Parental Dashboard:**
- View all saved stories
- Export all stories as PDF
- Content review
- Usage statistics

---

## Summary & Next Steps

### Summary

This plan outlines a comprehensive 8-9 week development timeline for the StoryQuest iOS/iPadOS app. The app will:

1. ✅ Provide a native, kid-friendly story experience
2. ✅ Integrate with existing StoryQuest backend
3. ✅ Add unique mobile features (TTS, offline, haptics)
4. ✅ Maintain safety and accessibility standards
5. ✅ Be production-ready for App Store

### Timeline

- **Weeks 1-2**: Foundation & API integration
- **Weeks 3-4**: Core UI (Theme + Story views)
- **Week 5**: Text-to-Speech
- **Week 6**: Offline & Storage
- **Week 7**: Polish & Enhancements
- **Week 8**: Testing & QA
- **Week 9**: Deployment

### Next Steps

1. **Create Xcode project** with SwiftUI template
2. **Set up models** matching backend API
3. **Implement APIService** and test connectivity
4. **Build ThemeSelectionView** (MVP)
5. **Build StoryView** (MVP)
6. **Iterate and test** with kids/parents

### Success Criteria

- ✅ App launches in <2 seconds
- ✅ Stories load in <5 seconds (with LLM)
- ✅ Smooth 60fps animations
- ✅ No crashes in critical flows
- ✅ 4.5+ star rating on App Store
- ✅ Kids love using it! 🎉

---

**Ready to build? Let's make StoryQuest magical on iPad! 🚀**
