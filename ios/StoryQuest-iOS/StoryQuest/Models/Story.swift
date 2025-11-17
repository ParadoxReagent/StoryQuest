//
//  Story.swift
//  StoryQuest
//
//  Core story data models
//

import Foundation

// MARK: - Story Metadata (Updated for Phase 6)

struct StoryMetadata: Codable, Equatable {
    let turns: Int
    let theme: String
    let ageRange: String
    let maxTurns: Int              // Dynamic max (8-15)
    let isFinished: Bool            // Completion status

    enum CodingKeys: String, CodingKey {
        case turns
        case theme
        case ageRange = "age_range"
        case maxTurns = "max_turns"
        case isFinished = "is_finished"
    }
}

// MARK: - Scene

struct Scene: Codable, Identifiable, Equatable {
    let id: String
    let text: String
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case id
        case text
        case timestamp
    }
}

// MARK: - Choice

struct Choice: Codable, Identifiable, Equatable {
    let id: String
    let text: String

    enum CodingKeys: String, CodingKey {
        case id
        case text
    }
}

// MARK: - Story Response

struct StoryResponse: Codable, Equatable {
    let sessionId: UUID
    let storySummary: String        // Required for continue requests
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

// MARK: - Start Story Request

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

// MARK: - Continue Story Request

struct ContinueStoryRequest: Codable {
    let sessionId: UUID
    let choiceId: String?
    let choiceText: String?
    let customInput: String?
    let storySummary: String        // Required

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case choiceId = "choice_id"
        case choiceText = "choice_text"
        case customInput = "custom_input"
        case storySummary = "story_summary"
    }
}

// MARK: - Reset Session Request

struct ResetSessionRequest: Codable {
    let sessionId: UUID

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
    }
}
