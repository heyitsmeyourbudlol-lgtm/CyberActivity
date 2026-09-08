import SwiftUI

/// Article modal — mirrors Electron `#article-modal` (summary + Ask / DeepHat).
struct ArticleDetailSheet: View {
    @EnvironmentObject private var store: BriefingStore
    @Environment(\.dismiss) private var dismiss

    let article: Article

    @State private var summaryText = "Generating…"
    @State private var summaryMeta = "\(SummaryService.summaryModel) · local"
    @State private var clarifyQuestion = ""
    @State private var clarifyAnswer = ""
    @State private var clarifyMeta = ""
    @State private var isAsking = false
    @State private var isLoadingSummary = true
    @State private var appeared = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    header
                    Text(article.title)
                        .font(CATheme.serif(28, weight: .semibold))
                        .foregroundStyle(CATheme.ink)
                        .lineSpacing(3)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.bottom, 12)

                    tags
                        .padding(.bottom, 6)

                    Text("High-level summary")
                        .font(CATheme.mono(11))
                        .tracking(0.7)
                        .textCase(.uppercase)
                        .foregroundStyle(CATheme.slate.opacity(0.65))
                        .padding(.top, 18)
                        .padding(.bottom, 8)

                    Text(summaryText)
                        .font(CATheme.serif(18, weight: .medium))
                        .foregroundStyle(CATheme.ink.opacity(0.92))
                        .lineSpacing(5)
                        .fixedSize(horizontal: false, vertical: true)

                    Text(summaryMeta)
                        .font(CATheme.mono(11))
                        .foregroundStyle(CATheme.slate.opacity(0.55))
                        .padding(.top, 8)

                    clarifyBlock
                        .padding(.top, 18)

                    HStack {
                        Spacer()
                        Button {
                            store.openOriginal(article)
                        } label: {
                            Text("Open original →")
                                .font(CATheme.sans(14, weight: .medium))
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(CATheme.ink)
                                .foregroundStyle(CATheme.paper)
                                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.top, 22)
                }
                .padding(.horizontal, 26)
                .padding(.top, 24)
                .padding(.bottom, 22)
            }
        }
        .frame(minWidth: 560, idealWidth: 640, maxWidth: 640, minHeight: 420, idealHeight: 620)
        .background(CATheme.paper)
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .strokeBorder(CATheme.ink.opacity(0.08), lineWidth: 1)
        )
        .shadow(color: CATheme.ink.opacity(0.22), radius: 28, y: 16)
        .opacity(appeared ? 1 : 0)
        .offset(y: appeared ? 0 : 10)
        .onAppear {
            withAnimation(.easeOut(duration: 0.28)) {
                appeared = true
            }
        }
        .task(id: article.id) {
            await loadSummary()
        }
    }

    private var header: some View {
        HStack(alignment: .top, spacing: 10) {
            ZStack {
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(article.primaryActor.accent)
                    .frame(width: 36, height: 36)
                Text(article.source.brandMark)
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.paper)
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(article.source.rawValue.uppercased())
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.ink)
                Text(article.publishedAt.formatted(date: .abbreviated, time: .shortened))
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.slate.opacity(0.65))
            }
            Spacer()
            Button {
                dismiss()
            } label: {
                Text("✕")
                    .font(CATheme.sans(14, weight: .medium))
                    .foregroundStyle(CATheme.slate)
                    .frame(width: 32, height: 32)
                    .background(CATheme.mist)
                    .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
            }
            .buttonStyle(.plain)
            .keyboardShortcut(.cancelAction)
        }
        .padding(.bottom, 14)
    }

    private var tags: some View {
        HStack(spacing: 6) {
            ForEach(article.actors.prefix(4), id: \.self) { actor in
                Text(actor.shortLabel)
                    .font(CATheme.mono(10))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(actor.accent.opacity(0.133))
                    .foregroundStyle(actor.accent)
                    .clipShape(RoundedRectangle(cornerRadius: 4, style: .continuous))
            }
        }
    }

    private var clarifyBlock: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Clarify with cyber model")
                .font(CATheme.mono(11))
                .tracking(0.7)
                .textCase(.uppercase)
                .foregroundStyle(CATheme.slate.opacity(0.65))

            HStack(spacing: 10) {
                TextField("e.g. How does this fit known APT TTPs?", text: $clarifyQuestion)
                    .textFieldStyle(.plain)
                    .font(CATheme.sans(14))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .background(CATheme.paper.opacity(0.9))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .strokeBorder(CATheme.ink.opacity(0.14), lineWidth: 1)
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                    .onSubmit { Task { await ask() } }

                Button {
                    Task { await ask() }
                } label: {
                    Text(isAsking ? "…" : "Ask")
                        .font(CATheme.sans(14, weight: .medium))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(CATheme.ink)
                        .foregroundStyle(CATheme.paper)
                        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                        .opacity(isAsking || isLoadingSummary ? 0.55 : 1)
                }
                .buttonStyle(.plain)
                .disabled(isAsking || isLoadingSummary)
            }

            if !clarifyAnswer.isEmpty {
                Text(clarifyAnswer)
                    .font(CATheme.serif(16, weight: .medium))
                    .foregroundStyle(CATheme.ink.opacity(0.9))
                    .lineSpacing(4)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.top, 4)
            }
            if !clarifyMeta.isEmpty {
                Text(clarifyMeta)
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.slate.opacity(0.55))
            }
        }
    }

    private func loadSummary() async {
        isLoadingSummary = true
        clarifyQuestion = ""
        clarifyAnswer = ""
        clarifyMeta = ""
        if let cached = store.articleSummaries[article.id] {
            summaryText = cached.text
            summaryMeta = metaLine(cached)
            isLoadingSummary = false
            return
        }
        summaryText = "Generating…"
        summaryMeta = "\(SummaryService.summaryModel) · local"
        let result = await store.summarizeArticle(article)
        summaryText = result.text
        summaryMeta = metaLine(result)
        isLoadingSummary = false
    }

    private func ask() async {
        let q = clarifyQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !q.isEmpty else {
            clarifyAnswer = "Type a short question first."
            clarifyMeta = ""
            return
        }
        isAsking = true
        clarifyAnswer = "Thinking with cyber model…"
        clarifyMeta = "\(SummaryService.cyberModel) · local"
        defer { isAsking = false }
        let result = await store.clarifyArticle(article, question: q)
        clarifyAnswer = result.text
        clarifyMeta = metaLine(result)
    }

    private func metaLine(_ result: SummaryResult) -> String {
        if let model = result.model {
            let via = result.provider == "ollama" ? "local" : result.provider
            return "\(model) · \(via)"
        }
        return result.provider
    }
}
