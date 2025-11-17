//
//  ErrorView.swift
//  StoryQuest
//
//  Error display component
//

import SwiftUI

struct ErrorView: View {
    let message: String
    let onDismiss: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 50))
                .foregroundColor(.orange)

            Text("Oops!")
                .font(.sqHeadline)
                .foregroundColor(.sqTextPrimary)

            Text(message)
                .font(.sqBody)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)

            Button(action: onDismiss) {
                Text("OK")
                    .font(.sqButton)
                    .foregroundColor(.white)
                    .padding(.horizontal, 32)
                    .padding(.vertical, 12)
                    .background(Color.orange)
                    .cornerRadius(12)
            }
        }
        .padding()
        .background(Color.sqSurface)
        .cornerRadius(16)
        .shadow(color: .black.opacity(0.2), radius: 10, x: 0, y: 5)
        .padding()
    }
}

#Preview {
    ErrorView(message: "Something went wrong. Please try again!", onDismiss: {})
}
