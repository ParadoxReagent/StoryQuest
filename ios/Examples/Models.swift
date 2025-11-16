// StoryQuest iOS - Data Models
// Example implementation of Swift models matching the backend API
//
// Copy these models into your Xcode project under Models/

import Foundation

// MARK: - Story Models

/// Represents a single choice option for the player
struct Choice: Codable, Identifiable, Hashable {
    let id: String
    let text: String

    enum CodingKeys: String, CodingKey {
        case id = "choice_id"
        case text
    }
}

/// Represents a single scene in the story
struct Scene: Codable, Identifiable, Hashable {
    let id: String
    let text: String
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case id = "scene_id"
        case text
        case timestamp
    }
}

/// Metadata about the story session
struct StoryMetadata: Codable, Hashable {
    let turns: Int
    let theme: String
    let ageRange: String

    enum CodingKeys: String, CodingKey {
        case turns
        case theme
        case ageRange = "age_range"
    }
}

/// Response from the backend API containing story state
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

/// Request to start a new story
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

/// Request to continue an existing story
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

// MARK: - App-Specific Models

/// Represents a story theme with UI properties
struct Theme: Identifiable, Hashable {
    let id: String
    let name: String
    let icon: String // SF Symbol name
    let colorHex: String
    let gradientHexes: [String]
    let description: String

    /// All available themes
    static let allThemes: [Theme] = [
        Theme(
            id: "magical_forest",
            name: "Magical Forest",
            icon: "leaf.fill",
            colorHex: "#4CAF50",
            gradientHexes: ["#4CAF50", "#8BC34A"],
            description: "Explore enchanted woods full of friendly creatures and sparkling magic!"
        ),
        Theme(
            id: "space_adventure",
            name: "Space Adventure",
            icon: "sparkles",
            colorHex: "#2196F3",
            gradientHexes: ["#2196F3", "#03A9F4"],
            description: "Blast off to distant planets and meet amazing aliens!"
        ),
        Theme(
            id: "underwater_quest",
            name: "Underwater Quest",
            icon: "drop.fill",
            colorHex: "#00BCD4",
            gradientHexes: ["#00BCD4", "#00ACC1"],
            description: "Dive deep into the ocean and discover hidden treasures!"
        ),
        Theme(
            id: "dinosaur_discovery",
            name: "Dinosaur Discovery",
            icon: "globe.americas.fill",
            colorHex: "#FF9800",
            gradientHexes: ["#FF9800", "#FFC107"],
            description: "Travel back in time to meet friendly dinosaurs!"
        ),
        Theme(
            id: "castle_quest",
            name: "Castle Quest",
            icon: "crown.fill",
            colorHex: "#9C27B0",
            gradientHexes: ["#9C27B0", "#BA68C8"],
            description: "Explore magical castles and help brave knights!"
        ),
        Theme(
            id: "robot_city",
            name: "Robot City",
            icon: "cube.fill",
            colorHex: "#607D8B",
            gradientHexes: ["#607D8B", "#78909C"],
            description: "Visit a futuristic city full of helpful robots!"
        )
    ]
}

/// Age range options for story content
enum AgeRange: String, CaseIterable, Identifiable {
    case young = "6-8"
    case older = "9-12"

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .young: return "Ages 6-8"
        case .older: return "Ages 9-12"
        }
    }

    var description: String {
        switch self {
        case .young: return "Simpler words and shorter stories"
        case .older: return "More challenging and longer adventures"
        }
    }
}

/// Represents a single turn in the story
struct StoryTurn: Identifiable, Hashable {
    let id: UUID
    let scene: Scene
    let chosenText: String
    let timestamp: Date

    init(scene: Scene, chosenText: String) {
        self.id = UUID()
        self.scene = scene
        self.chosenText = chosenText
        self.timestamp = Date()
    }
}

// MARK: - Health Check Response

/// Response from health check endpoint
struct HealthResponse: Codable {
    let status: String
    let service: String
    let version: String?
    let database: String?
    let llmProvider: String?

    enum CodingKeys: String, CodingKey {
        case status
        case service
        case version
        case database
        case llmProvider = "llm_provider"
    }
}

// MARK: - Error Response

/// Error response from API
struct APIErrorResponse: Codable {
    let detail: String
}

// MARK: - Extensions

extension JSONDecoder {
    /// Shared decoder configured for StoryQuest API
    static var storyQuestDecoder: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}

extension JSONEncoder {
    /// Shared encoder configured for StoryQuest API
    static var storyQuestEncoder: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }
}
