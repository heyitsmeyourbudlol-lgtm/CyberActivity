# CyberActivity

Native **SwiftUI macOS** briefing desk for state-sponsored cyber / adversarial AI / digital sovereignty.

## Primary product (Xcode)

The shippable, portable app lives here:

```text
macos/
  CyberActivity.xcodeproj   ← open this
  CyberActivity/            ← SwiftUI sources
  Scripts/
  README.md
```

**Export:** zip the entire `macos/` folder (or run `macos/Scripts/export-zip.sh`). On another Mac with Xcode: open `CyberActivity.xcodeproj` → ⌘R.

```bash
./macos/Scripts/open-xcode.sh
# Install Dock/Spotlight app:
./macos/Scripts/install-app.sh
# → /Applications/CyberActivity.app
```

Details, Ollama models, and `xcodebuild` steps: [macos/README.md](macos/README.md).

### Ollama defaults

| Role | Model |
|------|--------|
| Briefing / poster / article summary | `QyrouNnet/summarizer:400m` |
| Ask clarification | `DeepHat/DeepHat-V1-7B` |

Endpoint: `http://127.0.0.1:11434`

## Secondary / archived

| Path | Status |
|------|--------|
| `electron/`, `renderer/`, `package.json` | Former Electron prototype — kept for reference; **not** the primary product |
| `CyberActivity/` (Swift Package) | Incomplete SPM attempt — superseded by `macos/` |
| `dist/` | Electron build output |

Prefer the Xcode project under `macos/` for all new work and for moving the app to another machine.
