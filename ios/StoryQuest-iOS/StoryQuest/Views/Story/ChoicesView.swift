//
//  ChoicesView.swift
//  StoryQuest
//
//  Choice buttons display
//

import SwiftUI

struct ChoicesView: View {
    let choices: [Choice]
    let isDisabled: Bool
    let onChoiceSelected: (Choice) -> Void

    var body: some View {
        VStack(spacing: 12) {
            Text("What will you do?")
                .font(.sqSubheadline)
                .foregroundColor(.sqTextSecondary)
                .padding(.top)

            ForEach(choices) { choice in
                ChoiceButton(
                    choice: choice,
                    isDisabled: isDisabled,
                    action: { onChoiceSelected(choice) }
                )
            }
        }
        .padding(.horizontal)
    }
}

// MARK: - Choice Button

struct ChoiceButton: View {
    let choice: Choice
    let isDisabled: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Text(choice.text)
                    .font(.sqButton)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.leading)
                    .lineLimit(2)

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.white)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [.blue, .purple]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.2), radius: 5, x: 0, y: 2)
        }
        .buttonStyle(ScaleButtonStyle())
        .disabled(isDisabled)
        .opacity(isDisabled ? 0.6 : 1.0)
    }
}

#Preview {
    ChoicesView(
        choices: [
            Choice(id: "1", text: "Enter the forest"),
            Choice(id: "2", text: "Walk around the edge"),
            Choice(id: "3", text: "Call out to see if anyone is there")
        ],
        isDisabled: false,
        onChoiceSelected: { _ in }
    )
}
