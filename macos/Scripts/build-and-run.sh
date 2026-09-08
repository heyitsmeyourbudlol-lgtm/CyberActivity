#!/bin/zsh
# Build + run the native macOS CyberActivity app (requires full Xcode).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d /Applications/Xcode.app ]]; then
  echo "Full Xcode is required (SwiftUI / xcodebuild)." >&2
  echo "Install Xcode, then: sudo xcode-select -s /Applications/Xcode.app/Contents/Developer" >&2
  exit 1
fi

ACTIVE="$(xcode-select -p 2>/dev/null || true)"
if [[ "$ACTIVE" != *"/Xcode.app/"* ]]; then
  echo "Switching xcode-select to Xcode.app…"
  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
fi

if [[ ! -d CyberActivity.xcodeproj ]]; then
  command -v xcodegen >/dev/null 2>&1 || { echo "xcodegen required to regenerate project" >&2; exit 1; }
  xcodegen generate
fi

DERIVED="$ROOT/build/DerivedData"
echo "→ Building CyberActivity (macOS arm64 Debug)…"
xcodebuild \
  -project CyberActivity.xcodeproj \
  -scheme CyberActivity \
  -configuration Debug \
  -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath "$DERIVED" \
  CODE_SIGN_IDENTITY=- \
  CODE_SIGNING_ALLOWED=YES \
  build

APP="$DERIVED/Build/Products/Debug/CyberActivity.app"
if [[ -d "$APP" ]]; then
  echo "→ Opening $APP"
  open "$APP"
else
  echo "Build succeeded but app bundle not found at $APP" >&2
  exit 1
fi
