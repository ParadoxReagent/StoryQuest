# StoryQuest iOS/iPadOS App

Native Swift/SwiftUI app for iPad providing an interactive text adventure experience for kids.

## Overview

The StoryQuest iOS app is a kid-friendly, interactive story application that connects to the StoryQuest backend API. It features text-to-speech, offline story saving, and a touch-optimized interface designed for iPad.

## Status

🚧 **Phase 5**: Planning and design phase

See [IOS_APP_PLAN.md](../IOS_APP_PLAN.md) for the complete implementation plan.

## Prerequisites

- **macOS**: macOS 13.0 (Ventura) or later
- **Xcode**: 15.0 or later
- **iOS SDK**: iOS 16.0+
- **Swift**: 5.9+
- **Apple Developer Account**: Required for device testing and App Store submission

## Project Setup

### 1. Create Xcode Project

```bash
# Navigate to ios directory
cd ios

# Create new Xcode project (via Xcode GUI):
# - File > New > Project
# - iOS > App
# - Product Name: StoryQuest
# - Team: Your Apple Developer Team
# - Organization Identifier: com.yourcompany
# - Interface: SwiftUI
# - Language: Swift
# - Include Tests: Yes
# - Create Core Data: Yes
```

### 2. Configure Project Settings

**Target Settings:**
- **Deployment Target**: iOS 16.0
- **Devices**: iPad only (unchecked iPhone)
- **Orientations**: Landscape Left, Landscape Right, Portrait (iPad supports all)
- **Requires Full Screen**: Yes

**Capabilities:**
- None required for MVP (no push notifications, iCloud, etc.)

**Info.plist Additions:**
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

### 3. Install Dependencies

This project uses native iOS frameworks only. No external dependencies required for MVP.

*Optional for future enhancements:*
- **SwiftyJSON**: JSON parsing (if needed)
- **Lottie**: Advanced animations

### 4. Project Structure

```
StoryQuest-iOS/
├── StoryQuest.xcodeproj
├── StoryQuest/
│   ├── App/
│   │   ├── StoryQuestApp.swift
│   │   └── AppEnvironment.swift
│   ├── Models/
│   │   ├── Story.swift
│   │   ├── Scene.swift
│   │   ├── Choice.swift
│   │   └── Theme.swift
│   ├── ViewModels/
│   │   ├── StoryViewModel.swift
│   │   └── ThemeSelectionViewModel.swift
│   ├── Views/
│   │   ├── Theme/
│   │   │   └── ThemeSelectionView.swift
│   │   └── Story/
│   │       └── StoryView.swift
│   ├── Services/
│   │   ├── APIService.swift
│   │   ├── TTSService.swift
│   │   └── StorageService.swift
│   ├── CoreData/
│   │   └── StoryQuest.xcdatamodeld
│   ├── Utilities/
│   │   └── Constants.swift
│   └── Resources/
│       └── Assets.xcassets
├── StoryQuestTests/
└── StoryQuestUITests/
```

## Development

### Running the App

1. **Open project in Xcode:**
```bash
open StoryQuest.xcodeproj
```

2. **Select iPad simulator:**
   - Choose "iPad Pro 12.9-inch" or "iPad (10th generation)" from device selector

3. **Run the app:**
   - Press `Cmd + R` or click the Play button

### Testing on Device

1. **Connect iPad via USB**
2. **Select your device** from the device selector
3. **Trust computer** on iPad if prompted
4. **Run** the app (Xcode will install and launch)

### Backend Connection

The app needs to connect to the StoryQuest backend:

**Local Development (Simulator):**
```swift
// In APIService.swift
let baseURL = "http://localhost:8000"
```

**Local Development (Physical Device):**
```swift
// Use your Mac's local IP address
let baseURL = "http://192.168.1.XXX:8000"

// Find your IP:
// System Settings > Network > Your Connection > IP Address
```

**Production:**
```swift
let baseURL = "https://api.storyquest.app"
```

## Architecture

### MVVM Pattern

The app follows the Model-View-ViewModel (MVVM) pattern:

- **Models**: Data structures (Story, Scene, Choice)
- **Views**: SwiftUI views (ThemeSelectionView, StoryView)
- **ViewModels**: Business logic and state (@ObservableObject classes)
- **Services**: API calls, TTS, storage

### Data Flow

```
User Input → View → ViewModel → Service → API
                ↑        ↓
              Binding  Published State
```

## Key Features

### MVP Features

- [x] Theme selection (6 themes)
- [x] Story scene display
- [x] Choice selection (3 options)
- [x] Custom text input
- [x] Story history
- [x] Backend API integration

### Enhanced Features

- [x] Text-to-speech (AVFoundation)
- [x] Offline story viewing (Core Data)
- [x] Export stories (PDF)
- [x] Haptic feedback
- [x] Animations

## API Integration

### Endpoints Used

