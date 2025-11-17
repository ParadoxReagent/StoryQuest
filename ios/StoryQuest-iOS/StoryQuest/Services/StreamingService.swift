//
//  StreamingService.swift
//  StoryQuest
//
//  Server-Sent Events streaming service for real-time story generation
//

import Foundation

@MainActor
class StreamingService: ObservableObject {
    @Published var streamingText: String = ""
    @Published var isStreaming: Bool = false
    @Published var streamError: String?

    private let baseURL: String
    private var streamTask: URLSessionDataTask?
    private var buffer: String = ""

    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL
    }

    // MARK: - Start Story Stream

    func startStoryStream(
        request: StartStoryRequest,
        onSessionStart: @escaping (UUID) -> Void,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        let url = URL(string: "\(baseURL)/api/v1/story/start/stream")!
        streamStory(url: url, request: request, onSessionStart: onSessionStart, onComplete: onComplete)
    }

    // MARK: - Continue Story Stream

    func continueStoryStream(
        request: ContinueStoryRequest,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        let url = URL(string: "\(baseURL)/api/v1/story/continue/stream")!
        streamStory(url: url, request: request, onSessionStart: { _ in }, onComplete: onComplete)
    }

    // MARK: - Generic Stream Handler

    private func streamStory<T: Encodable>(
        url: URL,
        request: T,
        onSessionStart: @escaping (UUID) -> Void,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        streamingText = ""
        isStreaming = true
        streamError = nil
        buffer = ""

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("text/event-stream", forHTTPHeaderField: "Accept")

        do {
            urlRequest.httpBody = try JSONEncoder.storyQuestEncoder.encode(request)
        } catch {
            streamError = "Failed to encode request"
            isStreaming = false
            return
        }

        let session = URLSession.shared
        let delegate = SSEDelegate(
            onData: { [weak self] data in
                Task { @MainActor in
                    self?.processSSEData(data, onSessionStart: onSessionStart, onComplete: onComplete)
                }
            },
            onComplete: { [weak self] in
                Task { @MainActor in
                    if self?.streamError == nil {
                        self?.isStreaming = false
                    }
                }
            },
            onError: { [weak self] error in
                Task { @MainActor in
                    self?.streamError = error.localizedDescription
                    self?.isStreaming = false
                }
            }
        )

        streamTask = session.dataTask(with: urlRequest)
        streamTask?.resume()
    }

    // MARK: - SSE Data Processing

    private func processSSEData(
        _ data: Data,
        onSessionStart: @escaping (UUID) -> Void,
        onComplete: @escaping (StoryResponse) -> Void
    ) {
        guard let text = String(data: data, encoding: .utf8) else {
            streamError = "Failed to decode stream data"
            isStreaming = false
            return
        }

        buffer += text
        let lines = buffer.components(separatedBy: "\n")

        // Keep last line in buffer if incomplete
        buffer = lines.last ?? ""

        for line in lines.dropLast() {
            // SSE format: "data: {json}"
            if line.hasPrefix("data: ") {
                let jsonString = String(line.dropFirst(6))  // Remove "data: "

                do {
                    guard let jsonData = jsonString.data(using: .utf8) else { continue }
                    let event = try JSONDecoder.storyQuestDecoder.decode(StreamEvent.self, from: jsonData)

                    switch event.type {
                    case .sessionStart:
                        if let sessionId = event.sessionId {
                            onSessionStart(sessionId)
                        }

                    case .textChunk:
                        if let content = event.content {
                            streamingText += content
                        }

                    case .complete:
                        // Build StoryResponse from complete event
                        if let sceneText = event.sceneText,
                           let choices = event.choices,
                           let metadata = event.metadata,
                           let storySummary = event.storySummary,
                           let sessionId = event.sessionId {

                            let scene = Scene(
                                id: "scene_\(sessionId)_\(metadata.turns)",
                                text: sceneText,
                                timestamp: Date()
                            )

                            let response = StoryResponse(
                                sessionId: sessionId,
                                storySummary: storySummary,
                                currentScene: scene,
                                choices: choices,
                                metadata: metadata
                            )

                            onComplete(response)
                        }

                        isStreaming = false

                    case .error:
                        streamError = event.message ?? "Unknown error"
                        isStreaming = false
                    }
                } catch {
                    print("Failed to decode SSE event: \(error)")
                    // Continue processing other events
                }
            }
        }
    }

    // MARK: - Cancel Stream

    func cancelStream() {
        streamTask?.cancel()
        isStreaming = false
        streamingText = ""
        buffer = ""
    }
}

// MARK: - SSE Delegate

private class SSEDelegate: NSObject, URLSessionDataDelegate {
    let onData: (Data) -> Void
    let onComplete: () -> Void
    let onError: (Error) -> Void

    init(
        onData: @escaping (Data) -> Void,
        onComplete: @escaping () -> Void,
        onError: @escaping (Error) -> Void
    ) {
        self.onData = onData
        self.onComplete = onComplete
        self.onError = onError
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        onData(data)
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        if let error = error {
            onError(error)
        } else {
            onComplete()
        }
    }
}
