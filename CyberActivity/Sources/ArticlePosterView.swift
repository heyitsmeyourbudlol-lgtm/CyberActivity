import SwiftUI

/// Graphical 1:1 poster that mirrors an article's story shape:
/// masthead (source) → headline → lede beat → actor strip → dateline.
struct ArticlePosterView: View {
    let article: Article
    var beat: String?

    @State private var appeared = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            masthead
            heroBand
            bodyBlock
            footer
        }
        .frame(maxWidth: .infinity, minHeight: 360, alignment: .topLeading)
        .background(posterBackground)
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .shadow(color: CATheme.ink.opacity(0.10), radius: 16, y: 10)
        .scaleEffect(appeared ? 1 : 0.96)
        .opacity(appeared ? 1 : 0)
        .onAppear {
            withAnimation(.spring(response: 0.55, dampingFraction: 0.82)) {
                appeared = true
            }
        }
        .help("Open \(article.source.rawValue) article")
    }

    private var masthead: some View {
        HStack(spacing: 10) {
            ZStack {
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(article.primaryActor.accent)
                    .frame(width: 36, height: 36)
                Text(article.source.brandMark)
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundStyle(CATheme.paper)
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(article.source.rawValue.uppercased())
                    .font(CATheme.mono.weight(.semibold))
                    .foregroundStyle(CATheme.paper.opacity(0.9))
                Text(article.categories.prefix(2).joined(separator: " · ").uppercased())
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundStyle(CATheme.paper.opacity(0.55))
                    .lineLimit(1)
            }
            Spacer()
        }
        .padding(14)
        .background(CATheme.ink.opacity(0.92))
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

            // Abstract "layout grid" echoing a news page — not a photo collage.
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

                Circle()
                    .stroke(CATheme.paper.opacity(0.15), lineWidth: 1)
                    .frame(width: 120, height: 120)
                    .offset(x: geo.size.width - 140, y: 18)

                Text(article.primaryActor.shortLabel)
                    .font(.system(size: 64, weight: .bold, design: .serif))
                    .foregroundStyle(CATheme.paper.opacity(0.10))
                    .offset(x: 16, y: 8)
            }

            VStack(alignment: .leading, spacing: 8) {
                Text(article.title)
                    .font(.system(size: 20, weight: .semibold, design: .serif))
                    .foregroundStyle(CATheme.paper)
                    .lineLimit(4)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(16)
        }
        .frame(height: 168)
    }

    private var bodyBlock: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text((beat ?? article.posterLede))
                .font(.system(size: 13, design: .default))
                .foregroundStyle(CATheme.ink.opacity(0.88))
                .lineSpacing(3)
                .lineLimit(5)
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: 6) {
                ForEach(article.actors.prefix(3), id: \.self) { actor in
                    Text(actor.shortLabel)
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(actor.accent.opacity(0.15))
                        .foregroundStyle(actor.accent)
                        .clipShape(RoundedRectangle(cornerRadius: 4, style: .continuous))
                }
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(CATheme.paper)
    }

    private var footer: some View {
        HStack {
            Text(article.publishedAt.formatted(date: .abbreviated, time: .omitted))
                .font(CATheme.mono)
                .foregroundStyle(CATheme.slate.opacity(0.7))
            Spacer()
            Text("Open original →")
                .font(CATheme.mono)
                .foregroundStyle(CATheme.teal)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(CATheme.mist.opacity(0.9))
    }

    private var posterBackground: some View {
        CATheme.paper
    }
}
