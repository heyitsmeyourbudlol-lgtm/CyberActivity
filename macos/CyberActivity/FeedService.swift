import Foundation

enum FeedService {
    private static let session: URLSession = {
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 25
        config.httpAdditionalHeaders = [
            "User-Agent": "CyberActivity/1.0 (Macintosh; Intel Mac OS X) AppleSyndication/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        ]
        return URLSession(configuration: config)
    }()

    static func fetchAll(sources: [FeedSource] = FeedSource.allCases) async -> [Article] {
        await withTaskGroup(of: [Article].self) { group in
            for source in sources {
                group.addTask {
                    (try? await fetch(source: source)) ?? []
                }
            }
            var merged: [Article] = []
            for await batch in group {
                merged.append(contentsOf: batch)
            }
            return dedupe(merged).sorted { $0.publishedAt > $1.publishedAt }
        }
    }

    static func fetch(source: FeedSource) async throws -> [Article] {
        let (data, response) = try await session.data(from: source.feedURL)
        if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
            throw URLError(.badServerResponse)
        }
        let text = String(data: data, encoding: .utf8) ?? ""
        if text.contains("Attention Required") || text.contains("cf-error-details") {
            return []
        }
        return RSSParser.parse(data: data, source: source)
    }

    private static func dedupe(_ articles: [Article]) -> [Article] {
        var seen = Set<String>()
        var out: [Article] = []
        for article in articles {
            let key = article.title.lowercased()
                .replacingOccurrences(of: #"\s+"#, with: " ", options: .regularExpression)
            if seen.insert(key).inserted {
                out.append(article)
            }
        }
        return out
    }
}

enum RSSParser {
    static func parse(data: Data, source: FeedSource) -> [Article] {
        let parser = XMLFeedParser(source: source)
        let xml = XMLParser(data: data)
        xml.delegate = parser
        xml.parse()
        return parser.articles
    }
}

private final class XMLFeedParser: NSObject, XMLParserDelegate {
    let source: FeedSource
    private(set) var articles: [Article] = []

    private var inItem = false
    private var currentElement = ""
    private var title = ""
    private var link = ""
    private var summary = ""
    private var pubDate = ""
    private var guid = ""
    private var categories: [String] = []
    private var enclosureURL: String?
    private var buffer = ""

    init(source: FeedSource) {
        self.source = source
    }

    func parser(
        _ parser: XMLParser,
        didStartElement elementName: String,
        namespaceURI: String?,
        qualifiedName qName: String?,
        attributes attributeDict: [String: String] = [:]
    ) {
        currentElement = elementName.lowercased()
        buffer = ""
        if currentElement == "item" || currentElement == "entry" {
            inItem = true
            title = ""; link = ""; summary = ""; pubDate = ""; guid = ""
            categories = []; enclosureURL = nil
        }
        if inItem, currentElement == "enclosure" || currentElement == "media:content" {
            enclosureURL = attributeDict["url"]
        }
        if inItem, currentElement == "link", let href = attributeDict["href"], link.isEmpty {
            link = href
        }
    }

    func parser(_ parser: XMLParser, foundCharacters string: String) {
        guard inItem else { return }
        buffer += string
    }

    func parser(
        _ parser: XMLParser,
        didEndElement elementName: String,
        namespaceURI: String?,
        qualifiedName qName: String?
    ) {
        let name = elementName.lowercased()
        let value = buffer.trimmingCharacters(in: .whitespacesAndNewlines)

        if inItem {
            switch name {
            case "title":
                title = value
            case "link" where link.isEmpty:
                link = value
            case "description", "summary", "content:encoded", "content":
                if summary.isEmpty || value.count > summary.count { summary = value }
            case "pubdate", "published", "updated", "dc:date":
                pubDate = value
            case "guid", "id":
                guid = value
            case "category":
                if !value.isEmpty { categories.append(value) }
            case "source":
                if !value.isEmpty { categories.append(value) }
            default:
                break
            }
        }

        if name == "item" || name == "entry" {
            inItem = false
            commitItem()
        }
        buffer = ""
    }

