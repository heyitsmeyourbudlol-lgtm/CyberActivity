import CoreText
import SwiftUI

enum CATheme {
    // Exact Electron palette from renderer/styles.css
    static let ink = Color(hex: 0x171C21)
    static let slate = Color(hex: 0x38454F)
    static let mist = Color(hex: 0xEDEEEA)
    static let paper = Color(hex: 0xF7F7F3)
    static let signal = Color(hex: 0xC7472E)
    static let teal = Color(hex: 0x1F737A)
    static let russia = Color(hex: 0x2E5C9E)
    static let china = Color(hex: 0xB82E2E)
    static let nk = Color(hex: 0x6B478C)
    static let ai = Color(hex: 0x267A6B)
    static let sovereignty = Color(hex: 0x7A6138)
    static let bg0 = Color(hex: 0xEFEEE8)
    static let bg1 = Color(hex: 0xE0E8E6)
    static let bg2 = Color(hex: 0xE8E6DE)

    /// Fraunces — display / headlines (Electron `--serif`)
    static func serif(_ size: CGFloat, weight: Font.Weight = .semibold) -> Font {
        let name: String
        switch weight {
        case .medium, .regular:
            name = "Fraunces-Medium"
        case .bold, .heavy, .black:
            name = "Fraunces-Display"
        default:
            name = size >= 36 ? "Fraunces-Display" : "Fraunces-SemiBold"
        }
        return Font.custom(name, size: size)
    }

    /// IBM Plex Sans — body UI (Electron `--sans`)
    static func sans(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        let name: String
        switch weight {
        case .semibold, .bold, .heavy, .black:
            name = "IBMPlexSans-SemiBold"
        case .medium:
            name = "IBMPlexSans-Medium"
        default:
            name = "IBMPlexSans-Regular"
        }
        return Font.custom(name, size: size)
    }

    /// IBM Plex Mono Medium — labels / meta (Electron `--mono`)
    static func mono(_ size: CGFloat = 11) -> Font {
        Font.custom("IBMPlexMono-Medium", size: size)
    }

    static let display = serif(42, weight: .semibold)
    static let title = serif(26, weight: .semibold)
    static let headline = serif(20, weight: .semibold)
    static let body = sans(14)
    static let monoCaption = mono(11)
}

extension Color {
    init(hex: UInt32, opacity: Double = 1) {
        let r = Double((hex >> 16) & 0xFF) / 255
        let g = Double((hex >> 8) & 0xFF) / 255
        let b = Double(hex & 0xFF) / 255
        self.init(.sRGB, red: r, green: g, blue: b, opacity: opacity)
    }
}

extension ThreatActor {
    var accent: Color {
        switch self {
        case .russia: return CATheme.russia
        case .china: return CATheme.china
        case .northKorea: return CATheme.nk
        case .adversarialAI: return CATheme.ai
        case .digitalSovereignty: return CATheme.sovereignty
        case .general: return CATheme.slate
        }
    }
}

enum FontRegistrar {
    static func registerBundledFonts() {
        var urls: [URL] = []
        urls.append(contentsOf: Bundle.main.urls(forResourcesWithExtension: "ttf", subdirectory: nil) ?? [])
        urls.append(contentsOf: Bundle.main.urls(forResourcesWithExtension: "ttf", subdirectory: "Fonts") ?? [])
        for url in urls {
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}
