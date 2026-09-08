import SwiftUI

/// Graphical poster mirroring Electron renderer cards:
/// masthead → hero band → body/tags → foot.
struct ArticlePosterView: View {
    let article: Article
    var beat: String?
    var appearDelay: Double = 0
    var onSelect: (() -> Void)?
    var onOpenOriginal: (() -> Void)?

    @State private var appeared = false
    @State private var hovering = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Button {
                onSelect?()
            } label: {
                VStack(alignment: .leading, spacing: 0) {
                    masthead
                    heroBand
                    bodyBlock
                }
            }
            .buttonStyle(.plain)
            footer
        }
        .frame(maxWidth: .infinity, minHeight: 360, alignment: .topLeading)
        .background(CATheme.paper)
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .shadow(
            color: CATheme.ink.opacity(hovering ? 0.14 : 0.10),
            radius: hovering ? 18 : 14,
            y: hovering ? 14 : 10
        )
        .offset(y: hovering ? -4 : 0)
        .scaleEffect(appeared ? 1 : 0.985)
        .opacity(appeared ? 1 : 0)
        .animation(.easeOut(duration: 0.22), value: hovering)
        .onHover { hovering = $0 }
        .onAppear {
            withAnimation(.easeOut(duration: 0.56).delay(appearDelay)) {
                appeared = true
            }
        }
        .help("Summarize \(article.source.rawValue) article")
        .contentShape(Rectangle())
    }

    private var masthead: some View {
        HStack(spacing: 10) {
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
                    .tracking(0.4)
                    .foregroundStyle(CATheme.paper.opacity(0.9))
                Text(categoryLine)
                    .font(CATheme.mono(9))
                    .foregroundStyle(CATheme.paper.opacity(0.55))
                    .lineLimit(1)
            }
            Spacer(minLength: 0)
        }
        .padding(14)
        .background(CATheme.ink.opacity(0.92))
    }

    private var categoryLine: String {
        let cats = article.categories.prefix(2).joined(separator: " · ").uppercased()
        return cats.isEmpty ? "CYBER WATCH" : cats
    }

    private var heroBand: some View {
        ZStack(alignment: .bottomLeading) {
            LinearGradient(
                colors: [
                    article.primaryActor.accent.opacity(0.95),
                    CATheme.ink.opacity(0.85)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            GeometryReader { geo in
                Path { path in
                    let w = geo.size.width
                    let h = geo.size.height
                    path.move(to: CGPoint(x: w * 0.62, y: 0))
                    path.addLine(to: CGPoint(x: w * 0.62, y: h))
                    path.move(to: CGPoint(x: 0, y: h * 0.38))
                    path.addLine(to: CGPoint(x: w, y: h * 0.38))
                }
                .stroke(CATheme.paper.opacity(0.12), lineWidth: 1)

                Text(article.primaryActor.shortLabel)
                    .font(CATheme.serif(64, weight: .semibold))
                    .foregroundStyle(CATheme.paper.opacity(0.10))
                    .offset(x: 16, y: 8)
            }

            Text(article.title)
                .font(CATheme.serif(20, weight: .semibold))
                .foregroundStyle(CATheme.paper)
                .lineSpacing(2)
                .lineLimit(4)
                .fixedSize(horizontal: false, vertical: true)
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(height: 168)
        .clipped()
    }

    private var bodyBlock: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(beat ?? article.posterLede)
                .font(CATheme.sans(13))
                .foregroundStyle(CATheme.ink.opacity(0.88))
                .lineSpacing(3)
                .lineLimit(5)
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: 6) {
                ForEach(article.actors.prefix(3), id: \.self) { actor in
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
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 96, alignment: .topLeading)
        .background(CATheme.paper)
    }

    private var footer: some View {
        HStack {
            Text(article.publishedAt.formatted(date: .abbreviated, time: .omitted))
                .font(CATheme.mono(11))
                .foregroundStyle(CATheme.slate.opacity(0.7))
            Spacer()
            Button {
                onOpenOriginal?()
            } label: {
                Text("Open original →")
                    .font(CATheme.mono(11))
                    .foregroundStyle(CATheme.teal)
                    .underline(true, color: CATheme.teal.opacity(0.7))
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(CATheme.mist.opacity(0.9))
    }
}
