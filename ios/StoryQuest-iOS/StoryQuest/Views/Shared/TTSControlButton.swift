//
//  TTSControlButton.swift
//  StoryQuest
//
//  Text-to-speech control button
//

import SwiftUI

struct TTSControlButton: View {
    @ObservedObject var ttsService: TTSService

    var body: some View {
        Button(action: toggleTTS) {
            Image(systemName: iconName)
                .font(.system(size: 20))
                .foregroundColor(.sqPrimary)
        }
    }

    private var iconName: String {
        if ttsService.isSpeaking {
            return ttsService.isPaused ? "play.circle" : "pause.circle"
        } else {
            return "speaker.wave.2.circle"
        }
    }

    private func toggleTTS() {
        if ttsService.isSpeaking {
            if ttsService.isPaused {
                ttsService.resume()
            } else {
                ttsService.pause()
            }
        } else {
            ttsService.stop()
        }
    }
}

#Preview {
    TTSControlButton(ttsService: TTSService())
}
