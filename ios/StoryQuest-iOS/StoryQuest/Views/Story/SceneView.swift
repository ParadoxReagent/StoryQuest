//
//  SceneView.swift
//  StoryQuest
//
//  Scene display component
//

import SwiftUI

struct SceneView: View {
    let scene: Scene
    let ttsService: TTSService?

    var body: some View {
        VStack(spacing: 16) {
            // Scene text
            Text(scene.text)
                .font(.sqBodyLarge)
                .foregroundColor(.sqTextPrimary)
                .multilineTextAlignment(.center)
                .lineSpacing(8)
                .padding()
                .background(Color.sqSurface)
                .cornerRadius(16)
                .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
        }
        .padding(.horizontal)
        .onAppear {
            // Auto-play TTS if enabled
            if UserDefaults.standard.ttsEnabled, let tts = ttsService {
                tts.speak(text: scene.text)
            }
        }
    }
}

#Preview {
    SceneView(
        scene: Scene(
            id: "scene_1",
            text: "You find yourself at the edge of a mysterious forest. The trees are tall and ancient, and you can hear strange sounds coming from within. What will you do?",
            timestamp: Date()
        ),
        ttsService: nil
    )
}
