#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
APP="$PWD/dist/PowerMaster II Display.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" /tmp/powermaster-swift-cache
swiftc -module-cache-path /tmp/powermaster-swift-cache -O Sources/App.swift -framework Cocoa -framework WebKit -o "$APP/Contents/MacOS/PowerMasterIIDisplay"
cp Sources/*.py Sources/*.html "$APP/Contents/Resources/"
/usr/bin/python3 - "$APP" <<'PY'
import plistlib,sys
from pathlib import Path
p=Path(sys.argv[1])/'Contents'/'Info.plist'
p.write_bytes(plistlib.dumps(dict(CFBundleIdentifier='com.grmi64.PowerMasterIIDisplay',CFBundleName='PowerMaster II Display',CFBundleDisplayName='PowerMaster II Display',CFBundleExecutable='PowerMasterIIDisplay',CFBundlePackageType='APPL',CFBundleShortVersionString='0.2.0',CFBundleVersion='3',LSMinimumSystemVersion='12.0',NSHighResolutionCapable=True,NSPrincipalClass='NSApplication')))
PY
codesign --force --deep --sign - "$APP"
echo "$APP"
