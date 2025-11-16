// StoryQuest iOS - Theme Selection View
// Example implementation of the theme selection screen
//
// Copy this into your Xcode project under Views/Theme/

import SwiftUI

struct ThemeSelectionView: View {
    @StateObject private var viewModel = ThemeSelectionViewModel()
    @State private var playerName: String = ""
    @State private var selectedAgeRange: AgeRange = .young
    @State private var selectedTheme: Theme?

    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [
                    Color(hex: "#E3F2FD"),
                    Color(hex: "#BBDEFB")
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            ScrollView {
                VStack(spacing: 32) {
                    // Title
                    Text("StoryQuest")
                        .font(.system(size: 56, weight: .bold, design: .rounded))
                        .foregroundColor(Color(hex: "#1976D2"))
                        .padding(.top, 40)

                    Text("Choose Your Adventure!")
                        .font(.system(size: 32, weight: .semibold, design: .rounded))
                        .foregroundColor(Color(hex: "#424242"))

                    // Player name input
                    VStack(alignment: .leading, spacing: 12) {
                        Text("What's your name?")
                            .font(.system(size: 24, weight: .semibold, design: .rounded))
                            .foregroundColor(Color(hex: "#424242"))

                        TextField("Enter your name", text: $playerName)
                            .font(.system(size: 28, weight: .regular, design: .rounded))
                            .padding()
                            .background(Color.white)
                            .cornerRadius(16)
                            .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
                            .autocapitalization(.words)
                            .disableAutocorrection(true)
                    }
                    .padding(.horizontal, 40)

                    // Age range selector
                    VStack(alignment: .leading, spacing: 12) {
                        Text("How old are you?")
                            .font(.system(size: 24, weight: .semibold, design: .rounded))
                            .foregroundColor(Color(hex: "#424242"))

                        HStack(spacing: 16) {
                            ForEach(AgeRange.allCases) { ageRange in
                                Button(action: {
                                    selectedAgeRange = ageRange
                                    // Haptic feedback
                                    let generator = UIImpactFeedbackGenerator(style: .light)
                                    generator.impactOccurred()
                                }) {
                                    VStack(spacing: 8) {
                                        Text(ageRange.displayName)
                                            .font(.system(size: 22, weight: .semibold, design: .rounded))

                                        Text(ageRange.description)
                                            .font(.system(size: 16, weight: .regular, design: .rounded))
                                            .multilineTextAlignment(.center)
                                            .fixedSize(horizontal: false, vertical: true)
                                    }
                                    .foregroundColor(selectedAgeRange == ageRange ? .white : Color(hex: "#424242"))
                                    .padding()
                                    .frame(maxWidth: .infinity)
                                    .background(
                                        selectedAgeRange == ageRange ?
                                            Color(hex: "#4CAF50") : Color.white
                                    )
                                    .cornerRadius(16)
                                    .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
                                }
                            }
                        }
                    }
                    .padding(.horizontal, 40)

                    // Theme grid
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Pick a theme:")
                            .font(.system(size: 24, weight: .semibold, design: .rounded))
                            .foregroundColor(Color(hex: "#424242"))
                            .padding(.horizontal, 40)

                        LazyVGrid(columns: [
                            GridItem(.flexible(), spacing: 24),
                            GridItem(.flexible(), spacing: 24),
                            GridItem(.flexible(), spacing: 24)
                        ], spacing: 24) {
                            ForEach(Theme.allThemes) { theme in
                                ThemeCard(
                                    theme: theme,
                                    isSelected: selectedTheme?.id == theme.id
                                )
                                .onTapGesture {
                                    selectedTheme = theme
                                    // Haptic feedback
                                    let generator = UIImpactFeedbackGenerator(style: .medium)
                                    generator.impactOccurred()
                                }
                            }
                        }
                        .padding(.horizontal, 40)
                    }

                    // Start button
                    Button(action: startAdventure) {
                        HStack {
                            Image(systemName: "play.circle.fill")
                                .font(.system(size: 28))

                            Text("Start My Adventure!")
                                .font(.system(size: 28, weight: .bold, design: .rounded))
                        }
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: 600)
                        .background(
                            LinearGradient(
                                colors: [Color(hex: "#4CAF50"), Color(hex: "#66BB6A")],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .cornerRadius(20)
                        .shadow(color: Color.black.opacity(0.2), radius: 12, x: 0, y: 6)
                    }
                    .disabled(!canStart)
                    .opacity(canStart ? 1.0 : 0.5)
                    .padding(.horizontal, 40)
                    .padding(.bottom, 40)
                }
            }

            // Loading overlay
            if viewModel.isLoading {
                LoadingView(message: "Creating your story...")
            }

            // Error alert
            if viewModel.errorMessage != nil {
                ErrorView(
                    message: viewModel.errorMessage ?? "An error occurred",
                    onDismiss: { viewModel.errorMessage = nil }
                )
            }
        }
        .onAppear {
            // Pre-select first theme
            if selectedTheme == nil {
                selectedTheme = Theme.allThemes.first
            }
        }
    }

    private var canStart: Bool {
        !playerName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        selectedTheme != nil &&
        !viewModel.isLoading
    }

    private func startAdventure() {
        guard let theme = selectedTheme else { return }

        // Haptic feedback
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)

        viewModel.startStory(
            playerName: playerName.trimmingCharacters(in: .whitespacesAndNewlines),
            ageRange: selectedAgeRange,
            theme: theme
        )
    }
}

