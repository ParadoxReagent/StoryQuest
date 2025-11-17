//
//  StoryView.swift
//  StoryQuest
//
//  Main story interface with streaming support
//

import SwiftUI

struct StoryView: View {
    @ObservedObject var viewModel: StoryViewModel
    @StateObject private var ttsService = TTSService()
    @Environment(\.dismiss) var dismiss
    @State private var showCustomInput = false
    @State private var customInput = ""
    @State private var showExitConfirmation = false

    var body: some View {
        NavigationView {
            ZStack {
                Color.sqBackground
                    .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 24) {
                        // Progress indicator
                        if let story = viewModel.currentStory {
                            StoryProgressView(
                                currentTurn: story.metadata.turns,
                                maxTurns: story.metadata.maxTurns
                            )
                        }

                        // Story content
                        if viewModel.streamingService.isStreaming {
                            StreamingSceneView(streamingService: viewModel.streamingService)
                        } else if let story = viewModel.currentStory {
                            if story.metadata.isFinished {
                                StoryCompletionView(story: story, onNewStory: {
                                    dismiss()
                                })
                            } else {
                                SceneView(
                                    scene: story.currentScene,
                                    ttsService: ttsService
                                )

                                // Choices
                                ChoicesView(
                                    choices: story.choices,
                                    isDisabled: viewModel.isLoading || viewModel.rateLimitTracker.isRateLimited,
                                    onChoiceSelected: { choice in
                                        Task {
                                            await viewModel.continueStory(choice: choice)
                                        }
                                    }
                                )

                                // Custom input button
                                Button(action: { showCustomInput = true }) {
                                    HStack {
                                        Image(systemName: "pencil")
                                        Text("Write Your Own")
                                    }
                                    .font(.sqButton)
                                    .foregroundColor(.sqPrimary)
                                    .padding()
                                    .frame(maxWidth: .infinity)
                                    .background(Color.sqSurface)
                                    .cornerRadius(12)
                                }
                                .padding(.horizontal)
                                .disabled(viewModel.isLoading || viewModel.rateLimitTracker.isRateLimited)
                            }
                        } else if viewModel.isLoading {
                            LoadingView(message: "Starting your adventure...")
                        }

                        // Rate limit view
                        if viewModel.rateLimitTracker.isRateLimited {
                            RateLimitView(
                                retryAfter: viewModel.rateLimitTracker.retryAfter,
                                message: viewModel.rateLimitTracker.retryMessage
                            )
                        }

                        // Error view
                        if let error = viewModel.errorMessage, viewModel.showError {
                            ErrorView(message: error, onDismiss: {
                                viewModel.clearError()
                            })
                        }
                    }
                    .padding(.vertical)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Exit") {
                        showExitConfirmation = true
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    HStack {
                        // TTS controls
                        if !viewModel.streamingService.isStreaming {
                            TTSControlButton(ttsService: ttsService)
                        }
                    }
                }
            }
            .sheet(isPresented: $showCustomInput) {
                CustomInputView(
                    input: $customInput,
                    onSubmit: {
                        Task {
                            await viewModel.continueStoryWithCustomInput(customInput)
                            customInput = ""
                            showCustomInput = false
                        }
                    }
                )
            }
            .alert("Exit Story?", isPresented: $showExitConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Exit", role: .destructive) {
                    dismiss()
                }
            } message: {
                Text("Your progress will be saved. You can continue later!")
            }
        }
    }
}

#Preview {
    StoryView(viewModel: StoryViewModel())
}
