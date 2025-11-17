//
//  StoryCompletionView.swift
//  StoryQuest
//
//  Story completion screen
//

import SwiftUI

struct StoryCompletionView: View {
    let story: StoryResponse
    let onNewStory: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            // Completion badge
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [.green, .blue]),
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 120, height: 120)

                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.white)
            }
            .shadow(color: .black.opacity(0.2), radius: 10, x: 0, y: 5)

            // Title
            Text("Story Complete!")
                .font(.sqTitle)
                .foregroundColor(.sqTextPrimary)

            // Summary
            VStack(spacing: 8) {
                Text("You finished your \(story.metadata.theme.replacingOccurrences(of: "_", with: " ")) adventure!")
                    .font(.sqBody)
                    .foregroundColor(.sqTextSecondary)
                    .multilineTextAlignment(.center)

                Text("Total turns: \(story.metadata.turns)")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)
            }

            // Final scene
            Text(story.currentScene.text)
                .font(.sqBodyLarge)
                .foregroundColor(.sqTextPrimary)
                .multilineTextAlignment(.center)
                .lineSpacing(8)
                .padding()
                .background(Color.sqSurface)
                .cornerRadius(16)
                .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)

            Spacer()

            // Actions
            VStack(spacing: 12) {
                Button(action: onNewStory) {
                    Text("Start New Story")
                        .font(.sqButton)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [.blue, .purple]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .cornerRadius(12)
                }

                Button(action: {
                    // Navigate to history
                }) {
                    Text("View History")
                        .font(.sqButton)
                        .foregroundColor(.sqPrimary)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.sqSurface)
                        .cornerRadius(12)
                }
            }
        }
        .padding()
    }
}

#Preview {
    StoryCompletionView(
        story: StoryResponse(
            sessionId: UUID(),
            storySummary: "A great adventure!",
            currentScene: Scene(
                id: "final",
                text: "And they all lived happily ever after!",
                timestamp: Date()
            ),
            choices: [],
            metadata: StoryMetadata(
                turns: 10,
                theme: "space_adventure",
                ageRange: "6-8",
                maxTurns: 10,
                isFinished: true
            )
        ),
        onNewStory: {}
    )
}
