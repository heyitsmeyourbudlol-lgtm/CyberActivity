import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        ZStack {
            background
            HStack(spacing: 0) {
                SidebarView()
                    .frame(width: 220)
                Divider().opacity(0.25)
                mainPane
            }
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
            colors: [
                Color(red: 0.94, green: 0.93, blue: 0.89),
                Color(red: 0.88, green: 0.91, blue: 0.90),
                Color(red: 0.91, green: 0.90, blue: 0.86)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .ignoresSafeArea()
        .overlay {
            GeometryReader { geo in
                Circle()
                    .fill(CATheme.teal.opacity(0.08))
                    .frame(width: 420, height: 420)
                    .blur(radius: 40)
                    .offset(x: geo.size.width * 0.55, y: -80)
                Circle()
                    .fill(CATheme.signal.opacity(0.06))
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
                    SummaryHeroView(text: store.executiveSummary, refreshed: store.lastRefreshed)
                    posterStrip
                    ActorBoardView()
                }
                .padding(28)
            }
        }
    }

    private var header: some View {
        HStack(alignment: .firstTextBaseline) {
            VStack(alignment: .leading, spacing: 4) {
                Text("CyberActivity")
                    .font(CATheme.display)
                    .foregroundStyle(CATheme.ink)
                Text("State-sponsored cyber · adversarial AI · digital sovereignty")
                    .font(CATheme.mono)
                    .foregroundStyle(CATheme.slate.opacity(0.8))
            }
            Spacer()
            Button {
                Task { await store.refresh() }
            } label: {
                HStack(spacing: 8) {
                    if store.isLoading {
                        ProgressView().controlSize(.small)
                    } else {
                        Image(systemName: "arrow.clockwise")
                    }
                    Text(store.isLoading ? "Refreshing" : "Refresh")
                }
                .font(.system(.body, design: .default).weight(.medium))
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(CATheme.ink)
                .foregroundStyle(CATheme.paper)
                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
            }
            .buttonStyle(.plain)
            .disabled(store.isLoading)
            .padding(.trailing, 28)
        }
        .padding(.leading, 28)
        .padding(.top, 22)
        .padding(.bottom, 12)
    }

    private var posterStrip: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Article posters")
                    .font(CATheme.title)
                    .foregroundStyle(CATheme.ink)
                Spacer()
                Text("1:1 visual read of each piece")
                    .font(CATheme.mono)
                    .foregroundStyle(CATheme.slate.opacity(0.7))
            }

            if let error = store.errorMessage {
                Text(error)
                    .font(CATheme.body)
                    .foregroundStyle(CATheme.signal)
            }

            LazyVGrid(
                columns: [GridItem(.adaptive(minimum: 300, maximum: 380), spacing: 18)],
                spacing: 18
            ) {
                ForEach(store.filteredArticles.prefix(24)) { article in
                    ArticlePosterView(
                        article: article,
                        beat: store.articleBeats[article.id]
                    )
                    .onTapGesture {
                        store.selectedArticle = article
                        NSWorkspace.shared.open(article.url)
                    }
                }
            }
        }
    }
}

struct SidebarView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("WATCH")
                .font(CATheme.mono)
                .foregroundStyle(CATheme.slate.opacity(0.6))
                .padding(.top, 28)
                .padding(.horizontal, 20)

            actorButton(nil, label: "All activity", count: store.articles.count)

            ForEach(ThreatActor.allCases.filter { $0 != .general }) { actor in
                let count = store.articles.filter { $0.actors.contains(actor) }.count
                actorButton(actor, label: actor.rawValue, count: count)
            }

            Spacer()

            VStack(alignment: .leading, spacing: 6) {
                Text("SOURCES")
                    .font(CATheme.mono)
                    .foregroundStyle(CATheme.slate.opacity(0.55))
                ForEach(FeedSource.allCases) { source in
                    Toggle(source.rawValue, isOn: Binding(
                        get: { store.enabledSources.contains(source) },
                        set: { on in
                            if on { store.enabledSources.insert(source) }
                            else { store.enabledSources.remove(source) }
                        }
                    ))
                    .toggleStyle(.checkbox)
                    .font(.system(size: 12))
                    .foregroundStyle(CATheme.slate)
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 24)
        }
        .background(CATheme.paper.opacity(0.55))
    }

    private func actorButton(_ actor: ThreatActor?, label: String, count: Int) -> some View {
        let selected = store.selectedActor == actor
        return Button {
            store.selectedActor = actor
        } label: {
            HStack {
                Circle()
                    .fill(actor?.accent ?? CATheme.ink)
                    .frame(width: 8, height: 8)
                Text(label)
                    .font(.system(.body, design: .default).weight(selected ? .semibold : .regular))
                Spacer()
                Text("\(count)")
                    .font(CATheme.mono)
                    .foregroundStyle(CATheme.slate.opacity(0.7))
            }
            .foregroundStyle(CATheme.ink)
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(selected ? CATheme.mist : Color.clear)
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
        }
        .buttonStyle(.plain)
        .padding(.horizontal, 10)
    }
}

struct SummaryHeroView: View {
    let text: String
    let refreshed: Date?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .firstTextBaseline) {
                Text("AI briefing")
                    .font(CATheme.title)
                    .foregroundStyle(CATheme.ink)
                Spacer()
                if let refreshed {
                    Text(refreshed.formatted(date: .abbreviated, time: .shortened))
                        .font(CATheme.mono)
                        .foregroundStyle(CATheme.slate.opacity(0.65))
                }
            }
            Text(text)
                .font(.system(.title3, design: .serif))
                .foregroundStyle(CATheme.ink.opacity(0.92))
                .lineSpacing(5)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(24)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(CATheme.paper.opacity(0.9))
                .shadow(color: CATheme.ink.opacity(0.06), radius: 18, y: 8)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .strokeBorder(CATheme.ink.opacity(0.06), lineWidth: 1)
        )
    }
}

struct ActorBoardView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Actor board")
                .font(CATheme.title)
                .foregroundStyle(CATheme.ink)

            HStack(spacing: 12) {
                ForEach(ThreatActor.allCases.filter { $0 != .general }) { actor in
                    let items = store.articles.filter { $0.actors.contains(actor) }
                    VStack(alignment: .leading, spacing: 10) {
                        HStack {
                            Text(actor.shortLabel)
                                .font(CATheme.mono.weight(.bold))
                                .foregroundStyle(actor.accent)
                            Spacer()
                            Text("\(items.count)")
                                .font(CATheme.mono)
                        }
                        Text(actor.rawValue)
                            .font(.system(.headline, design: .serif))
                            .foregroundStyle(CATheme.ink)
                        ForEach(items.prefix(3)) { article in
                            Text(article.title)
                                .font(.system(size: 12))
                                .foregroundStyle(CATheme.slate)
                                .lineLimit(2)
                        }
                        if items.isEmpty {
                            Text("Quiet this cycle")
                                .font(CATheme.mono)
                                .foregroundStyle(CATheme.slate.opacity(0.5))
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
    }
}

struct SettingsView: View {
    @EnvironmentObject private var store: BriefingStore

    var body: some View {
        Form {
            Section("About") {
                Text("CyberActivity consolidates Lawfare, The Record, and related state-cyber coverage into one Mac briefing.")
                Text("Summaries use Apple Foundation Models when available, with an extractive fallback.")
                    .foregroundStyle(.secondary)
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
