#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
APP="$ROOT/dist/mac-arm64/CyberActivity.app"
if [[ ! -d "$APP" ]]; then
  echo "Building CyberActivity.app…"
  cd "$ROOT"
  npm install
  npx electron-builder --mac dir --arm64
fi
open "$APP"
