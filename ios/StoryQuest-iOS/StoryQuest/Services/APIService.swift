//
//  APIService.swift
//  StoryQuest
//
//  API service for backend communication with Phase 6 endpoints
//

import Foundation
import Combine

@MainActor
class APIService: ObservableObject {
    static let shared = APIService()

    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()

    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 90  // LLM can be slow
        config.timeoutIntervalForResource = 120
        self.session = URLSession(configuration: config)
    }

    // MARK: - Non-Streaming Endpoints

    /// Start a new story session
    func startStory(request: StartStoryRequest) async throws -> StoryResponse {
        let url = URL(string: "\(baseURL)/api/v1/story/start")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        return try JSONDecoder.storyQuestDecoder.decode(StoryResponse.self, from: data)
    }

    /// Continue an existing story
    func continueStory(request: ContinueStoryRequest) async throws -> StoryResponse {
        let url = URL(string: "\(baseURL)/api/v1/story/continue")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        return try JSONDecoder.storyQuestDecoder.decode(StoryResponse.self, from: data)
    }

    /// Generate dynamic themes based on age range
    func generateThemes(ageRange: String) async throws -> [Theme] {
        let url = URL(string: "\(baseURL)/api/v1/story/generate-themes")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let request = GenerateThemesRequest(ageRange: ageRange)
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        let result = try JSONDecoder.storyQuestDecoder.decode(GenerateThemesResponse.self, from: data)
        return result.themes
    }

    /// Get session history from backend
    func getSessionHistory(sessionId: UUID) async throws -> SessionHistory {
        let url = URL(string: "\(baseURL)/api/v1/story/session/\(sessionId.uuidString)")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"

        let (data, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)

        return try JSONDecoder.storyQuestDecoder.decode(SessionHistory.self, from: data)
    }

    /// Reset/abandon a session
    func resetSession(sessionId: UUID) async throws {
        let url = URL(string: "\(baseURL)/api/v1/story/reset")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let request = ResetSessionRequest(sessionId: sessionId)
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (_, response) = try await session.data(for: urlRequest)
        try handleHTTPResponse(response)
    }

    /// Health check endpoint
    func healthCheck() async throws -> Bool {
        let url = URL(string: "\(baseURL)/health")!
        let (_, response) = try await session.data(from: url)
        return (response as? HTTPURLResponse)?.statusCode == 200
    }

    // MARK: - HTTP Response Handling

    private func handleHTTPResponse(_ response: URLResponse) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return

        case 400:
            // Safety violation or validation error
            throw APIError.safetyViolation("Your input was filtered for safety. Please try something else!")

        case 404:
            throw APIError.serverError("Session not found")

        case 429:
            // Rate limit exceeded
            let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After")
            let seconds = Int(retryAfter ?? "60") ?? 60
            throw APIError.rateLimitExceeded(retryAfter: seconds)

        case 500...599:
            throw APIError.serverError("Server error. Please try again later.")

        default:
            throw APIError.invalidResponse
        }
    }
}

// MARK: - JSON Decoder Extension

extension JSONDecoder {
    static var storyQuestDecoder: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}

// MARK: - JSON Encoder Extension

extension JSONEncoder {
    static var storyQuestEncoder: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }
}
