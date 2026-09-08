import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        ZStack {
            background
            HStack(spacing: 0) {
                SidebarView()
                    .frame(width: 220)
                Rectangle()
                    .fill(CATheme.ink.opacity(0.08))
                    .frame(width: 1)
                mainPane
            }
        }
        .sheet(item: $store.selectedArticle) { article in
            ArticleDetailSheet(article: article)
                .environmentObject(store)
        }
        .task {
            if store.articles.isEmpty {
                await store.refresh()
            } else if store.executiveSummary.contains("Pulling") {
                await store.refresh()
            }
        }
    }

    private var background: some View {
        LinearGradient(
            colors: [CATheme.bg0, CATheme.bg1, CATheme.bg2],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .ignoresSafeArea()
        .overlay {
            GeometryReader { geo in
                Circle()
                    .fill(CATheme.teal.opacity(0.12))
                    .frame(width: 420, height: 420)
                    .blur(radius: 48)
                    .offset(x: geo.size.width * 0.55, y: -80)
                Circle()
                    .fill(CATheme.signal.opacity(0.08))
                    .frame(width: 320, height: 320)
                    .blur(radius: 50)
                    .offset(x: -60, y: geo.size.height * 0.55)
            }
        }
    }

    private var mainPane: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            ScrollView {
                VStack(alignment: .leading, spacing: 28) {
                    SummaryHeroView(
                        text: store.executiveSummary,
                        refreshed: store.lastRefreshed,
                        modelLine: summaryModelLine
                    )
                    posterStrip
                    ActorBoardView()
                }
                .padding(.horizontal, 28)
                .padding(.bottom, 40)
            }
        }
    }

    private var summaryModelLine: String {
        if let model = store.summaryModel {
            let via = store.summaryProvider == "ollama" ? "local" : (store.summaryProvider ?? "model")
            return "\(model) · \(via)"
        }
        if store.summaryProvider == "extractive" {
            return "extractive fallback"
        }
        return ""
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 6) {
                Text("CyberActivity")
                    .font(CATheme.display)
                    .foregroundStyle(CATheme.ink)
                    .tracking(-0.4)
                Text("State-sponsored cyber · adversarial AI · digital sovereignty")
                    .font(CATheme.mono(12))
                    .foregroundStyle(CATheme.slate.opacity(0.75))
            }
            Spacer()
            Button {
                Task { await store.refresh() }
            } label: {
                Text(store.isLoading ? "Refreshing" : "Refresh")
                    .font(CATheme.sans(14, weight: .medium))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(CATheme.ink)
                    .foregroundStyle(CATheme.paper)
                    .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                    .opacity(store.isLoading ? 0.55 : 1)
            }
            .buttonStyle(.plain)
            .disabled(store.isLoading)
            .padding(.trailing, 28)
            .padding(.top, 8)
        }
        .padding(.leading, 28)
        .padding(.top, 18)
        .padding(.bottom, 22)
    }

    private var posterStrip: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .firstTextBaseline) {
                Text("Article posters")
                    .font(CATheme.title)
                    .foregroundStyle(CATheme.ink)
                Spacer()
                Text("Click a poster for a high-level summary")
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.slate.opacity(0.65))
            }

            if let error = store.errorMessage {
                Text(error)
                    .font(CATheme.sans(13))
                    .foregroundStyle(CATheme.signal)
            }

            if store.filteredArticles.isEmpty, !store.isLoading {
                Text("No articles yet. Hit Refresh.")
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.slate.opacity(0.5))
            }

            LazyVGrid(
                columns: [GridItem(.adaptive(minimum: 300, maximum: 400), spacing: 18)],
                spacing: 18
            ) {
                ForEach(Array(store.filteredArticles.prefix(24).enumerated()), id: \.element.id) { index, article in
                    ArticlePosterView(
                        article: article,
                        beat: store.articleBeats[article.id],
                        appearDelay: Double(index) * 0.03,
                        onSelect: { store.selectedArticle = article },
                        onOpenOriginal: { store.openOriginal(article) }
                    )
                }
            }
        }
    }
}