```swift
// Start new story
POST /api/v1/story/start
Body: { player_name, age_range, theme }
Response: StoryResponse

// Continue story
POST /api/v1/story/continue
Body: { session_id, choice_id, custom_input, story_summary }
Response: StoryResponse

// Health check
GET /health
Response: { status, service }
```

### Sample Code

See `Examples/APIService.swift` for a complete implementation.

## Code Examples

### Start a Story

```swift
let request = StartStoryRequest(
    playerName: "Alex",
    ageRange: "6-8",
    theme: "space_adventure"
)

APIService.shared.startStory(request: request)
    .sink(
        receiveCompletion: { completion in
            // Handle error
        },
        receiveValue: { response in
            // Update UI with response
            self.currentScene = response.currentScene
            self.choices = response.choices
        }
    )
    .store(in: &cancellables)
```

### Text-to-Speech

```swift
let ttsService = TTSService()
ttsService.speak(text: scene.text)

// Controls
ttsService.pause()
ttsService.resume()
ttsService.stop()
```

## Testing

### Unit Tests

```bash
# Run unit tests
Cmd + U
```

Tests are located in `StoryQuestTests/`

### UI Tests

```bash
# Run UI tests
# Select StoryQuestUITests scheme
Cmd + U
```

UI tests are located in `StoryQuestUITests/`

### Manual Testing Checklist

- [ ] Theme selection works
- [ ] Story loads from backend
- [ ] Choices update story
- [ ] Custom input works
- [ ] TTS reads scenes
- [ ] History saves stories
- [ ] App works offline (viewing saved stories)
- [ ] Error handling displays properly

## Performance Targets

- **App Launch**: < 2 seconds
- **Story Load**: < 5 seconds (LLM dependent)
- **Scene Transition**: < 0.5 seconds
- **Memory Usage**: < 100MB typical
- **Frame Rate**: 60fps for animations

## Accessibility

### VoiceOver Support

All UI elements must have:
- Accessibility labels
- Accessibility hints
- Proper traits

### Dynamic Type

All text must support Dynamic Type for vision accessibility.

### Color Contrast

Minimum 4.5:1 contrast ratio for all text.

## Deployment

### TestFlight Beta

1. Archive the app (Product > Archive)
2. Upload to App Store Connect
3. Create TestFlight beta
4. Invite testers
5. Gather feedback

### App Store Submission

1. Complete App Store metadata
2. Upload screenshots (iPad Pro 12.9" and 11")
3. Set age rating (4+)
4. Privacy policy (no data collection)
5. Submit for review

See [IOS_APP_PLAN.md](../IOS_APP_PLAN.md) for detailed deployment guide.

## Troubleshooting

### Backend Connection Issues

**Simulator can't reach backend:**
- Use `http://localhost:8000` (works from simulator)

**Physical device can't reach backend:**
- Use your Mac's local IP address
- Ensure backend is running with `--host 0.0.0.0`
- Ensure Mac firewall allows connections

**Rate limit errors:**
- Wait for retry-after duration
- Reduce testing frequency
- Use different player names/sessions

### Build Errors

**Core Data errors:**
- Clean build folder (Cmd + Shift + K)
- Rebuild project

**Signing errors:**
- Check Apple Developer account
- Verify provisioning profiles
- Ensure bundle ID is unique

### Performance Issues

**Slow UI:**
- Profile with Instruments (Cmd + I)
- Check for main thread blocking
- Optimize image assets

**Memory leaks:**
- Use Instruments (Leaks template)
- Check for retain cycles in ViewModels
- Properly manage Combine cancellables

## Resources

### Documentation

- [IOS_APP_PLAN.md](../IOS_APP_PLAN.md) - Complete implementation plan
- [Apple SwiftUI Docs](https://developer.apple.com/documentation/swiftui/)
- [Combine Framework](https://developer.apple.com/documentation/combine)
- [Core Data](https://developer.apple.com/documentation/coredata)
- [AVFoundation TTS](https://developer.apple.com/documentation/avfoundation/speech_synthesis)

### Design Resources

- [SF Symbols](https://developer.apple.com/sf-symbols/) - System icons
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [iOS Design Resources](https://developer.apple.com/design/resources/)

### Learning

- [100 Days of SwiftUI](https://www.hackingwithswift.com/100/swiftui)
- [SwiftUI by Example](https://www.hackingwithswift.com/quick-start/swiftui)
- [Combine by Tutorials](https://www.raywenderlich.com/books/combine-asynchronous-programming-with-swift)

## Contributing

This is part of the StoryQuest project. See main [README.md](../README.md) for contribution guidelines.

## License

TBD

---

## Next Steps

1. ✅ Review [IOS_APP_PLAN.md](../IOS_APP_PLAN.md)
2. ⬜ Create Xcode project
3. ⬜ Implement Models and APIService
4. ⬜ Build ThemeSelectionView
5. ⬜ Build StoryView
6. ⬜ Add TTS and offline features
7. ⬜ Test and polish
8. ⬜ Deploy to App Store

**Let's build something amazing! 🚀**
