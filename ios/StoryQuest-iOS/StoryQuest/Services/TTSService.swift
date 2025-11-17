//
//  TTSService.swift
//  StoryQuest
//
//  Text-to-speech service using AVFoundation
//

import Foundation
import AVFoundation

@MainActor
class TTSService: NSObject, ObservableObject {
    @Published var isSpeaking: Bool = false
    @Published var isPaused: Bool = false
    @Published var speakingRate: Float = 0.5
    @Published var selectedVoice: AVSpeechSynthesisVoice?

    private let synthesizer = AVSpeechSynthesizer()
    private var currentUtterance: AVSpeechUtterance?

    override init() {
        super.init()
        synthesizer.delegate = self

        // Set default voice (child-friendly)
        if let voice = AVSpeechSynthesisVoice(language: "en-US") {
            selectedVoice = voice
        }
    }

    // MARK: - Speech Control

    /// Speak text with TTS
    func speak(text: String) {
        // Stop any current speech
        stop()

        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = selectedVoice
        utterance.rate = speakingRate
        utterance.pitchMultiplier = 1.2  // Slightly higher pitch for kids
        utterance.volume = 1.0

        currentUtterance = utterance
        synthesizer.speak(utterance)
        isSpeaking = true
    }

    /// Pause speech
    func pause() {
        guard isSpeaking else { return }
        synthesizer.pauseSpeaking(at: .word)
        isPaused = true
    }

    /// Resume speech
    func resume() {
        guard isPaused else { return }
        synthesizer.continueSpeaking()
        isPaused = false
    }

    /// Stop speech
    func stop() {
        synthesizer.stopSpeaking(at: .immediate)
        isSpeaking = false
        isPaused = false
        currentUtterance = nil
    }

    // MARK: - Voice Selection

    /// Get available voices
    func getAvailableVoices() -> [AVSpeechSynthesisVoice] {
        let voices = AVSpeechSynthesisVoice.speechVoices()
        // Filter for English voices only
        return voices.filter { $0.language.hasPrefix("en") }
    }

    /// Set voice by identifier
    func setVoice(identifier: String) {
        if let voice = AVSpeechSynthesisVoice(identifier: identifier) {
            selectedVoice = voice
        }
    }

    /// Set speaking rate (0.0 to 1.0)
    func setRate(_ rate: Float) {
        speakingRate = max(0.0, min(1.0, rate))
    }
}

// MARK: - AVSpeechSynthesizerDelegate

extension TTSService: AVSpeechSynthesizerDelegate {
    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didStart utterance: AVSpeechUtterance) {
        Task { @MainActor in
            isSpeaking = true
            isPaused = false
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        Task { @MainActor in
            isSpeaking = false
            isPaused = false
            currentUtterance = nil
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didPause utterance: AVSpeechUtterance) {
        Task { @MainActor in
            isPaused = true
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didContinue utterance: AVSpeechUtterance) {
        Task { @MainActor in
            isPaused = false
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        Task { @MainActor in
            isSpeaking = false
            isPaused = false
            currentUtterance = nil
        }
    }
}
