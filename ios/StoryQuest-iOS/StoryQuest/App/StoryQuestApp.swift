//
//  StoryQuestApp.swift
//  StoryQuest
//
//  Main app entry point
//

import SwiftUI

@main
struct StoryQuestApp: App {
    @StateObject private var appEnvironment = AppEnvironment()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appEnvironment)
        }
    }
}

// MARK: - Content View

struct ContentView: View {
    @EnvironmentObject var appEnvironment: AppEnvironment
    @State private var showOnboarding = false

    var body: some View {
        Group {
            if showOnboarding {
                OnboardingView(onComplete: {
                    UserDefaults.standard.hasSeenOnboarding = true
                    showOnboarding = false
                })
            } else {
                ThemeSelectionView()
            }
        }
        .onAppear {
            showOnboarding = !UserDefaults.standard.hasSeenOnboarding
        }
    }
}

// MARK: - Onboarding View (Placeholder)

struct OnboardingView: View {
    let onComplete: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            Text("🎭")
                .font(.system(size: 80))

            Text("Welcome to StoryQuest!")
                .font(.sqTitle)
                .foregroundColor(.sqTextPrimary)

            Text("Create magical stories where YOU are the hero!")
                .font(.sqBody)
                .foregroundColor(.sqTextSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Spacer()

            Button(action: onComplete) {
                Text("Start Adventure")
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
            .padding()
        }
        .background(Color.sqBackground)
    }
}

#Preview {
    ContentView()
        .environmentObject(AppEnvironment())
}
