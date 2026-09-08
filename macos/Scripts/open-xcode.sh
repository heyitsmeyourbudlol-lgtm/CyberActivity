#!/bin/zsh
# Open the native CyberActivity Xcode project (self-contained in macos/).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJ="$ROOT/CyberActivity.xcodeproj"
SPEC="$ROOT/project.yml"

if [[ ! -d "$PROJ" ]]; then
  if command -v xcodegen >/dev/null 2>&1 && [[ -f "$SPEC" ]]; then
    echo "Generating $PROJ via XcodeGen…"
    (cd "$ROOT" && xcodegen generate)
  else
    echo "Missing $PROJ. Install XcodeGen (brew install xcodegen) and run: xcodegen generate" >&2
    exit 1
  fi
fi

if [[ ! -d /Applications/Xcode.app ]]; then
  echo "Note: Full Xcode is not installed at /Applications/Xcode.app yet."
  echo "Install from the App Store (or xcodes), then:"
  echo "  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer"
fi

open "$PROJ"
