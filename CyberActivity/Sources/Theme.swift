import SwiftUI

enum CATheme {
    static let ink = Color(red: 0.09, green: 0.11, blue: 0.13)
    static let slate = Color(red: 0.22, green: 0.27, blue: 0.31)
    static let mist = Color(red: 0.93, green: 0.94, blue: 0.92)
    static let paper = Color(red: 0.97, green: 0.97, blue: 0.95)
    static let signal = Color(red: 0.78, green: 0.28, blue: 0.18)
    static let teal = Color(red: 0.12, green: 0.45, blue: 0.48)
    static let amber = Color(red: 0.82, green: 0.55, blue: 0.18)
    static let china = Color(red: 0.72, green: 0.18, blue: 0.18)
    static let russia = Color(red: 0.18, green: 0.36, blue: 0.62)
    static let nk = Color(red: 0.42, green: 0.28, blue: 0.55)
    static let ai = Color(red: 0.15, green: 0.48, blue: 0.42)
    static let sovereignty = Color(red: 0.48, green: 0.38, blue: 0.22)

    static let display = Font.system(.largeTitle, design: .serif).weight(.semibold)
    static let title = Font.system(.title2, design: .serif).weight(.semibold)
    static let headline = Font.system(.title3, design: .serif).weight(.medium)
    static let body = Font.system(.body, design: .default)
    static let mono = Font.system(.caption, design: .monospaced)
}

extension ThreatActor {
    var accent: Color {
        switch self {
        case .russia: CATheme.russia
        case .china: CATheme.china
        case .northKorea: CATheme.nk
        case .adversarialAI: CATheme.ai
        case .digitalSovereignty: CATheme.sovereignty
        case .general: CATheme.slate
        }
    }
}
