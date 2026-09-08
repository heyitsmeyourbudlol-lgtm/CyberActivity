import Foundation
import FoundationModels
import NaturalLanguage

enum SummaryService {
    static func summarize(articles: [Article]) async -> String {
        let focused = articles.filter { article in
            article.actors.contains { $0 != .general } || isPriority(article)
        }
        let corpus = Array((focused.isEmpty ? articles : focused).prefix(18))
        guard !corpus.isEmpty else {
            return "No fresh items matched the state-cyber watchlist. Refresh after feeds update."
        }

        if #available(macOS 27.0, *) {
            if let ai = await appleIntelligenceSummary(articles: corpus) {
                return ai
            }
        }
        return extractiveSummary(articles: corpus)
    }

    static func articleBeat(for article: Article) async -> String {
        if #available(macOS 27.0, *) {
            let model = SystemLanguageModel.default
            if case .available = model.availability {
                do {
                    let session = LanguageModelSession(
                        instructions: """
                        You distill cyber threat journalism into one crisp beat line.
                        Keep the original actors, verbs, and stakes. Max 28 words. No preamble.
                        """
                    )
                    let prompt = """
                    Title: \(article.title)
                    Source: \(article.source.rawValue)
                    Lede: \(article.posterLede)
                    """
                    let response = try await session.respond(to: prompt)
                    let text = response.content.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !text.isEmpty { return text }
                } catch {
                    // fall through
                }
            }
        }
        return shorten(article.posterLede, limit: 160)
    }

    @available(macOS 27.0, *)
    private static func appleIntelligenceSummary(articles: [Article]) async -> String? {
        let model = SystemLanguageModel.default
        guard case .available = model.availability else { return nil }

        let bullets = articles.prefix(12).map { article in
            "- [\(article.source.brandMark)] \(article.title) — \(shorten(article.posterLede, limit: 140)) · actors: \(article.actors.map(\.shortLabel).joined(separator: "/"))"
        }.joined(separator: "\n")

        do {
            let session = LanguageModelSession(
                instructions: """
                You are CyberActivity's briefing officer for state-sponsored cyber activity.
                Focus on Russia, China, North Korea, adversarial AI trends, and digital sovereignty.
                Write 3 short paragraphs for a Mac briefing pane:
                1) What moved in the last cycle
                2) Actor / capability implications
                3) What to watch next
                Be concrete. Cite source brands inline (The Record, Lawfare, Krebs). No fluff, no markdown headings.
                """
            )
            let response = try await session.respond(
                to: "Synthesize this watchlist into today's executive brief:\n\(bullets)"
            )
            let text = response.content.trimmingCharacters(in: .whitespacesAndNewlines)
            return text.isEmpty ? nil : text
        } catch {
            return nil
        }
    }

    private static func extractiveSummary(articles: [Article]) -> String {
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
        parts.append("Drawn from \(articles.count) items across \(sources). On-device AI summary unavailable — showing extractive brief.")
        return parts.joined(separator: "\n\n")
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
        tagger.enumerateTags(in: text.startIndex..<text.endIndex, unit: .word, scheme: .lexicalClass, options: options) { tag, range in
            guard let tag, tag == .noun || tag == .verb else { return true }
            let word = String(text[range]).lowercased()
            guard word.count > 3 else { return true }
            scores[word, default: 0] += 1
            return true
        }
        return scores.sorted { $0.value > $1.value }.prefix(6).map(\.key)
    }
}
