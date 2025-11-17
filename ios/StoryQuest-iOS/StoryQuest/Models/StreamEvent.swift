//
//  StreamEvent.swift
//  StoryQuest
//
//  Server-Sent Events models for streaming
//

import Foundation

// MARK: - Stream Event Type

enum StreamEventType: String, Codable {
    case sessionStart = "session_start"
    case textChunk = "text_chunk"
    case complete = "complete"
    case error = "error"
}

// MARK: - Stream Event

struct StreamEvent: Codable {
    let type: StreamEventType
    let sessionId: UUID?
    let content: String?
    let sceneText: String?
    let choices: [Choice]?
    let metadata: StoryMetadata?
    let storySummary: String?
    let message: String?

    enum CodingKeys: String, CodingKey {
        case type
        case sessionId = "session_id"
        case content
        case sceneText = "scene_text"
        case choices
        case metadata
        case storySummary = "story_summary"
        case message
    }
}
