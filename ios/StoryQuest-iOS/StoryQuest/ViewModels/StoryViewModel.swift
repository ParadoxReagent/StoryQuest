//
//  StoryViewModel.swift
//  StoryQuest
//
//  ViewModel for story management with streaming support
//

import Foundation
import Combine

@MainActor
class StoryViewModel: ObservableObject {
    // Published properties
    @Published var currentStory: StoryResponse?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false

    // Services
    private let apiService: APIService
    let streamingService: StreamingService
    private let storageService: StorageService
    let rateLimitTracker = RateLimitTracker()

    // Story state
    private var playerName: String = ""
    private var currentTheme: String = ""
    private var currentAgeRange: String = ""

    init(
        apiService: APIService = .shared,
        streamingService: StreamingService = StreamingService(),
        storageService: StorageService = .shared
    ) {
        self.apiService = apiService
        self.streamingService = streamingService
        self.storageService = storageService
    }

    // MARK: - Start Story

    /// Start a new story with streaming
    func startStory(playerName: String, ageRange: String, theme: String, useStreaming: Bool = true) async {
        self.playerName = playerName
        self.currentAgeRange = ageRange
        self.currentTheme = theme

        isLoading = true
        errorMessage = nil
        currentStory = nil

        let request = StartStoryRequest(
            playerName: playerName,
            ageRange: ageRange,
            theme: theme
        )

        if useStreaming {
            startStoryStreaming(request: request)
        } else {
            await startStoryNonStreaming(request: request)
        }
    }

    /// Start story with streaming
    private func startStoryStreaming(request: StartStoryRequest) {
        streamingService.startStoryStream(
            request: request,
            onSessionStart: { sessionId in
                print("Session started: \(sessionId)")
            },
            onComplete: { [weak self] response in
                Task { @MainActor in
                    self?.handleStoryResponse(response)
                }
            }
        )
    }

    /// Start story without streaming
    private func startStoryNonStreaming(request: StartStoryRequest) async {
        do {
            let response = try await apiService.startStory(request: request)
            handleStoryResponse(response)
        } catch {
            handleError(error)
        }
    }

    // MARK: - Continue Story

    /// Continue story with a choice
    func continueStory(choice: Choice, useStreaming: Bool = true) async {
        guard let story = currentStory else { return }

        isLoading = true
        errorMessage = nil

        let request = ContinueStoryRequest(
            sessionId: story.sessionId,
            choiceId: choice.id,
            choiceText: choice.text,
            customInput: nil,
            storySummary: story.storySummary
        )

        if useStreaming {
            continueStoryStreaming(request: request)
        } else {
            await continueStoryNonStreaming(request: request)
        }
    }

    /// Continue story with custom input
    func continueStoryWithCustomInput(_ input: String, useStreaming: Bool = true) async {
        guard let story = currentStory else { return }

        isLoading = true
        errorMessage = nil

        let request = ContinueStoryRequest(
            sessionId: story.sessionId,
            choiceId: nil,
            choiceText: nil,
            customInput: input,
            storySummary: story.storySummary
        )

        if useStreaming {
            continueStoryStreaming(request: request)
        } else {
            await continueStoryNonStreaming(request: request)
        }
    }

    /// Continue story with streaming
    private func continueStoryStreaming(request: ContinueStoryRequest) {
        streamingService.continueStoryStream(
            request: request,
            onComplete: { [weak self] response in
                Task { @MainActor in
                    self?.handleStoryResponse(response)
                }
            }
        )
    }

    /// Continue story without streaming
    private func continueStoryNonStreaming(request: ContinueStoryRequest) async {
        do {
            let response = try await apiService.continueStory(request: request)
            handleStoryResponse(response)
        } catch {
            handleError(error)
        }
    }

    // MARK: - Story Management

    /// Handle story response
    private func handleStoryResponse(_ response: StoryResponse) {
        currentStory = response
        isLoading = false

        // Save to storage
        do {
            if response.metadata.turns == 1 {
                try storageService.saveStory(response, playerName: playerName, theme: currentTheme)
            } else {
                try storageService.updateStory(response)
            }
        } catch {
            print("Failed to save story: \(error)")
        }
    }

    /// Handle errors
    private func handleError(_ error: Error) {
        isLoading = false

        if let apiError = error as? APIError {
            switch apiError {
            case .rateLimitExceeded(let retryAfter):
                rateLimitTracker.setRateLimit(retryAfter: retryAfter)
                errorMessage = "Rate limit exceeded"

            case .safetyViolation(let message):
                errorMessage = message
                showError = true

            case .serverError(let message):
                errorMessage = message
                showError = true

            default:
                errorMessage = "Something went wrong. Please try again!"
                showError = true
            }
        } else {
            errorMessage = "Network error. Check your connection!"
            showError = true
        }
    }

    /// Reset current story
    func resetStory() async {
        guard let sessionId = currentStory?.sessionId else { return }

        do {
            try await apiService.resetSession(sessionId: sessionId)
            currentStory = nil
            isLoading = false
            errorMessage = nil
        } catch {
            handleError(error)
        }
    }

    /// Clear error
    func clearError() {
        errorMessage = nil
        showError = false
    }

    // MARK: - Computed Properties

    /// Check if story is finished
    var isStoryFinished: Bool {
        currentStory?.metadata.isFinished ?? false
    }

    /// Get current turn
    var currentTurn: Int {
        currentStory?.metadata.turns ?? 0
    }

    /// Get max turns
    var maxTurns: Int {
        currentStory?.metadata.maxTurns ?? 0
    }

    /// Get progress percentage
    var progress: Double {
        guard maxTurns > 0 else { return 0 }
        return Double(currentTurn) / Double(maxTurns)
    }
}
