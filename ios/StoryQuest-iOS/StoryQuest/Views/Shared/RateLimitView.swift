//
//  RateLimitView.swift
//  StoryQuest
//
//  Rate limit display with countdown
//

import SwiftUI

struct RateLimitView: View {
    let retryAfter: Int
    let message: String

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "clock.badge.exclamationmark")
                .font(.system(size: 60))
                .foregroundColor(.orange)

            Text("Whoa, slow down!")
                .font(.sqHeadline)
                .foregroundColor(.sqTextPrimary)

            Text(message)
                .font(.sqBody)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)

            Text("This helps keep StoryQuest running smoothly for everyone!")
                .font(.sqCaption)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            // Countdown circle
            ZStack {
                Circle()
                    .stroke(Color.orange.opacity(0.2), lineWidth: 8)
                    .frame(width: 80, height: 80)

                Circle()
                    .trim(from: 0, to: progressValue)
                    .stroke(Color.orange, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .frame(width: 80, height: 80)
                    .rotationEffect(.degrees(-90))
                    .animation(.linear(duration: 1), value: retryAfter)

                Text("\(retryAfter)")
                    .font(.system(size: 24, weight: .bold, design: .rounded))
                    .foregroundColor(.orange)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.orange.opacity(0.1))
        )
        .padding()
    }

    private var progressValue: CGFloat {
        // Assuming max wait time of 5 minutes (300 seconds)
        let maxWait = 300.0
        return CGFloat(max(0, maxWait - Double(retryAfter)) / maxWait)
    }
}

#Preview {
    RateLimitView(retryAfter: 45, message: "Try again in 45 seconds")
}
