//
//  SessionHistory.swift
//  StoryQuest
//
//  Models for session history retrieval
//

import Foundation

// MARK: - Session History

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

// MARK: - Session Turn

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
