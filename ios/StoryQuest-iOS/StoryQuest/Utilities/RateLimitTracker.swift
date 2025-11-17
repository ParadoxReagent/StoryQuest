//
//  RateLimitTracker.swift
//  StoryQuest
//
//  Client-side rate limit tracking and countdown
//

import Foundation
import Combine

@MainActor
class RateLimitTracker: ObservableObject {
    @Published var isRateLimited: Bool = false
    @Published var retryAfter: Int = 0
    @Published var retryMessage: String = ""

    private var retryTimer: Timer?

    // MARK: - Rate Limit Management

    /// Set rate limit with countdown
    func setRateLimit(retryAfter: Int) {
        self.retryAfter = retryAfter
        self.isRateLimited = true
        self.retryMessage = formatRetryMessage(seconds: retryAfter)

        // Start countdown timer
        retryTimer?.invalidate()
        retryTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }

            Task { @MainActor in
                self.retryAfter -= 1

                if self.retryAfter <= 0 {
                    self.clearRateLimit()
                } else {
                    self.retryMessage = self.formatRetryMessage(seconds: self.retryAfter)
                }
            }
        }
    }

    /// Clear rate limit
    func clearRateLimit() {
        retryTimer?.invalidate()
        retryTimer = nil
        isRateLimited = false
        retryAfter = 0
        retryMessage = ""
    }

    // MARK: - Helper Methods

    /// Format retry message based on seconds
    private func formatRetryMessage(seconds: Int) -> String {
        if seconds < 60 {
            return "Try again in \(seconds) second\(seconds == 1 ? "" : "s")"
        } else {
            let minutes = seconds / 60
            let remainingSeconds = seconds % 60
            if remainingSeconds == 0 {
                return "Try again in \(minutes) minute\(minutes == 1 ? "" : "s")"
            } else {
                return "Try again in \(minutes)m \(remainingSeconds)s"
            }
        }
    }

    deinit {
        retryTimer?.invalidate()
    }
}
