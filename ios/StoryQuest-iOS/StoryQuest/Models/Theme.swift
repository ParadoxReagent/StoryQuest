//
//  Theme.swift
//  StoryQuest
//
//  Dynamic theme models with backend generation support
//

import Foundation
import SwiftUI

// MARK: - Theme

struct Theme: Codable, Identifiable, Equatable {
    let id: String
    let name: String
    let description: String
    let emoji: String               // Backend provides emoji
    let color: String               // Tailwind gradient class

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case description
        case emoji
        case color
    }

    // Convert Tailwind gradient to SwiftUI gradient
    var gradient: LinearGradient {
        GradientParser.parse(color)
    }
}

// MARK: - Theme Generation Request

struct GenerateThemesRequest: Codable {
    let ageRange: String

    enum CodingKeys: String, CodingKey {
        case ageRange = "age_range"
    }
}

// MARK: - Theme Generation Response

struct GenerateThemesResponse: Codable {
    let themes: [Theme]

    enum CodingKeys: String, CodingKey {
        case themes
    }
}

// MARK: - Gradient Parser

struct GradientParser {
    /// Parse Tailwind gradient class to SwiftUI LinearGradient
    /// Examples: "from-indigo-400 to-purple-500", "from-green-400 to-emerald-500"
    static func parse(_ tailwindClass: String) -> LinearGradient {
        let components = tailwindClass.components(separatedBy: " ")

        var startColor: Color = .blue
        var endColor: Color = .purple

        for component in components {
            if component.hasPrefix("from-") {
                startColor = parseTailwindColor(component.replacingOccurrences(of: "from-", with: ""))
            } else if component.hasPrefix("to-") {
                endColor = parseTailwindColor(component.replacingOccurrences(of: "to-", with: ""))
            }
        }

        return LinearGradient(
            gradient: Gradient(colors: [startColor, endColor]),
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    /// Parse individual Tailwind color to SwiftUI Color
    private static func parseTailwindColor(_ colorName: String) -> Color {
        // Map Tailwind colors to SwiftUI colors
        let colorMap: [String: Color] = [
            // Blues
            "blue-400": Color(red: 0.37, green: 0.67, blue: 0.98),
            "blue-500": Color(red: 0.23, green: 0.53, blue: 0.98),
            "cyan-400": Color(red: 0.13, green: 0.79, blue: 0.88),
            "cyan-500": Color(red: 0.02, green: 0.71, blue: 0.84),
            "indigo-400": Color(red: 0.51, green: 0.55, blue: 0.98),
            "indigo-500": Color(red: 0.39, green: 0.42, blue: 0.98),

            // Purples
            "purple-400": Color(red: 0.67, green: 0.45, blue: 0.98),
            "purple-500": Color(red: 0.58, green: 0.29, blue: 0.98),
            "pink-400": Color(red: 0.98, green: 0.45, blue: 0.80),
            "pink-500": Color(red: 0.93, green: 0.26, blue: 0.71),

            // Greens
            "green-400": Color(red: 0.29, green: 0.87, blue: 0.47),
            "green-500": Color(red: 0.13, green: 0.80, blue: 0.33),
            "emerald-400": Color(red: 0.20, green: 0.83, blue: 0.60),
            "emerald-500": Color(red: 0.06, green: 0.73, blue: 0.51),

            // Oranges/Reds
            "orange-400": Color(red: 0.98, green: 0.60, blue: 0.22),
            "orange-500": Color(red: 0.98, green: 0.49, blue: 0.05),
            "red-400": Color(red: 0.98, green: 0.36, blue: 0.36),
            "red-500": Color(red: 0.94, green: 0.27, blue: 0.27),

            // Grays
            "gray-400": Color(red: 0.61, green: 0.64, blue: 0.69),
            "gray-500": Color(red: 0.42, green: 0.45, blue: 0.50)
        ]

        return colorMap[colorName] ?? .blue
    }
}
