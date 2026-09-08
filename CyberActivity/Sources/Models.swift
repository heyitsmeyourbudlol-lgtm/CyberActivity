import Foundation
import SwiftUI

enum ThreatActor: String, CaseIterable, Identifiable, Codable, Hashable {
    case russia = "Russia"
    case china = "China"
    case northKorea = "North Korea"
    case adversarialAI = "Adversarial AI"
    case digitalSovereignty = "Digital Sovereignty"
    case general = "Landscape"

    var id: String { rawValue }

    var shortLabel: String {
        switch self {
        case .russia: "RU"
        case .china: "CN"
        case .northKorea: "NK"
        case .adversarialAI: "AI"
        case .digitalSovereignty: "SOV"
        case .general: "ALL"
        }
    }
}

enum FeedSource: String, CaseIterable, Identifiable, Codable, Hashable {
    case theRecord = "The Record"
    case lawfare = "Lawfare"
    case krebs = "Krebs on Security"
    case googleLawfare = "Lawfare via Google News"
    case googleStateCyber = "State cyber watch"

    var id: String { rawValue }

    var feedURL: URL {
        switch self {
        case .theRecord:
            URL(string: "https://therecord.media/feed")!
        case .lawfare:
            URL(string: "https://www.lawfaremedia.org/feed")!
        case .krebs:
            URL(string: "https://krebsonsecurity.com/feed/")!
        case .googleLawfare:
            URL(string: "https://news.google.com/rss/search?q=site:lawfaremedia.org+(cyber+OR+russia+OR+china+OR+%22north+korea%22+OR+AI+OR+sovereignty)&hl=en-US&gl=US&ceid=US:en")!
        case .googleStateCyber:
            URL(string: "https://news.google.com/rss/search?q=(Russia+OR+China+OR+%22North+Korea%22)+(cyber+OR+APT+OR+espionage)+OR+%22digital+sovereignty%22+OR+%22adversarial+AI%22&hl=en-US&gl=US&ceid=US:en")!
        }
    }

    var brandMark: String {
        switch self {
        case .theRecord: "TR"
        case .lawfare, .googleLawfare: "LF"
        case .krebs: "KS"
        case .googleStateCyber: "GN"
        }
    }
}

struct Article: Identifiable, Hashable, Codable {
    let id: String
    var title: String
    var summary: String
    var url: URL
    var publishedAt: Date
    var source: FeedSource
    var actors: [ThreatActor]
    var imageURL: URL?
    var categories: [String]

    var primaryActor: ThreatActor {
        actors.first(where: { $0 != .general }) ?? .general
    }

    var posterLede: String {
        let cleaned = summary
            .replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
            .replacingOccurrences(of: "&nbsp;", with: " ")
            .replacingOccurrences(of: "&amp;", with: "&")
            .replacingOccurrences(of: "&quot;", with: "\"")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if cleaned.isEmpty { return title }
        return cleaned
    }
}

struct BriefingSnapshot: Codable {
    var generatedAt: Date
    var executiveSummary: String
    var articles: [Article]
    var highlightsByActor: [String: [String]]
}
