#!/bin/zsh
# Opens the primary native Xcode project under macos/.
exec "$(cd "$(dirname "$0")/.." && pwd)/macos/Scripts/open-xcode.sh"
