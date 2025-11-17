//
//  CustomInputView.swift
//  StoryQuest
//
//  Custom text input sheet
//

import SwiftUI

struct CustomInputView: View {
    @Binding var input: String
    let onSubmit: () -> Void
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: "pencil.circle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.sqPrimary)

                    Text("Write Your Own Choice")
                        .font(.sqHeadline)
                        .foregroundColor(.sqTextPrimary)

                    Text("Be creative! Your choice will guide the story.")
                        .font(.sqBody)
                        .foregroundColor(.sqTextSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding()

                // Input field
                VStack(alignment: .leading, spacing: 8) {
                    Text("What do you do?")
                        .font(.sqBody)
                        .foregroundColor(.sqTextPrimary)

                    TextEditor(text: $input)
                        .frame(height: 120)
                        .padding(8)
                        .background(Color.sqSurface)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.sqPrimary.opacity(0.3), lineWidth: 1)
                        )

                    HStack {
                        Spacer()
                        Text("\(input.count)/\(AppConstants.maxCustomInputLength)")
                            .font(.sqCaption)
                            .foregroundColor(.sqTextSecondary)
                    }
                }
                .padding(.horizontal)

                // Safety message
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "shield.fill")
                            .foregroundColor(.green)
                        Text("Keep it safe and fun!")
                            .font(.sqCaption)
                            .foregroundColor(.sqTextSecondary)
                    }

                    Text("Inappropriate content will be filtered.")
                        .font(.sqCaption)
                        .foregroundColor(.sqTextSecondary)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(12)
                .padding(.horizontal)

                Spacer()

                // Submit button
                Button(action: {
                    guard input.isValid else { return }
                    onSubmit()
                }) {
                    Text("Continue Story")
                        .font(.sqButton)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [.blue, .purple]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .cornerRadius(12)
                }
                .disabled(!input.isValid)
                .opacity(input.isValid ? 1.0 : 0.6)
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .onChange(of: input) { newValue in
                // Limit input length
                if newValue.count > AppConstants.maxCustomInputLength {
                    input = String(newValue.prefix(AppConstants.maxCustomInputLength))
                }
            }
        }
    }
}

#Preview {
    CustomInputView(input: .constant(""), onSubmit: {})
}
