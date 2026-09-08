#!/bin/zsh
# Create a portable zip of the native Xcode project (everything needed to open+build).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$ROOT/.." && pwd)"
STAMP="$(date +%Y%m%d)"
OUT="$REPO/CyberActivity-macos-$STAMP.zip"

cd "$REPO"
rm -f "$OUT"
# Exclude local build products; keep sources + xcodeproj + scripts + docs
zip -r "$OUT" macos \
  -x "macos/build/*" \
  -x "macos/**/.DS_Store" \
  -x "macos/**/*.xcuserstate" \
  -x "macos/**/xcuserdata/*"

echo "Export ready: $OUT"
echo "On another Mac: unzip, open macos/CyberActivity.xcodeproj, ⌘R"
