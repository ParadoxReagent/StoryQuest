//
//  ThemeViewModel.swift
//  StoryQuest
//
//  ViewModel for dynamic theme generation
//

import Foundation
import Combine

@MainActor
class ThemeViewModel: ObservableObject {
    @Published var themes: [Theme] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private let apiService: APIService

    // Fallback themes (used if dynamic generation fails)
    private let fallbackThemes: [Theme] = [
        Theme(
            id: "space_adventure",
            name: "Space Adventure",
            description: "Explore the stars and distant planets!",
            emoji: "🚀",
            color: "from-indigo-400 to-purple-500"
        ),
        Theme(
            id: "magical_forest",
            name: "Magical Forest",
            description: "Meet friendly forest creatures!",
            emoji: "🌲",
            color: "from-green-400 to-emerald-500"
        ),
        Theme(
            id: "underwater_quest",
            name: "Underwater Quest",
            description: "Dive into the deep blue ocean!",
            emoji: "🌊",
            color: "from-blue-400 to-cyan-500"
        ),
        Theme(
            id: "dinosaur_discovery",
            name: "Dinosaur Discovery",
            description: "Find ancient creatures!",
            emoji: "🦕",
            color: "from-orange-400 to-red-500"
        ),
        Theme(
            id: "castle_quest",
            name: "Castle Quest",
            description: "Explore a magical castle!",
            emoji: "🏰",
            color: "from-purple-400 to-pink-500"
        ),
        Theme(
            id: "robot_city",
            name: "Robot City",
            description: "Visit a futuristic city!",
            emoji: "🤖",
            color: "from-gray-400 to-blue-500"
        )
    ]

    init(apiService: APIService = .shared) {
        self.apiService = apiService
        // Load fallback themes initially
        self.themes = fallbackThemes
    }

    // MARK: - Theme Loading

    /// Load themes for age range (try dynamic, fall back to hardcoded)
    func loadThemes(for ageRange: String) async {
        isLoading = true
        errorMessage = nil

        do {
            // Try to generate dynamic themes
            let dynamicThemes = try await apiService.generateThemes(ageRange: ageRange)
            themes = dynamicThemes
        } catch {
            // Fall back to hardcoded themes
            print("Failed to load dynamic themes, using fallback: \(error)")
            themes = fallbackThemes
            errorMessage = "Using default themes (couldn't load custom ones)"
        }

        isLoading = false
    }

    /// Refresh themes
    func refreshThemes(for ageRange: String) async {
        await loadThemes(for: ageRange)
    }

    /// Get theme by ID
    func getTheme(id: String) -> Theme? {
        themes.first { $0.id == id }
    }
}
