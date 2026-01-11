#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

APP_NAME="Pomodoro Timer"
BUNDLE_ID="com.pomodoro.timer"
ENTRYPOINT="src/pomodoro_timer/pomodoro.py"
SOUNDS_DIR="resources/sounds"
DIST_DIR="$PROJECT_ROOT/dist"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 Building $APP_NAME for macOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1) Clean previous build
rm -rf build dist *.spec || true

# 2) Ensure virtualenv for reproducible build
if [ ! -d .venv-build ]; then
  echo "📦 Creating build venv (.venv-build)"
  /usr/bin/python3 -m venv .venv-build
fi
VENV_PYTHON=".venv-build/bin/python"
source .venv-build/bin/activate
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt pyinstaller

# Optional icon
ICON_ARG=""
if [ -f "resources/icon.icns" ]; then
  ICON_ARG="--icon resources/icon.icns"
  echo "🎨 Using custom icon: resources/icon.icns"
else
  echo "⚠️  No icon found at resources/icon.icns (run scripts/create_icon.py to create one)"
fi

# 3) PyInstaller build (.app bundle)
echo "🚀 Running PyInstaller... (this may take a few minutes)"
ADD_DATA_ARGS=(
  --add-data "$SOUNDS_DIR/alarm.wav:resources/sounds"
  --add-data "$SOUNDS_DIR/break_alarm.wav:resources/sounds"
)

# Добавляем иконку PNG для использования в pygame (если существует)
if [ -f "resources/icon.png" ]; then
  ADD_DATA_ARGS+=("--add-data" "resources/icon.png:resources")
fi

"$VENV_PYTHON" -m PyInstaller \
  --name "$APP_NAME" \
  --windowed \
  --onedir \
  --clean \
  --noconfirm \
  --osx-bundle-identifier "$BUNDLE_ID" \
  $ICON_ARG \
  "${ADD_DATA_ARGS[@]}" \
  "$ENTRYPOINT"

echo "✅ App bundle created: dist/$APP_NAME.app"

# 4) Copy docs
mkdir -p "$DIST_DIR"
if [ -f "resources/docs/INSTALL_INSTRUCTIONS.md" ]; then
  cp "resources/docs/INSTALL_INSTRUCTIONS.md" "$DIST_DIR/"
fi
if [ -f "resources/docs/README.md" ]; then
  cp "resources/docs/README.md" "$DIST_DIR/README.md"
fi

# 5) Create ZIP for easy sharing
echo "📦 Creating ZIP archive..."
(cd dist && zip -r -q "PomodoroTimer-macOS.zip" "$APP_NAME.app")
echo "✅ ZIP ready: dist/PomodoroTimer-macOS.zip"

# 6) Create DMG installer (optional but nice)
DMG_NAME="PomodoroTimer-macOS.dmg"
echo "💿 Creating DMG..."
test -f "dist/$DMG_NAME" && rm -f "dist/$DMG_NAME"
hdiutil create -volname "PomodoroTimer" -srcfolder "dist/$APP_NAME.app" -ov -format UDZO "dist/$DMG_NAME" >/dev/null
echo "✅ DMG ready: dist/$DMG_NAME"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Done! Distribute either the ZIP or DMG from the dist/ folder."
echo "👉 First run on another Mac may require right-click → Open or xattr -cr."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