    private func commitItem() {
        guard !title.isEmpty, let url = URL(string: link), !link.isEmpty else { return }
        let id = guid.isEmpty ? url.absoluteString : guid
        let date = parseDate(pubDate) ?? Date()
        let actors = ActorClassifier.classify(title: title, summary: summary, categories: categories)
        let mappedSource = remapSource(title: title, url: url)
        articles.append(
            Article(
                id: id,
                title: cleanHTML(title),
                summary: cleanHTML(summary),
                url: url,
                publishedAt: date,
                source: mappedSource,
                actors: actors,
                imageURL: enclosureURL.flatMap(URL.init(string:)),
                categories: categories
            )
        )
    }

    private func remapSource(title: String, url: URL) -> FeedSource {
        let host = url.host?.lowercased() ?? ""
        let blob = (title + " " + host).lowercased()
        if blob.contains("lawfare") { return .lawfare }
        if host.contains("therecord.media") { return .theRecord }
        if host.contains("krebsonsecurity") { return .krebs }
        return source
    }

    private func cleanHTML(_ raw: String) -> String {
        raw
            .replacingOccurrences(of: "<[^>]+>", with: " ", options: .regularExpression)
            .replacingOccurrences(of: "&nbsp;", with: " ")
            .replacingOccurrences(of: "&amp;", with: "&")
            .replacingOccurrences(of: "&lt;", with: "<")
            .replacingOccurrences(of: "&gt;", with: ">")
            .replacingOccurrences(of: "&quot;", with: "\"")
            .replacingOccurrences(of: "&#39;", with: "'")
            .replacingOccurrences(of: #"\s+"#, with: " ", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func parseDate(_ raw: String) -> Date? {
        guard !raw.isEmpty else { return nil }
        let formats = [
            "EEE, dd MMM yyyy HH:mm:ss Z",
            "EEE, dd MMM yyyy HH:mm:ss zzz",
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
            "yyyy-MM-dd'T'HH:mm:ssxxx"
        ]
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        for format in formats {
            formatter.dateFormat = format
            if let date = formatter.date(from: raw) { return date }
        }
        return ISO8601DateFormatter().date(from: raw)
    }
}

enum ActorClassifier {
    static func classify(title: String, summary: String, categories: [String]) -> [ThreatActor] {
        let blob = ([title, summary] + categories).joined(separator: " ").lowercased()
        var hits: [ThreatActor] = []

        let russia = ["russia", "russian", "moscow", "kremlin", "apt28", "apt29", "fancy bear", "cozy bear", "sandworm", "gru", "fsb"]
        let china = ["china", "chinese", "beijing", "pla", "mss", "apt41", "apt10", "volt typhoon", "salt typhoon", "hafnium"]
        let nk = ["north korea", "dprk", "pyongyang", "lazarus", "andariel", "kimsuky"]
        let ai = ["adversarial ai", "ai-enabled", "generative ai", "llm", "machine learning attack", "deepfake", "model theft"]
        let sov = ["digital sovereignty", "data localization", "splinternet", "cyber sovereignty", "tech decoupling"]

        if russia.contains(where: blob.contains) { hits.append(.russia) }
        if china.contains(where: blob.contains) { hits.append(.china) }
        if nk.contains(where: blob.contains) { hits.append(.northKorea) }
        if ai.contains(where: blob.contains) { hits.append(.adversarialAI) }
        if sov.contains(where: blob.contains) { hits.append(.digitalSovereignty) }

        let cyberSignals = ["cyber", "apt", "espionage", "malware", "ransomware", "intrusion", "hack", "breach", "nation-state", "state-sponsored"]
        if hits.isEmpty, cyberSignals.contains(where: blob.contains) {
            hits.append(.general)
        }
        if hits.isEmpty { hits.append(.general) }
        return hits
    }
}
