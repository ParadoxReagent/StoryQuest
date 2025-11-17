//
//  HistoryViewModel.swift
//  StoryQuest
//
//  ViewModel for story history management
//

import Foundation
import Combine

@MainActor
class HistoryViewModel: ObservableObject {
    @Published var savedSessions: [SavedSession] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var selectedSession: SavedSession?

    private let storageService: StorageService
    private let apiService: APIService

    init(
        storageService: StorageService = .shared,
        apiService: APIService = .shared
    ) {
        self.storageService = storageService
        self.apiService = apiService
    }

    // MARK: - Load History

    /// Load saved sessions from storage
    func loadHistory() {
        isLoading = true
        errorMessage = nil

        do {
            savedSessions = try storageService.getSavedSessions()
        } catch {
            errorMessage = "Failed to load history: \(error.localizedDescription)"
            savedSessions = []
        }

        isLoading = false
    }

    /// Refresh history from backend
    func refreshSession(_ session: SavedSession) async {
        do {
            let history = try await apiService.getSessionHistory(sessionId: session.id)
            // Update local storage with backend data
            updateSessionFromHistory(session, history: history)
        } catch {
            errorMessage = "Failed to refresh session: \(error.localizedDescription)"
        }
    }

    // MARK: - Session Management

    /// Select session for viewing
    func selectSession(_ session: SavedSession) {
        selectedSession = session
    }

    /// Delete session
    func deleteSession(_ session: SavedSession) {
        do {
            try storageService.deleteSession(session)
            loadHistory()  // Reload list
        } catch {
            errorMessage = "Failed to delete session: \(error.localizedDescription)"
        }
    }

    /// Delete all sessions
    func deleteAllSessions() {
        do {
            try storageService.deleteAllSessions()
            savedSessions = []
        } catch {
            errorMessage = "Failed to delete all sessions: \(error.localizedDescription)"
        }
    }

    /// Export session as text
    func exportSessionAsText(_ session: SavedSession) -> String {
        var text = """
        StoryQuest Adventure
        ====================

        Player: \(session.playerName)
        Theme: \(session.theme)
        Age Range: \(session.ageRange)
        Created: \(session.createdAt.fullDate)
        Total Turns: \(session.totalTurns)

        Story
        =====

        """

        for turn in session.turnsArray {
            text += """

            Turn \(turn.turnNumber)
            ---------
            \(turn.sceneText)

            """

            if let choice = turn.playerChoice {
                text += "Choice: \(choice)\n"
            }

            if let input = turn.customInput {
                text += "Custom Input: \(input)\n"
            }
        }

        return text
    }

    // MARK: - Private Methods

    /// Update session from backend history
    private func updateSessionFromHistory(_ session: SavedSession, history: SessionHistory) {
        // Update session metadata
        session.lastActivity = history.lastActivity
        session.totalTurns = Int16(history.totalTurns)
        session.isActive = history.isActive

        // This would require more complex Core Data update logic
        // For now, just reload from storage
        loadHistory()
    }

    // MARK: - Computed Properties

    /// Get active sessions
    var activeSessions: [SavedSession] {
        savedSessions.filter { $0.isActive }
    }

    /// Get completed sessions
    var completedSessions: [SavedSession] {
        savedSessions.filter { $0.isFinished }
    }

    /// Get total story count
    var totalStories: Int {
        savedSessions.count
    }
}
