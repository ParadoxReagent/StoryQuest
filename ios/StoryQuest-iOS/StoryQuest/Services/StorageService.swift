//
//  StorageService.swift
//  StoryQuest
//
//  Local storage service using Core Data
//

import Foundation
import CoreData

@MainActor
class StorageService: ObservableObject {
    static let shared = StorageService()

    private let persistentContainer: NSPersistentContainer

    init() {
        persistentContainer = NSPersistentContainer(name: "StoryQuest")
        persistentContainer.loadPersistentStores { description, error in
            if let error = error {
                print("Core Data failed to load: \(error.localizedDescription)")
            }
        }

        persistentContainer.viewContext.automaticallyMergesChangesFromParent = true
    }

    var context: NSManagedObjectContext {
        persistentContainer.viewContext
    }

    // MARK: - Save Story

    /// Save story session to Core Data
    func saveStory(_ story: StoryResponse, playerName: String, theme: String) throws {
        let savedSession = SavedSession(context: context)
        savedSession.id = story.sessionId
        savedSession.playerName = playerName
        savedSession.theme = theme
        savedSession.ageRange = story.metadata.ageRange
        savedSession.createdAt = Date()
        savedSession.lastActivity = Date()
        savedSession.totalTurns = Int16(story.metadata.turns)
        savedSession.isActive = !story.metadata.isFinished
        savedSession.maxTurns = Int16(story.metadata.maxTurns)
        savedSession.isFinished = story.metadata.isFinished

        // Save current turn
        let turn = SavedTurn(context: context)
        turn.id = UUID()
        turn.turnNumber = Int16(story.metadata.turns)
        turn.sceneText = story.currentScene.text
        turn.sceneId = story.currentScene.id
        turn.storySummary = story.storySummary
        turn.createdAt = story.currentScene.timestamp
        turn.session = savedSession

        try context.save()
    }

    /// Update existing story session
    func updateStory(_ story: StoryResponse) throws {
        let request: NSFetchRequest<SavedSession> = SavedSession.fetchRequest()
        request.predicate = NSPredicate(format: "id == %@", story.sessionId as CVarArg)

        guard let session = try context.fetch(request).first else {
            throw NSError(domain: "StorageService", code: 404, userInfo: [NSLocalizedDescriptionKey: "Session not found"])
        }

        session.lastActivity = Date()
        session.totalTurns = Int16(story.metadata.turns)
        session.isActive = !story.metadata.isFinished
        session.isFinished = story.metadata.isFinished

        // Add new turn
        let turn = SavedTurn(context: context)
        turn.id = UUID()
        turn.turnNumber = Int16(story.metadata.turns)
        turn.sceneText = story.currentScene.text
        turn.sceneId = story.currentScene.id
        turn.storySummary = story.storySummary
        turn.createdAt = story.currentScene.timestamp
        turn.session = session

        try context.save()
    }

    // MARK: - Fetch Stories

    /// Get all saved sessions
    func getSavedSessions() throws -> [SavedSession] {
        let request: NSFetchRequest<SavedSession> = SavedSession.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(key: "lastActivity", ascending: false)]
        return try context.fetch(request)
    }

    /// Get session by ID
    func getSession(id: UUID) throws -> SavedSession? {
        let request: NSFetchRequest<SavedSession> = SavedSession.fetchRequest()
        request.predicate = NSPredicate(format: "id == %@", id as CVarArg)
        return try context.fetch(request).first
    }

    // MARK: - Delete Stories

    /// Delete session
    func deleteSession(_ session: SavedSession) throws {
        context.delete(session)
        try context.save()
    }

    /// Delete all sessions
    func deleteAllSessions() throws {
        let request: NSFetchRequest<NSFetchRequestResult> = SavedSession.fetchRequest()
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
        try persistentContainer.persistentStoreCoordinator.execute(deleteRequest, with: context)
        try context.save()
    }
}

// MARK: - Core Data Entities

@objc(SavedSession)
class SavedSession: NSManagedObject {
    @NSManaged var id: UUID
    @NSManaged var playerName: String
    @NSManaged var theme: String
    @NSManaged var ageRange: String
    @NSManaged var createdAt: Date
    @NSManaged var lastActivity: Date
    @NSManaged var totalTurns: Int16
    @NSManaged var maxTurns: Int16
    @NSManaged var isActive: Bool
    @NSManaged var isFinished: Bool
    @NSManaged var turns: NSSet?

    @nonobjc class func fetchRequest() -> NSFetchRequest<SavedSession> {
        return NSFetchRequest<SavedSession>(entityName: "SavedSession")
    }

    var turnsArray: [SavedTurn] {
        let set = turns as? Set<SavedTurn> ?? []
        return set.sorted { $0.turnNumber < $1.turnNumber }
    }
}

@objc(SavedTurn)
class SavedTurn: NSManagedObject {
    @NSManaged var id: UUID
    @NSManaged var turnNumber: Int16
    @NSManaged var sceneText: String
    @NSManaged var sceneId: String
    @NSManaged var playerChoice: String?
    @NSManaged var customInput: String?
    @NSManaged var storySummary: String
    @NSManaged var createdAt: Date
    @NSManaged var session: SavedSession?

    @nonobjc class func fetchRequest() -> NSFetchRequest<SavedTurn> {
        return NSFetchRequest<SavedTurn>(entityName: "SavedTurn")
    }
}
