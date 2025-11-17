//
//  LoadingView.swift
//  StoryQuest
//
//  Loading indicator component
//

import SwiftUI

struct LoadingView: View {
    let message: String

    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)

            Text(message)
                .font(.sqBody)
                .foregroundColor(.sqTextSecondary)
        }
        .padding()
    }
}

#Preview {
    LoadingView(message: "Loading...")
}
