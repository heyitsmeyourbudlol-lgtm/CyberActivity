// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "CyberActivity",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "CyberActivity", targets: ["CyberActivity"])
    ],
    targets: [
        .executableTarget(
            name: "CyberActivity",
            path: "Sources",
            linkerSettings: [
                .linkedFramework("SwiftUI"),
                .linkedFramework("AppKit"),
                .linkedFramework("FoundationModels"),
                .linkedFramework("NaturalLanguage")
            ]
        )
    ]
)
