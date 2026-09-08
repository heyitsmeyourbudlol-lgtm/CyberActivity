import Foundation
import NaturalLanguage

/// Local Ollama chat API — mirrors electron/summary.js.
enum SummaryService {
    /// Summaries / beats / article high-level reads
    static let summaryModel = ProcessInfo.processInfo.environment["CYBERACTIVITY_MODEL"]
        ?? "QyrouNnet/summarizer:400m"
    /// Ask / clarification path
    static let cyberModel = ProcessInfo.processInfo.environment["CYBERACTIVITY_CYBER_MODEL"]
        ?? "DeepHat/DeepHat-V1-7B"

    private static let ollamaBase = ProcessInfo.processInfo.environment["OLLAMA_HOST"]
        ?? "http://127.0.0.1:11434"

    private static let session: URLSession = {
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 120
        return URLSession(configuration: config)
    }()

    // MARK: - Public API

    static func summarize(articles: [Article]) async -> SummaryResult {
        let focused = articles.filter { article in
            article.actors.contains { $0 != .general } || isPriority(article)
        }
        let corpus = Array((focused.isEmpty ? articles : focused).prefix(18))
        guard !corpus.isEmpty else {
            return SummaryResult(
                text: "No fresh items matched the state-cyber watchlist. Refresh after feeds update.",
                model: nil,
                provider: "none"
            )
        }

        do {
            let bullets = briefBullets(corpus)
            let text = try await ollamaChat(
                messages: [
                    ChatMessage(
                        role: "system",
                        content: "You write short cyber threat briefs. Plain prose only. No markdown, no bullets, no headers, no recommendations section. Exactly 3 short paragraphs: (1) what moved, (2) actor implications, (3) what to watch. Cite source brands like The Record or Lawfare inline. Stay concrete."
                    ),
                    ChatMessage(
                        role: "user",
                        content: "Write today's executive brief from this watchlist:\n\(bullets)"
                    )
                ],
                model: summaryModel,
                temperature: 0.2
            )
            return SummaryResult(text: text, model: summaryModel, provider: "ollama")
        } catch {
            return extractiveSummary(articles: corpus)
        }
    }

    static func articleBeat(for article: Article) async -> String {
        do {
            return try await ollamaChat(
                messages: [
                    ChatMessage(
                        role: "system",
                        content: "Distill cyber threat journalism into one crisp beat line. Max 28 words. No preamble."
                    ),
                    ChatMessage(
                        role: "user",
                        content: "Title: \(article.title)\nSource: \(article.source.rawValue)\nLede: \(article.posterLede)"
                    )
                ],
                model: summaryModel,
                temperature: 0.2
            )
        } catch {
            return shorten(article.posterLede, limit: 160)
        }
    }

    static func articleSummary(for article: Article) async -> SummaryResult {
        do {
            let actors = article.actors.map(\.rawValue).joined(separator: ", ")
            let text = try await ollamaChat(
                messages: [
                    ChatMessage(
                        role: "system",
                        content: "You write high-level article summaries for a cyber threat desk. Plain prose only. No markdown, no bullets, no headers. Exactly 2 short paragraphs: (1) what the piece says happened, (2) why it matters for state cyber / adversarial AI / digital sovereignty watchers. Cite the source brand once. Stay faithful to the provided lede—do not invent facts."
                    ),
                    ChatMessage(
                        role: "user",
                        content: """
                        Summarize this article at a high level.
                        Title: \(article.title)
                        Source: \(article.source.rawValue)
                        Published: \(article.publishedAt.formatted())
                        Actors: \(actors)
                        Lede: \(article.summary.isEmpty ? article.title : article.summary)
                        """
                    )
                ],
                model: summaryModel,
                temperature: 0.2
            )
            return SummaryResult(text: text, model: summaryModel, provider: "ollama")
        } catch {
            let lede = article.summary.isEmpty ? article.title : article.summary
            return SummaryResult(
                text: "\(lede)\n\nHigh-level read from \(article.source.rawValue). Open the original for full detail; local summarizer was unavailable.",
                model: nil,
                provider: "extractive"
            )
        }
    }

    static func articleClarify(
        article: Article,
        question: String,
        summaryText: String
    ) async -> SummaryResult {
        let q = question.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !q.isEmpty else {
            return SummaryResult(
                text: "Ask a short clarification question about this article.",
                model: nil,
                provider: "none"
            )
        }

        do {
            let actors = article.actors.map(\.rawValue).joined(separator: ", ")
            let text = try await ollamaChat(
                messages: [
                    ChatMessage(
                        role: "system",
                        content: "You are a cyber threat intelligence analyst for a state-sponsored cyber briefing desk covering Russia, China, North Korea, adversarial AI, and digital sovereignty. Answer the user's clarification question using the article context. Plain prose preferred; short bullets only if essential. Be concrete about actors, TTPs, and implications. Do not invent facts not supported by the context; say when something is uncertain or outside the provided material. Keep answers under ~180 words unless the question needs more."
                    ),
                    ChatMessage(
                        role: "user",
                        content: """
                        Title: \(article.title)
                        Source: \(article.source.rawValue)
                        Published: \(article.publishedAt.formatted())
                        Actors: \(actors.isEmpty ? "unspecified" : actors)
                        Lede: \(article.summary.isEmpty ? article.title : article.summary)
                        High-level summary: \(summaryText.isEmpty ? "(not yet generated)" : summaryText)

                        Clarification question: \(q)
                        """
                    )
                ],
                model: cyberModel,
                temperature: 0.25
            )
            return SummaryResult(text: text, model: cyberModel, provider: "ollama")
        } catch {
            return SummaryResult(
                text: error.localizedDescription.isEmpty
                    ? "Cyber clarification model unavailable. Ensure Ollama is running with \(cyberModel)."
                    : error.localizedDescription,
                model: nil,
                provider: "error"
            )
        }
    }

