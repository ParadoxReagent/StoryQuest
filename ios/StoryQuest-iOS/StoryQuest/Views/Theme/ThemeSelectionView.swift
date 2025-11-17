//
//  ThemeSelectionView.swift
//  StoryQuest
//
//  Theme selection screen with dynamic theme loading
//

import SwiftUI

struct ThemeSelectionView: View {
    @StateObject private var themeViewModel = ThemeViewModel()
    @StateObject private var storyViewModel = StoryViewModel()
    @State private var selectedAgeRange: String = AppConstants.defaultAgeRange
    @State private var playerName: String = ""
    @State private var showStoryView: Bool = false
    @State private var showError: Bool = false

    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Text("🎭 StoryQuest")
                        .font(.sqTitle)
                        .foregroundColor(.sqTextPrimary)

                    Text("Choose your adventure!")
                        .font(.sqSubheadline)
                        .foregroundColor(.sqTextSecondary)
                }
                .padding(.top, 32)

                // Player name input
                VStack(alignment: .leading, spacing: 8) {
                    Text("What's your name?")
                        .font(.sqBody)
                        .foregroundColor(.sqTextPrimary)

                    TextField("Enter your name", text: $playerName)
                        .textFieldStyle(.roundedBorder)
                        .font(.sqBody)
                        .autocapitalization(.words)
                        .disableAutocorrection(true)
                        .onChange(of: playerName) { newValue in
                            // Limit name length
                            if newValue.count > AppConstants.maxPlayerNameLength {
                                playerName = String(newValue.prefix(AppConstants.maxPlayerNameLength))
                            }
                        }
                }
                .padding(.horizontal)

                // Age range selector
                VStack(alignment: .leading, spacing: 8) {
                    Text("Select your age")
                        .font(.sqBody)
                        .foregroundColor(.sqTextPrimary)

                    Picker("Age Range", selection: $selectedAgeRange) {
                        Text("Ages 6-8").tag("6-8")
                        Text("Ages 9-12").tag("9-12")
                    }
                    .pickerStyle(.segmented)
                    .onChange(of: selectedAgeRange) { newValue in
                        Task {
                            await themeViewModel.loadThemes(for: newValue)
                        }
                    }
                }
                .padding(.horizontal)

                // Theme grid
                ScrollView {
                    if themeViewModel.isLoading {
                        ProgressView("Loading themes...")
                            .padding()
                    } else {
                        LazyVGrid(columns: [GridItem(.adaptive(minimum: 300))], spacing: 16) {
                            ForEach(themeViewModel.themes) { theme in
                                ThemeCard(theme: theme) {
                                    startStory(with: theme)
                                }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        Task {
                            await themeViewModel.refreshThemes(for: selectedAgeRange)
                        }
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .alert("Error", isPresented: $showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text("Please enter your name to start!")
            }
            .fullScreenCover(isPresented: $showStoryView) {
                StoryView(viewModel: storyViewModel)
            }
        }
        .onAppear {
            // Load saved player name
            if let savedName = UserDefaults.standard.lastPlayerName {
                playerName = savedName
            }

            selectedAgeRange = UserDefaults.standard.lastAgeRange

            // Load themes
            Task {
                await themeViewModel.loadThemes(for: selectedAgeRange)
            }
        }
    }

    // MARK: - Actions

    private func startStory(with theme: Theme) {
        guard playerName.isValid else {
            showError = true
            return
        }

        // Save preferences
        UserDefaults.standard.lastPlayerName = playerName
        UserDefaults.standard.lastAgeRange = selectedAgeRange

        // Start story
        Task {
            await storyViewModel.startStory(
                playerName: playerName,
                ageRange: selectedAgeRange,
                theme: theme.id,
                useStreaming: true
            )
            showStoryView = true
        }
    }
}

#Preview {
    ThemeSelectionView()
}
