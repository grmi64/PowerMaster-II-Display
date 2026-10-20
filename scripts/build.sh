#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
APP="$PWD/dist/PowerMaster II Display.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" /tmp/powermaster-swift-cache
swiftc -module-cache-path /tmp/powermaster-swift-cache -O Sources/App.swift -framework Cocoa -framework WebKit -o "$APP/Contents/MacOS/PowerMasterIIDisplay"
BUILD_PYTHON="${PM_BUILD_PYTHON:-/tmp/powermaster-build-env/bin/python}"
PYINSTALLER_CONFIG_DIR=/tmp/powermaster-pyinstaller "$BUILD_PYTHON" -m PyInstaller --noconfirm --onedir --name meter-reader --distpath /tmp/powermaster-frozen --workpath /tmp/powermaster-freeze-work --specpath /tmp/powermaster-freeze-spec --add-data "$PWD/Sources/powermaster_ui.html:." Sources/powermaster_web.py
# Remove stale source-only resources from older builds.
find "$APP/Contents/Resources" -maxdepth 1 -type f \( -name '*.py' -o -name '*.html' \) -delete
ditto /tmp/powermaster-frozen/meter-reader "$APP/Contents/Resources/meter-reader"
/usr/bin/python3 - "$APP" <<'PY'
import plistlib,sys
from pathlib import Path
p=Path(sys.argv[1])/'Contents'/'Info.plist'
p.write_bytes(plistlib.dumps(dict(CFBundleIdentifier='com.grmi64.PowerMasterIIDisplay',CFBundleName='PowerMaster II Display',CFBundleDisplayName='PowerMaster II Display',CFBundleExecutable='PowerMasterIIDisplay',CFBundlePackageType='APPL',CFBundleShortVersionString='0.4.3',CFBundleVersion='8',LSMinimumSystemVersion='12.0',NSHighResolutionCapable=True,NSPrincipalClass='NSApplication')))
PY
mkdir -p "$APP/Contents/Resources/ThirdParty"
cp ThirdParty/* "$APP/Contents/Resources/ThirdParty/"
codesign --force --deep --sign - "$APP"
echo "$APP"
