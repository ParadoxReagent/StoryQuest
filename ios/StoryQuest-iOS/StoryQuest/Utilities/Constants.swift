//
//  Constants.swift
//  StoryQuest
//
//  App constants and configuration
//

import Foundation
import SwiftUI

// MARK: - API Configuration

struct APIConfig {
    static let baseURL = "http://localhost:8000"
    static let apiVersion = "v1"

    static var storyEndpoint: String {
        "\(baseURL)/api/\(apiVersion)/story"
    }
}

// MARK: - App Constants

struct AppConstants {
    // Age ranges
    static let ageRanges = ["6-8", "9-12"]

    // Default values
    static let defaultAgeRange = "6-8"
    static let defaultTheme = "space_adventure"

    // Limits
    static let maxPlayerNameLength = 20
    static let maxCustomInputLength = 200

    // Animation durations
    static let shortAnimation = 0.3
    static let mediumAnimation = 0.5
    static let longAnimation = 0.8
}

// MARK: - Color Extensions

extension Color {
    static let sqPrimary = Color("Primary", bundle: nil)
    static let sqSecondary = Color("Secondary", bundle: nil)
    static let sqBackground = Color("Background", bundle: nil)
    static let sqSurface = Color("Surface", bundle: nil)
    static let sqTextPrimary = Color("TextPrimary", bundle: nil)
    static let sqTextSecondary = Color("TextSecondary", bundle: nil)
    static let sqError = Color("Error", bundle: nil)
    static let sqSuccess = Color("Success", bundle: nil)

    // Fallback colors if assets not available
    static var sqPrimaryFallback: Color { Color.blue }
    static var sqSecondaryFallback: Color { Color.purple }
    static var sqBackgroundFallback: Color { Color(.systemBackground) }
    static var sqSurfaceFallback: Color { Color(.secondarySystemBackground) }
    static var sqTextPrimaryFallback: Color { Color(.label) }
    static var sqTextSecondaryFallback: Color { Color(.secondaryLabel) }
    static var sqErrorFallback: Color { Color.red }
    static var sqSuccessFallback: Color { Color.green }
}

// MARK: - Font Extensions

extension Font {
    static let sqTitle = Font.system(size: 34, weight: .bold, design: .rounded)
    static let sqHeadline = Font.system(size: 24, weight: .semibold, design: .rounded)
    static let sqSubheadline = Font.system(size: 20, weight: .medium, design: .rounded)
    static let sqBody = Font.system(size: 17, weight: .regular, design: .rounded)
    static let sqBodyLarge = Font.system(size: 20, weight: .regular, design: .rounded)
    static let sqCaption = Font.system(size: 14, weight: .regular, design: .rounded)
    static let sqButton = Font.system(size: 18, weight: .semibold, design: .rounded)
}

// MARK: - UserDefaults Keys

extension UserDefaults {
    enum Keys {
        static let hasSeenOnboarding = "hasSeenOnboarding"
        static let ttsEnabled = "ttsEnabled"
        static let ttsVoiceIdentifier = "ttsVoiceIdentifier"
        static let ttsRate = "ttsRate"
        static let lastPlayerName = "lastPlayerName"
        static let lastAgeRange = "lastAgeRange"
        static let apiBaseURL = "apiBaseURL"
    }

    var hasSeenOnboarding: Bool {
        get { bool(forKey: Keys.hasSeenOnboarding) }
        set { set(newValue, forKey: Keys.hasSeenOnboarding) }
    }

    var ttsEnabled: Bool {
        get { bool(forKey: Keys.ttsEnabled) }
        set { set(newValue, forKey: Keys.ttsEnabled) }
    }

    var ttsVoiceIdentifier: String? {
        get { string(forKey: Keys.ttsVoiceIdentifier) }
        set { set(newValue, forKey: Keys.ttsVoiceIdentifier) }
    }

    var ttsRate: Float {
        get {
            let rate = float(forKey: Keys.ttsRate)
            return rate == 0 ? 0.5 : rate  // Default to 0.5
        }
        set { set(newValue, forKey: Keys.ttsRate) }
    }

    var lastPlayerName: String? {
        get { string(forKey: Keys.lastPlayerName) }
        set { set(newValue, forKey: Keys.lastPlayerName) }
    }

    var lastAgeRange: String {
        get { string(forKey: Keys.lastAgeRange) ?? AppConstants.defaultAgeRange }
        set { set(newValue, forKey: Keys.lastAgeRange) }
    }

    var apiBaseURL: String {
        get { string(forKey: Keys.apiBaseURL) ?? APIConfig.baseURL }
        set { set(newValue, forKey: Keys.apiBaseURL) }
    }
}