// MARK: - Theme Card

struct ThemeCard: View {
    let theme: Theme
    let isSelected: Bool

    var body: some View {
        VStack(spacing: 16) {
            // Icon
            Image(systemName: theme.icon)
                .font(.system(size: 64))
                .foregroundColor(.white)
                .frame(width: 120, height: 120)
                .background(
                    LinearGradient(
                        colors: theme.gradientHexes.map { Color(hex: $0) },
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .clipShape(Circle())
                .shadow(color: Color.black.opacity(0.15), radius: 8, x: 0, y: 4)

            // Name
            Text(theme.name)
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .foregroundColor(Color(hex: "#212121"))
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .minimumScaleFactor(0.8)

            // Description
            Text(theme.description)
                .font(.system(size: 16, weight: .regular, design: .rounded))
                .foregroundColor(Color(hex: "#757575"))
                .multilineTextAlignment(.center)
                .lineLimit(3)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding()
        .frame(width: 280, height: 320)
        .background(Color.white)
        .cornerRadius(24)
        .overlay(
            RoundedRectangle(cornerRadius: 24)
                .stroke(
                    isSelected ? Color(hex: theme.colorHex) : Color.clear,
                    lineWidth: 4
                )
        )
        .shadow(
            color: Color.black.opacity(isSelected ? 0.2 : 0.1),
            radius: isSelected ? 16 : 8,
            x: 0,
            y: isSelected ? 8 : 4
        )
        .scaleEffect(isSelected ? 1.05 : 1.0)
        .animation(.spring(response: 0.3), value: isSelected)
    }
}

// MARK: - Loading View

struct LoadingView: View {
    let message: String

    var body: some View {
        ZStack {
            Color.black.opacity(0.4)
                .ignoresSafeArea()

            VStack(spacing: 24) {
                ProgressView()
                    .scaleEffect(2.0)
                    .tint(.white)

                Text(message)
                    .font(.system(size: 24, weight: .semibold, design: .rounded))
                    .foregroundColor(.white)
            }
            .padding(40)
            .background(Color(hex: "#424242"))
            .cornerRadius(24)
            .shadow(radius: 20)
        }
    }
}

// MARK: - Error View

struct ErrorView: View {
    let message: String
    let onDismiss: () -> Void

    var body: some View {
        ZStack {
            Color.black.opacity(0.4)
                .ignoresSafeArea()

            VStack(spacing: 24) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 64))
                    .foregroundColor(Color(hex: "#F44336"))

                Text("Oops!")
                    .font(.system(size: 32, weight: .bold, design: .rounded))
                    .foregroundColor(Color(hex: "#212121"))

                Text(message)
                    .font(.system(size: 20, weight: .regular, design: .rounded))
                    .foregroundColor(Color(hex: "#757575"))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)

                Button(action: onDismiss) {
                    Text("Try Again")
                        .font(.system(size: 22, weight: .semibold, design: .rounded))
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color(hex: "#4CAF50"))
                        .cornerRadius(16)
                }
                .padding(.horizontal)
            }
            .padding(40)
            .background(Color.white)
            .cornerRadius(24)
            .shadow(radius: 20)
            .frame(maxWidth: 500)
            .padding()
        }
    }
}

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Preview

struct ThemeSelectionView_Previews: PreviewProvider {
    static var previews: some View {
        ThemeSelectionView()
            .previewDevice("iPad Pro (12.9-inch) (6th generation)")
            .previewDisplayName("iPad Pro 12.9\"")
    }
}
