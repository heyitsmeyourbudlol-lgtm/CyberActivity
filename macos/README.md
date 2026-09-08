# CyberActivity (native macOS)

This folder is the **primary, portable CyberActivity product**: a self-contained SwiftUI macOS app for Xcode.

Zip or copy **this entire `macos/` directory** to another Mac that has Xcode. No Electron, npm, or Node required.

## Contents

| Path | Role |
|------|------|
| `CyberActivity.xcodeproj` | Open this in Xcode |
| `CyberActivity/` | SwiftUI sources, Info.plist, entitlements, assets |
| `Scripts/open-xcode.sh` | Opens the project |
| `Scripts/build-and-run.sh` | CLI build + launch (requires Xcode) |
| `project.yml` | Optional XcodeGen spec (only if you regenerate the project) |

## Open in Xcode

```bash
open /path/to/macos/CyberActivity.xcodeproj
# or
./Scripts/open-xcode.sh
```

Then press **⌘R** (scheme: **CyberActivity**, destination: **My Mac**).

## Install as a normal Mac app (Dock + Spotlight)

One step — Release build, copy to `/Applications`, register with Launch Services, launch:

```bash
./Scripts/install-app.sh
```

Installed path (preferred): **`/Applications/CyberActivity.app`**

- Dock: right-click the running icon → **Options → Keep in Dock**
- Spotlight / Cmd-space: type **CyberActivity**
- Display name / bundle: `CFBundleDisplayName` = CyberActivity, `CFBundleIdentifier` = `studio.cyberactivity.app`

Falls back to `~/Applications/CyberActivity.app` if `/Applications` is not writable.

## Build from the command line

Requires full Xcode (not Command Line Tools only):

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
cd /path/to/macos
xcodebuild \
  -project CyberActivity.xcodeproj \
  -scheme CyberActivity \
  -configuration Release \
  -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath ./build/DerivedData \
  CODE_SIGN_IDENTITY=- \
  build
# Then install:
./Scripts/install-app.sh
```

Or Debug only: `./Scripts/build-and-run.sh`

## Features (parity with former Electron UI)

- Feed ingest: The Record, Lawfare, Krebs, Lawfare via Google News, state-cyber watch
- Actor filters: Russia / China / North Korea / adversarial AI / digital sovereignty
- Article poster grid + actor board
- AI briefing via local Ollama summarizer **`QyrouNnet/summarizer:400m`**
- Poster click → high-level summary modal (same summarizer)
- Open original → default browser
- Ask clarification → **`DeepHat/DeepHat-V1-7B`**
- Teal/slate + system serif (New York) design language

## Ollama

App Sandbox allows outbound client networking; ATS allows local HTTP to `127.0.0.1`.

```bash
ollama serve   # if not already running
ollama pull QyrouNnet/summarizer:400m
ollama pull DeepHat/DeepHat-V1-7B
```

Optional env overrides (when launching from Terminal):

- `OLLAMA_HOST` (default `http://127.0.0.1:11434`)
- `CYBERACTIVITY_MODEL` (default summarizer)
- `CYBERACTIVITY_CYBER_MODEL` (default DeepHat)

## Export checklist

Copy or zip:

```text
macos/
  CyberActivity.xcodeproj/
  CyberActivity/
  Scripts/
  project.yml          # optional
  README.md
```

Do **not** require `node_modules`, `electron/`, or the incomplete SPM under `../CyberActivity/`.

## Requirements

- macOS 14+
- Xcode 15+ (full app under `/Applications/Xcode.app`)
- Local Ollama for AI briefings (extractive fallback if Ollama is down)
