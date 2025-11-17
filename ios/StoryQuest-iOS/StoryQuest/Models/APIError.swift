//
//  APIError.swift
//  StoryQuest
//
//  API error models
//

import Foundation

// MARK: - API Error

enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case serverError(String)
    case rateLimitExceeded(retryAfter: Int)
    case safetyViolation(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .invalidResponse:
            return "Invalid response from server"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .serverError(let message):
            return message
        case .rateLimitExceeded(let seconds):
            return "Rate limit exceeded. Try again in \(seconds) seconds"
        case .safetyViolation(let message):
            return message
        }
    }
}

// MARK: - Error Response

struct ErrorResponse: Codable {
    let detail: String
}

// MARK: - Rate Limit Error

struct RateLimitError: Error {
    let retryAfter: Int  // seconds
    let message: String
}
