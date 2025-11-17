//
//  ThemeCard.swift
//  StoryQuest
//
//  Theme card component with gradient and emoji
//

import SwiftUI

struct ThemeCard: View {
    let theme: Theme
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 16) {
                // Emoji
                Text(theme.emoji)
                    .font(.system(size: 60))

                // Title
                Text(theme.name)
                    .font(.sqHeadline)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)

                // Description
                Text(theme.description)
                    .font(.sqBody)
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
            }
            .padding(24)
            .frame(maxWidth: .infinity)
            .frame(height: 220)
            .background(theme.gradient)
            .cornerRadius(20)
            .shadow(color: .black.opacity(0.2), radius: 10, x: 0, y: 5)
        }
        .buttonStyle(ScaleButtonStyle())
    }
}

// MARK: - Scale Button Style

struct ScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

#Preview {
    ThemeCard(
        theme: Theme(
            id: "space_adventure",
            name: "Space Adventure",
            description: "Explore the stars!",
            emoji: "🚀",
            color: "from-indigo-400 to-purple-500"
        ),
        action: {}
    )
    .padding()
}