struct SidebarView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Color.clear.frame(height: 42)

            Text("Watch")
                .font(CATheme.mono(11))
                .tracking(0.9)
                .textCase(.uppercase)
                .foregroundStyle(CATheme.slate.opacity(0.55))
                .padding(.horizontal, 20)
                .padding(.bottom, 10)

            VStack(spacing: 4) {
                actorButton(nil, label: "All activity", count: store.articles.count)

                ForEach(ThreatActor.allCases.filter { $0 != .general }) { actor in
                    let count = store.articles.filter { $0.actors.contains(actor) }.count
                    actorButton(actor, label: actor.rawValue, count: count)
                }
            }
            .padding(.horizontal, 10)

            Spacer()

            Text("Sources")
                .font(CATheme.mono(11))
                .tracking(0.9)
                .textCase(.uppercase)
                .foregroundStyle(CATheme.slate.opacity(0.55))
                .padding(.horizontal, 20)
                .padding(.bottom, 8)
                .padding(.top, 8)

            VStack(alignment: .leading, spacing: 8) {
                ForEach(FeedSource.allCases) { source in
                    Toggle(isOn: Binding(
                        get: { store.enabledSources.contains(source) },
                        set: { on in
                            if on { store.enabledSources.insert(source) }
                            else { store.enabledSources.remove(source) }
                        }
                    )) {
                        Text(source.rawValue)
                            .font(CATheme.sans(12))
                            .foregroundStyle(CATheme.slate)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .toggleStyle(.checkbox)
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 18)
        }
        .background(CATheme.paper.opacity(0.55))
    }

    private func actorButton(_ actor: ThreatActor?, label: String, count: Int) -> some View {
        let selected = store.selectedActor == actor
        return Button {
            store.selectedActor = actor
        } label: {
            HStack(spacing: 10) {
                Circle()
                    .fill(actor?.accent ?? CATheme.ink)
                    .frame(width: 8, height: 8)
                Text(label)
                    .font(CATheme.sans(14, weight: selected ? .semibold : .medium))
                    .lineLimit(1)
                Spacer(minLength: 4)
                Text("\(count)")
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.slate.opacity(0.7))
            }
            .foregroundStyle(CATheme.ink)
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(selected ? CATheme.mist : Color.clear)
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

struct SummaryHeroView: View {
    let text: String
    let refreshed: Date?
    var modelLine: String = ""

    @State private var appeared = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text("AI briefing")
                    .font(CATheme.title)
                    .foregroundStyle(CATheme.ink)
                Spacer()
                VStack(alignment: .trailing, spacing: 4) {
                    if !modelLine.isEmpty {
                        Text(modelLine)
                            .font(CATheme.mono(11))
                            .foregroundStyle(CATheme.slate.opacity(0.65))
                    }
                    if let refreshed {
                        Text(refreshed.formatted(date: .abbreviated, time: .shortened))
                            .font(CATheme.mono(11))
                            .foregroundStyle(CATheme.slate.opacity(0.65))
                    }
                }
            }
            Text(text)
                .font(CATheme.serif(20, weight: .medium))
                .foregroundStyle(CATheme.ink.opacity(0.92))
                .lineSpacing(6)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(24)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(CATheme.paper.opacity(0.92))
                .shadow(color: CATheme.ink.opacity(0.06), radius: 16, y: 10)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .strokeBorder(CATheme.ink.opacity(0.06), lineWidth: 1)
        )
        .opacity(appeared ? 1 : 0)
        .offset(y: appeared ? 0 : 10)
        .onAppear {
            withAnimation(.easeOut(duration: 0.48)) {
                appeared = true
            }
        }
    }
}

struct ActorBoardView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Actor board")
                .font(CATheme.title)
                .foregroundStyle(CATheme.ink)

            HStack(alignment: .top, spacing: 12) {
                ForEach(ThreatActor.allCases.filter { $0 != .general }) { actor in
                    let items = store.articles.filter { $0.actors.contains(actor) }
                    VStack(alignment: .leading, spacing: 0) {
                        HStack {
                            Text(actor.shortLabel)
                                .font(CATheme.mono(11))
                                .foregroundStyle(actor.accent)
                            Spacer()
                            Text("\(items.count)")
                                .font(CATheme.mono(11))
                                .foregroundStyle(CATheme.slate.opacity(0.65))
                        }
                        Text(actor.rawValue)
                            .font(CATheme.serif(18, weight: .semibold))
                            .foregroundStyle(CATheme.ink)
                            .padding(.top, 8)
                            .padding(.bottom, 10)

                        if items.isEmpty {
                            Text("Quiet this cycle")
                                .font(CATheme.mono(11))
                                .foregroundStyle(CATheme.slate.opacity(0.5))
                        } else {
                            VStack(alignment: .leading, spacing: 6) {
                                ForEach(items.prefix(3)) { article in
                                    Text(article.title)
                                        .font(CATheme.sans(12))
                                        .foregroundStyle(CATheme.slate)
                                        .lineLimit(2)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                        }
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, minHeight: 150, alignment: .topLeading)
                    .background(CATheme.paper.opacity(0.75))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .strokeBorder(actor.accent.opacity(0.35), lineWidth: 1.5)
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                }
            }
        }
        .padding(.top, 4)
    }
}

struct SettingsView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        Form {
            Section("About") {
                Text("CyberActivity consolidates Lawfare, The Record, Krebs, and state-cyber coverage into one Mac briefing.")
                Text("Summaries use local Ollama (\(SummaryService.summaryModel)). Clarifications use \(SummaryService.cyberModel).")
                    .foregroundStyle(.secondary)
            }
            Section("Ollama") {
                Text("Endpoint: \(ProcessInfo.processInfo.environment["OLLAMA_HOST"] ?? "http://127.0.0.1:11434")")
                    .font(.system(.caption, design: .monospaced))
                Text("Pull models with: ollama pull \(SummaryService.summaryModel)")
                    .font(.system(.caption, design: .monospaced))
                Text("and: ollama pull \(SummaryService.cyberModel)")
                    .font(.system(.caption, design: .monospaced))
            }
            Section("Cache") {
                Text("\(store.articles.count) articles cached")
                if let last = store.lastRefreshed {
                    Text("Last refresh \(last.formatted())")
                }
            }
        }
        .padding()
    }
}
