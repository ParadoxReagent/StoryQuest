//
//  AppEnvironment.swift
//  StoryQuest
//
//  Global app environment and configuration
//

import Foundation
import Combine

@MainActor
class AppEnvironment: ObservableObject {
    // Services
    let apiService: APIService
    let storageService: StorageService
    let ttsService: TTSService

    // App state
    @Published var isOnline: Bool = true
    @Published var serverHealth: Bool = false

    init() {
        // Initialize services
        let baseURL = UserDefaults.standard.apiBaseURL
        self.apiService = APIService(baseURL: baseURL)
        self.storageService = StorageService.shared
        self.ttsService = TTSService()

        // Check server health on init
        Task {
            await checkServerHealth()
        }
    }

    // MARK: - Server Health

    func checkServerHealth() async {
        do {
            serverHealth = try await apiService.healthCheck()
            isOnline = serverHealth
        } catch {
            print("Server health check failed: \(error)")
            serverHealth = false
            isOnline = false
        }
    }

    // MARK: - Configuration

    func updateAPIBaseURL(_ url: String) {
        UserDefaults.standard.apiBaseURL = url
        // Would need to reinitialize apiService here in production
    }

    // MARK: - TTS Configuration

    func configureTTS(enabled: Bool, voiceIdentifier: String?, rate: Float) {
        UserDefaults.standard.ttsEnabled = enabled

        if let voiceId = voiceIdentifier {
            UserDefaults.standard.ttsVoiceIdentifier = voiceId
            ttsService.setVoice(identifier: voiceId)
        }

        UserDefaults.standard.ttsRate = rate
        ttsService.setRate(rate)
    }
}