    // MARK: - Ollama

    private struct ChatMessage: Encodable {
        let role: String
        let content: String
    }

    private struct ChatRequest: Encodable {
        let model: String
        let messages: [ChatMessage]
        let stream: Bool
        let options: Options

        struct Options: Encodable {
            let temperature: Double
        }
    }

    private struct ChatResponse: Decodable {
        struct Message: Decodable {
            let content: String?
        }
        let message: Message?
    }

    private static func ollamaChat(
        messages: [ChatMessage],
        model: String,
        temperature: Double
    ) async throws -> String {
        guard let url = URL(string: "\(ollamaBase)/api/chat") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(
            ChatRequest(
                model: model,
                messages: messages,
                stream: false,
                options: .init(temperature: temperature)
            )
        )

        let (data, response) = try await session.data(for: request)
        if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
            let errText = String(data: data, encoding: .utf8) ?? ""
            throw NSError(
                domain: "Ollama",
                code: http.statusCode,
                userInfo: [NSLocalizedDescriptionKey: "Ollama \(http.statusCode): \(String(errText.prefix(200)))"]
            )
        }
        let decoded = try JSONDecoder().decode(ChatResponse.self, from: data)
        let text = decoded.message?.content?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if text.isEmpty {
            throw NSError(
                domain: "Ollama",
                code: -1,
                userInfo: [NSLocalizedDescriptionKey: "Empty Ollama response"]
            )
        }
        return text
    }

    // MARK: - Fallback

    private static func extractiveSummary(articles: [Article]) -> SummaryResult {
        let byActor = Dictionary(grouping: articles) { $0.primaryActor }
        var parts: [String] = []

        let movers = ThreatActor.allCases.compactMap { actor -> String? in
            guard actor != .general, let items = byActor[actor], !items.isEmpty else { return nil }
            let sample = items.prefix(2).map(\.title).joined(separator: "; ")
            return "\(actor.rawValue): \(sample)"
        }

        if movers.isEmpty {
            parts.append(
                "Landscape pulse: \(articles.prefix(3).map(\.title).joined(separator: " · "))."
            )
        } else {
            parts.append("What moved: " + movers.joined(separator: " | "))
        }

        let top = articles.prefix(4)
        let keywords = keywordSketch(from: top.map { $0.title + " " + $0.posterLede }.joined(separator: " "))
        if !keywords.isEmpty {
            parts.append("Signal cluster: \(keywords.joined(separator: ", ")).")
        }

        let sources = Set(articles.prefix(10).map(\.source.rawValue)).sorted().joined(separator: ", ")
        parts.append(
            "Drawn from \(articles.count) items across \(sources). Start Ollama (model \(summaryModel)) to restore the AI brief."
        )
        return SummaryResult(text: parts.joined(separator: "\n\n"), model: nil, provider: "extractive")
    }

    private static func briefBullets(_ articles: [Article]) -> String {
        articles.prefix(12).map { article in
            "- [\(article.source.brandMark)] \(article.title) — \(shorten(article.posterLede, limit: 140)) · \(article.actors.map(\.shortLabel).joined(separator: "/"))"
        }.joined(separator: "\n")
    }

    private static func isPriority(_ article: Article) -> Bool {
        let blob = (article.title + " " + article.summary).lowercased()
        return ["russia", "china", "north korea", "dprk", "lazarus", "apt", "sovereignty", "adversarial"]
            .contains(where: blob.contains)
    }

    private static func shorten(_ text: String, limit: Int) -> String {
        guard text.count > limit else { return text }
        let idx = text.index(text.startIndex, offsetBy: limit)
        return String(text[..<idx]).trimmingCharacters(in: .whitespaces) + "…"
    }

    private static func keywordSketch(from text: String) -> [String] {
        let tagger = NLTagger(tagSchemes: [.nameType, .lexicalClass])
        tagger.string = text
        var scores: [String: Int] = [:]
        let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace, .omitOther]
        tagger.enumerateTags(
            in: text.startIndex..<text.endIndex,
            unit: .word,
            scheme: .lexicalClass,
            options: options
        ) { tag, range in
            guard let tag, tag == .noun || tag == .verb else { return true }
            let word = String(text[range]).lowercased()
            guard word.count > 3 else { return true }
            scores[word, default: 0] += 1
            return true
        }
        return scores.sorted { $0.value > $1.value }.prefix(6).map(\.key)
    }
}
