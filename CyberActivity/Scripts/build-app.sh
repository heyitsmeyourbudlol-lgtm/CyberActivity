#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="CyberActivity"
BUILD_DIR="$ROOT/.build"
APP_DIR="$ROOT/dist/${APP_NAME}.app"
CONTENTS="$APP_DIR/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

cd "$ROOT"

echo "→ Building $APP_NAME…"
swift build -c release --product CyberActivity

BIN="$(swift build -c release --show-bin-path)/CyberActivity"
if [[ ! -x "$BIN" ]]; then
  echo "Binary not found at $BIN" >&2
  exit 1
fi

rm -rf "$APP_DIR"
mkdir -p "$MACOS" "$RESOURCES"

cat > "$CONTENTS/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>CyberActivity</string>
  <key>CFBundleIdentifier</key>
  <string>studio.cyberactivity.app</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>CyberActivity</string>
  <key>CFBundleDisplayName</key>
  <string>CyberActivity</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>14.0</string>
  <key>LSApplicationCategoryType</key>
  <string>public.app-category.news</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSPrincipalClass</key>
  <string>NSApplication</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
</dict>
</plist>
PLIST

# Simple generated icon (PDF-free): create .icns from a solid-color PNG if sips/iconutil available
ICONSET="$BUILD_DIR/AppIcon.iconset"
mkdir -p "$ICONSET"
python3 - <<'PY'
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    # Fallback: write a tiny PPM then convert via sips if needed — skip icon
    Path("/tmp/ca_skip_icon").write_text("1")
    raise SystemExit(0)

out = Path(".build/AppIcon.iconset")
for size in (16, 32, 64, 128, 256, 512, 1024):
    img = Image.new("RGBA", (size, size), (24, 30, 34, 255))
    d = ImageDraw.Draw(img)
    margin = max(2, size // 10)
    d.rounded_rectangle([margin, margin, size - margin, size - margin], radius=size // 6, fill=(30, 115, 122, 255))
    # CA monogram
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/NewYork.ttf", size=int(size * 0.38))
    except Exception:
        font = ImageFont.load_default()
    text = "CA"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2, (size - th) / 2 - size * 0.04), text, fill=(247, 247, 243, 255), font=font)
    img.save(out / f"icon_{size}x{size}.png")
    if size <= 512:
        img2 = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
        img2.save(out / f"icon_{size}x{size}@2x.png")
print("iconset ready")
PY

if [[ ! -f /tmp/ca_skip_icon ]] && command -v iconutil >/dev/null 2>&1; then
  iconutil -c icns "$ICONSET" -o "$RESOURCES/AppIcon.icns" || true
fi
rm -f /tmp/ca_skip_icon

cp "$BIN" "$MACOS/CyberActivity"
chmod +x "$MACOS/CyberActivity"

# ad-hoc sign so Gatekeeper is happier for local runs
codesign --force --deep --sign - "$APP_DIR" 2>/dev/null || true

echo "✓ Built $APP_DIR"
echo "  Open with: open \"$APP_DIR\""
