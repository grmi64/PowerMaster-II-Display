#!/bin/bash
# Build paired DMGs from current built apps. Pass --preview for ad-hoc test images.
set -euo pipefail
cd "$(dirname "$0")/.."
PREVIEW=false
if [[ "${1:-}" == --preview ]]; then PREVIEW=true; shift; fi
DX_SOURCE="${1:-$PWD/../DX-Caliber/DX Caliber DEV.app}"
METER_SOURCE="$PWD/dist/PowerMaster II Display.app"
IDENTITY='Developer ID Application: Greg Miller (5DD7E8D68A)'
PROFILE='DXCaliber-notary'
OUT="$PWD/release/station-suite"
mkdir -p "$OUT"
STAGE="$(mktemp -d "$OUT/stage.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT
[[ -d "$DX_SOURCE" && -d "$METER_SOURCE" ]] || { echo 'Build both apps first.' >&2; exit 1; }
mkdir -p "$STAGE/apps" "$STAGE/combined" "$STAGE/meter"
DX_NAME="$(basename "$DX_SOURCE")"
ditto "$DX_SOURCE" "$STAGE/apps/$DX_NAME"
ditto "$METER_SOURCE" "$STAGE/apps/PowerMaster II Display.app"
notarize(){
  local artifact="$1" result="$2"
  xcrun notarytool submit "$artifact" --keychain-profile "$PROFILE" --wait --output-format json > "$result"
  cat "$result"
  /usr/bin/python3 - "$result" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
if r.get('status')!='Accepted':raise SystemExit('Not accepted: '+str(r.get('id'))+'. Retrieve the log with notarytool before continuing.')
PY
}
if ! $PREVIEW; then
  /usr/bin/python3 scripts/sign_bundle.py "$STAGE/apps/$DX_NAME" "$IDENTITY"
  /usr/bin/python3 scripts/sign_bundle.py "$STAGE/apps/PowerMaster II Display.app" "$IDENTITY"
  ditto -c -k --sequesterRsrc --keepParent "$STAGE/apps" "$OUT/apps-for-notarization.zip"
  notarize "$OUT/apps-for-notarization.zip" "$OUT/apps-notarization.json"
  for app in "$STAGE/apps/"*.app; do
    xcrun stapler staple "$app"
    xcrun stapler validate "$app"
    spctl --assess --type execute --verbose=2 "$app"
  done
fi
ditto "$STAGE/apps/$DX_NAME" "$STAGE/combined/$DX_NAME"
ditto "$STAGE/apps/PowerMaster II Display.app" "$STAGE/combined/PowerMaster II Display.app"
ditto "$STAGE/apps/PowerMaster II Display.app" "$STAGE/meter/PowerMaster II Display.app"
ln -s /Applications "$STAGE/combined/Applications"
ln -s /Applications "$STAGE/meter/Applications"
cat > "$STAGE/combined/Read Me.txt" <<'TXT'
DX Caliber DEV + PowerMaster II Display (Apple Silicon preview)

Quit older copies first. Drag both apps to Applications. Open PowerMaster II Display once, select the meter USB port and its baud (usually 38400), and connect.

To share live data, enable "Share readings with DX Caliber on this Mac" in the meter app. In DX Caliber Settings > Station Accessories > PowerMaster II, enable "Receive meter data in DX Caliber" and save settings. Sharing and reception both default off. Launch at startup is a separate option.

The meter display works independently. Closing DX Caliber does not stop it. DX Caliber never opens the USB meter port.

This package contains a DEV build of DX Caliber, not a production upgrade. Meter app is Apple Silicon only. True PEP is not implemented; peak hold is based on received samples.
TXT
cat > "$STAGE/meter/Read Me.txt" <<'TXT'
PowerMaster II Display 0.4.0 (Apple Silicon)

Quit older copies. Drag PowerMaster II Display to Applications, launch it, choose the USB port and matching baud, and connect.

The app works standalone; no DX Caliber installation or separate Python is required. Sharing with DX Caliber is optional and off by default. True PEP is not implemented; peak hold is based on received samples.
TXT
SUFFIX=''
if $PREVIEW; then
 SUFFIX='-preview'
 for target in combined meter; do
  printf '\nUNNOTARIZED DEVELOPMENT PREVIEW. Do not distribute as a signed release.\n' >> "$STAGE/$target/Read Me.txt"
 done
fi
COMBINED="$OUT/DX-Caliber-DEV-0.6.59-PowerMaster-II-0.4.0-arm64${SUFFIX}.dmg"
METER="$OUT/PowerMaster-II-Display-0.4.0-arm64${SUFFIX}.dmg"
for kind in combined meter; do
  if [[ "$kind" == combined ]]; then image="$COMBINED"; volume='DX Caliber + PowerMaster II'; else image="$METER"; volume='PowerMaster II Display'; fi
  hdiutil create -ov -volname "$volume" -srcfolder "$STAGE/$kind" -format UDZO "$image"
  hdiutil verify "$image"
  if ! $PREVIEW; then
   codesign --force --timestamp --sign "$IDENTITY" "$image"
   notarize "$image" "$image.notarization.json"
   xcrun stapler staple "$image"
   xcrun stapler validate "$image"
   spctl --assess --type open --context context:primary-signature --verbose=2 "$image"
  fi
done
shasum -a 256 "$COMBINED" "$METER" > "$OUT/SHA256SUMS${SUFFIX}.txt"
printf 'Combined: %s\nMeter only: %s\n' "$COMBINED" "$METER"
