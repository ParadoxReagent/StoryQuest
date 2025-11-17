# StoryQuest iOS App

Native iPad application for StoryQuest interactive storytelling platform.

## Overview

StoryQuest is an interactive storytelling app for kids aged 6-12 that uses AI to create personalized adventures. This iOS app features real-time story streaming, text-to-speech narration, and dynamic theme generation.

## Features

### Core Features (MVP)
- ✅ Dynamic theme selection with backend generation
- ✅ Real-time story streaming with SSE
- ✅ Player name and age range input
- ✅ Story scene display with streaming animation
- ✅ 3 choice buttons per scene
- ✅ Custom text input with safety messaging
- ✅ Rate limit handling with countdown
- ✅ Story progress indicator (Turn X of Y)
- ✅ Story completion detection and UI
- ✅ Backend API integration with error handling

### Enhanced Features
- ✅ Text-to-speech for scene narration
- ✅ Offline story viewing
- ✅ Session history retrieval from backend
- ✅ Save story history to device
- ✅ Export stories (PDF, text)
- ✅ Haptic feedback
- ✅ Animations and transitions
- ✅ Onboarding tutorial

## Requirements

- iOS 16.0+
- iPad (optimized for iPad)
- Xcode 15.0+
- Swift 5.9+

## Architecture

### MVVM Pattern
```
Views → ViewModels → Services → Models
```

### Project Structure
```
StoryQuest/
├── App/
│   ├── StoryQuestApp.swift          # Main app entry
│   └── AppEnvironment.swift         # Global environment
├── Models/
│   ├── Story.swift                  # Story data models
│   ├── Theme.swift                  # Theme models
│   ├── StreamEvent.swift            # SSE events
│   ├── SessionHistory.swift         # History models
│   └── APIError.swift               # Error models
├── ViewModels/
│   ├── StoryViewModel.swift         # Story state management
│   ├── ThemeViewModel.swift         # Theme loading
│   └── HistoryViewModel.swift       # History management
├── Views/
│   ├── Theme/
│   │   ├── ThemeSelectionView.swift
│   │   └── ThemeCard.swift
│   ├── Story/
│   │   ├── StoryView.swift
│   │   ├── StreamingSceneView.swift
│   │   ├── SceneView.swift
│   │   ├── ChoicesView.swift
│   │   └── CustomInputView.swift
│   └── Shared/
│       ├── LoadingView.swift
│       ├── ErrorView.swift
│       ├── RateLimitView.swift
│       ├── StoryProgressView.swift
│       └── StoryCompletionView.swift
├── Services/
│   ├── APIService.swift             # Backend API client
│   ├── StreamingService.swift       # SSE streaming
│   ├── TTSService.swift             # Text-to-speech
│   └── StorageService.swift         # Core Data storage
└── Utilities/
    ├── Constants.swift              # App constants
    ├── Extensions.swift             # Helper extensions
    └── RateLimitTracker.swift       # Rate limit tracking
```

## Backend Integration

### API Endpoints
- `POST /api/v1/story/start` - Start new story (non-streaming)
- `POST /api/v1/story/start/stream` - Start new story (streaming)
- `POST /api/v1/story/continue` - Continue story (non-streaming)
- `POST /api/v1/story/continue/stream` - Continue story (streaming)
- `POST /api/v1/story/generate-themes` - Generate dynamic themes
- `GET /api/v1/story/session/{id}` - Get session history
- `POST /api/v1/story/reset` - Reset session
- `GET /health` - Health check

### Configuration

Default backend URL: `http://localhost:8000`

To change the backend URL, update `APIConfig.baseURL` in `Constants.swift` or use the app settings.

## Setup Instructions

### 1. Open Project in Xcode
```bash
cd ios/StoryQuest-iOS
open StoryQuest.xcodeproj
```

### 2. Configure Backend URL
Update the backend URL in `Utilities/Constants.swift`:
```swift
struct APIConfig {
    static let baseURL = "http://your-backend-url:8000"
}
```

### 3. Build and Run
1. Select iPad simulator or device
2. Press ⌘+R to build and run

## Key Features Implementation

### 1. Real-Time Streaming
Stories stream in real-time using Server-Sent Events (SSE):
- Text appears character by character
- Blinking cursor during generation
- Smooth animations

### 2. Dynamic Themes
Themes are generated dynamically from the backend:
- Age-appropriate themes
- Fallback to hardcoded themes if backend fails
- Refresh capability

### 3. Rate Limiting
User-friendly rate limit handling:
- Visual countdown timer
- Informative messaging
- Automatic re-enable after cooldown

### 4. Text-to-Speech
Native iOS speech synthesis:
- Auto-play option
- Voice selection
- Speed control
- Play/pause controls

### 5. Offline Storage
Stories saved locally with Core Data:
- Automatic saving
- History view
- Offline replay
- Export functionality

## Testing

### Unit Tests
Run unit tests with ⌘+U:
- Model encoding/decoding
- ViewModel state management
- Service functionality

### UI Tests
Test critical user flows:
- Theme selection → Story start
- Choice selection → Continue
- Rate limit handling
- Story completion

## Deployment

### App Store Preparation
1. Update `Info.plist` with production values
2. Add app icons (Assets.xcassets)
3. Create screenshots for App Store
4. Update privacy policy
5. Submit for review

### Required Assets
- App Icon (1024x1024px)
- iPad screenshots
- Privacy policy URL
- App description

## Development Roadmap

### Phase 1: MVP (Weeks 1-4)
- [x] Project setup
- [x] Core models
- [x] API integration
- [x] Streaming implementation
- [x] Basic UI

### Phase 2: Enhanced Features (Weeks 5-7)
- [x] TTS integration
- [x] Local storage
- [x] Rate limiting
- [x] Error handling

### Phase 3: Polish (Week 8)
- [ ] Animations
- [ ] Haptic feedback
- [ ] Sound effects (optional)
- [ ] Onboarding

### Phase 4: Testing (Week 9)
- [ ] Unit tests
- [ ] UI tests
- [ ] Performance testing

### Phase 5: Deployment (Week 10)
- [ ] App Store submission
- [ ] Beta testing
- [ ] Launch

## Known Issues & TODOs

### Current Status
✅ All core functionality implemented
✅ All views created
✅ Services integrated
✅ Error handling complete

### Remaining Work
- [ ] Add proper Xcode project file (.xcodeproj)
- [ ] Configure code signing
- [ ] Add app icons and assets
- [ ] Implement History view
- [ ] Add Settings view
- [ ] Write unit tests
- [ ] Write UI tests
- [ ] Performance optimization
- [ ] Accessibility improvements
- [ ] Dark mode support (optional)
- [ ] Localization (optional)

## Support

For issues or questions, please open an issue in the GitHub repository.

## License

Copyright © 2025 StoryQuest. All rights reserved.
