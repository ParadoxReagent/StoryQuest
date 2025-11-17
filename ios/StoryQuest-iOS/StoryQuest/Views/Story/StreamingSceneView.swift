//
//  StreamingSceneView.swift
//  StoryQuest
//
//  Streaming text display with typing animation
//

import SwiftUI

struct StreamingSceneView: View {
    @ObservedObject var streamingService: StreamingService
    @State private var cursorOpacity: Double = 1.0

    var body: some View {
        VStack(spacing: 20) {
            if streamingService.isStreaming {
                // Streaming text with cursor
                HStack(alignment: .bottom, spacing: 4) {
                    Text(streamingService.streamingText)
                        .font(.sqBodyLarge)
                        .foregroundColor(.sqTextPrimary)
                        .multilineTextAlignment(.center)
                        .lineSpacing(8)
                        .animation(.easeIn(duration: 0.1), value: streamingService.streamingText)

                    // Blinking cursor
                    Text("|")
                        .font(.sqBodyLarge)
                        .foregroundColor(.sqPrimary)
                        .opacity(cursorOpacity)
                }

                // Loading indicator
                ProgressView()
                    .scaleEffect(1.5)
                    .padding()

                Text("Creating your story...")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)
            }

            if let error = streamingService.streamError {
                ErrorView(message: error, onDismiss: {
                    streamingService.cancelStream()
                })
            }
        }
        .padding()
        .frame(maxWidth: 600)
        .onAppear {
            withAnimation(.easeInOut(duration: 0.5).repeatForever()) {
                cursorOpacity = 0.0
            }
        }
    }
}

#Preview {
    StreamingSceneView(streamingService: StreamingService())
}
