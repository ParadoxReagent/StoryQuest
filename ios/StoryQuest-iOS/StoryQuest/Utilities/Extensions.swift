//
//  Extensions.swift
//  StoryQuest
//
//  Useful extensions for the app
//

import Foundation
import SwiftUI

// MARK: - String Extensions

extension String {
    /// Truncate string to max length
    func truncated(to length: Int, trailing: String = "...") -> String {
        if self.count > length {
            return String(self.prefix(length)) + trailing
        }
        return self
    }

    /// Check if string is valid (not empty after trimming)
    var isValid: Bool {
        !self.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    /// Trim whitespace
    var trimmed: String {
        self.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

// MARK: - View Extensions

extension View {
    /// Add corner radius to specific corners
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }

    /// Add haptic feedback
    func hapticFeedback(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) -> some View {
        self.onTapGesture {
            let generator = UIImpactFeedbackGenerator(style: style)
            generator.impactOccurred()
        }
    }

    /// Conditional modifier
    @ViewBuilder
    func `if`<Transform: View>(_ condition: Bool, transform: (Self) -> Transform) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
}

// MARK: - Rounded Corner Shape

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}

// MARK: - Date Extensions

extension Date {
    /// Format as relative time (e.g., "2 hours ago")
    var relativeTime: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: self, relativeTo: Date())
    }

    /// Format as short date (e.g., "Jan 15")
    var shortDate: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d"
        return formatter.string(from: self)
    }

    /// Format as full date (e.g., "January 15, 2025")
    var fullDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        return formatter.string(from: self)
    }
}

// MARK: - Double Extensions

extension Double {
    /// Format as percentage
    var asPercentage: String {
        "\(Int(self * 100))%"
    }
}

// MARK: - Collection Extensions

extension Collection {
    /// Safe subscript
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

// MARK: - Binding Extensions

extension Binding {
    /// Create binding with custom setter
    func onChange(_ handler: @escaping (Value) -> Void) -> Binding<Value> {
        Binding(
            get: { self.wrappedValue },
            set: { newValue in
                self.wrappedValue = newValue
                handler(newValue)
            }
        )
    }
}

// MARK: - Color Extensions

extension Color {
    /// Initialize from hex string
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }

    /// Convert to hex string
    var hexString: String {
        guard let components = UIColor(self).cgColor.components, components.count >= 3 else {
            return "#000000"
        }
        let r = Float(components[0])
        let g = Float(components[1])
        let b = Float(components[2])
        return String(format: "#%02lX%02lX%02lX", lroundf(r * 255), lroundf(g * 255), lroundf(b * 255))
    }
}
