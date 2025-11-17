//
//  StoryProgressView.swift
//  StoryQuest
//
//  Story progress indicator with turn count
//

import SwiftUI

struct StoryProgressView: View {
    let currentTurn: Int
    let maxTurns: Int

    var progress: Double {
        guard maxTurns > 0 else { return 0 }
        return Double(currentTurn) / Double(maxTurns)
    }

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text("Turn \(currentTurn) of \(maxTurns)")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)

                Spacer()

                Text("\(Int(progress * 100))%")
                    .font(.sqCaption)
                    .foregroundColor(.sqTextSecondary)
            }

            ProgressView(value: progress)
                .tint(.sqPrimary)
        }
        .padding()
    }
}

#Preview {
    StoryProgressView(currentTurn: 3, maxTurns: 12)
}
