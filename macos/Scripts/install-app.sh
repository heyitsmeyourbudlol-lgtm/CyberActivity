#!/bin/zsh
# Build Release CyberActivity.app and install for Dock + Spotlight.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d /Applications/Xcode.app ]]; then
  echo "Full Xcode required at /Applications/Xcode.app" >&2
  exit 1
fi

ACTIVE="$(xcode-select -p 2>/dev/null || true)"
if [[ "$ACTIVE" != *"/Xcode.app/"* ]]; then
  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
fi

if [[ ! -d CyberActivity.xcodeproj ]]; then
  command -v xcodegen >/dev/null 2>&1 && xcodegen generate
fi

DERIVED="$ROOT/build/DerivedData"
echo "→ Building CyberActivity (macOS arm64 Release)…"
xcodebuild \
  -project CyberActivity.xcodeproj \
  -scheme CyberActivity \
  -configuration Release \
  -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath "$DERIVED" \
  CODE_SIGN_IDENTITY=- \
  CODE_SIGNING_ALLOWED=YES \
  build

APP_SRC="$DERIVED/Build/Products/Release/CyberActivity.app"
if [[ ! -d "$APP_SRC" ]]; then
  echo "Release app not found at $APP_SRC" >&2
  exit 1
fi

# Prefer /Applications; fall back to ~/Applications
if [[ -w /Applications ]] || mkdir -p /Applications 2>/dev/null; then
  DEST="/Applications/CyberActivity.app"
  echo "→ Installing to $DEST"
  rm -rf "$DEST"
  if cp -R "$APP_SRC" "$DEST" 2>/dev/null; then
    :
  else
    # May need elevated copy into /Applications
    sudo rm -rf "$DEST"
    sudo cp -R "$APP_SRC" "$DEST"
    sudo chown -R "$(whoami):staff" "$DEST" 2>/dev/null || true
  fi
else
  mkdir -p "$HOME/Applications"
  DEST="$HOME/Applications/CyberActivity.app"
  echo "→ Installing to $DEST"
  rm -rf "$DEST"
  cp -R "$APP_SRC" "$DEST"
fi

# Touch + reopen so Launch Services / Spotlight reindex the bundle
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$DEST" 2>/dev/null || true
mdimport "$DEST" 2>/dev/null || true

echo "→ Launching CyberActivity"
open -a "$DEST" || open "$DEST"

echo ""
echo "Installed: $DEST"
echo "Dock: right-click the icon → Options → Keep in Dock"
echo "Spotlight: search for CyberActivity"
