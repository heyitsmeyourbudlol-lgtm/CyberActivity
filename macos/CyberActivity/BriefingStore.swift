import AppKit
import Foundation
import SwiftUI

@MainActor
final class BriefingStore: ObservableObject {
    @Published var articles: [Article] = []
    @Published var executiveSummary = "Pulling the landscape…"
    @Published var summaryModel: String?
    @Published var summaryProvider: String?
    @Published var isLoading = false
    @Published var lastRefreshed: Date?
    @Published var errorMessage: String?
    @Published var selectedActor: ThreatActor?
    @Published var selectedArticle: Article?
    @Published var articleBeats: [String: String] = [:]
    @Published var articleSummaries: [String: SummaryResult] = [:]
    @Published var enabledSources: Set<FeedSource> = Set(FeedSource.allCases)

    private let cacheURL: URL = {
        let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            .appendingPathComponent("CyberActivity", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir.appendingPathComponent("briefing.json")
    }()

    init() {
        loadCache()
    }

    var filteredArticles: [Article] {
        guard let selectedActor else { return articles }
        return articles.filter { $0.actors.contains(selectedActor) }
    }

    var countsByActor: [(ThreatActor, Int)] {
        ThreatActor.allCases.map { actor in
            (actor, articles.filter { $0.actors.contains(actor) }.count)
        }
    }

    func refresh() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let sources = FeedSource.allCases.filter { enabledSources.contains($0) }
        let fetched = await FeedService.fetchAll(sources: sources)
        if fetched.isEmpty && articles.isEmpty {
            errorMessage = "Feeds returned nothing (some sources block automated clients). Try again shortly."
            executiveSummary = "Waiting on live feeds. The Record and Google News usually come through first; Lawfare may be Cloudflare-gated."
            summaryModel = nil
            summaryProvider = nil
            return
        }
        if !fetched.isEmpty {
            articles = fetched
        }
        lastRefreshed = Date()
        let summary = await SummaryService.summarize(articles: articles)
        executiveSummary = summary.text
        summaryModel = summary.model
        summaryProvider = summary.provider
        await generateBeats(for: Array(articles.prefix(8)))
        persist()
    }

    func generateBeats(for items: [Article]) async {
        for article in items {
            if articleBeats[article.id] != nil { continue }
            let beat = await SummaryService.articleBeat(for: article)
            articleBeats[article.id] = beat
        }
    }

    func summarizeArticle(_ article: Article) async -> SummaryResult {
        if let cached = articleSummaries[article.id] {
            return cached
        }
        let result = await SummaryService.articleSummary(for: article)
        articleSummaries[article.id] = result
        return result
    }

    func clarifyArticle(_ article: Article, question: String) async -> SummaryResult {
        let summaryText = articleSummaries[article.id]?.text ?? ""
        return await SummaryService.articleClarify(
            article: article,
            question: question,
            summaryText: summaryText
        )
    }

    func openOriginal(_ article: Article) {
        NSWorkspace.shared.open(article.url)
    }

    private func persist() {
        let snap = BriefingSnapshot(
            generatedAt: lastRefreshed ?? Date(),
            executiveSummary: executiveSummary,
            summaryModel: summaryModel,
            summaryProvider: summaryProvider,
            articles: articles,
            highlightsByActor: Dictionary(
                uniqueKeysWithValues: countsByActor.map {
                    ($0.0.rawValue, $0.1 > 0 ? ["\($0.1) items"] : [])
                }
            )
        )
        do {
            let data = try JSONEncoder().encode(snap)
            try data.write(to: cacheURL, options: .atomic)
        } catch {
            // non-fatal
        }
    }

    private func loadCache() {
        guard let data = try? Data(contentsOf: cacheURL),
              let snap = try? JSONDecoder().decode(BriefingSnapshot.self, from: data)
        else { return }
        articles = snap.articles
        executiveSummary = snap.executiveSummary
        summaryModel = snap.summaryModel
        summaryProvider = snap.summaryProvider
        lastRefreshed = snap.generatedAt
    }
}
