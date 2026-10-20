#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
IDENTITY='Developer ID Application: Greg Miller (5DD7E8D68A)'
PROFILE='DXCaliber-notary'
SOURCE="$PWD/dist/PowerMaster II Display.app"
RELEASE="$PWD/release"
APP="$RELEASE/PowerMaster II Display.app"
mkdir -p "$RELEASE"
if [[ ! -d "$SOURCE" ]]; then
  echo "Missing built app: $SOURCE" >&2
  exit 1
fi
# Keep the development build intact; sign a release copy.
ditto "$SOURCE" "$APP"
python3 - "$APP" "$IDENTITY" <<'PY'
import pathlib, subprocess, sys
root=pathlib.Path(sys.argv[1]); identity=sys.argv[2]
magic={bytes.fromhex(x) for x in ('feedface','cefaedfe','feedfacf','cffaedfe','cafebabe','bebafeca','cafebabf','bfbafeca')}
files=[]
for p in root.rglob('*'):
    if p.is_symlink() or not p.is_file():continue
    with p.open('rb') as f:head=f.read(4)
    if head in magic:files.append(p)
def sign(p):
    print('Signing:',p,flush=True)
    subprocess.run(['codesign','--force','--options','runtime','--timestamp','--sign',identity,str(p)],check=True)
for p in sorted(files,key=lambda p:len(p.parts),reverse=True):sign(p)
for p in sorted(root.rglob('*.framework'),key=lambda p:len(p.parts),reverse=True):
    if not p.is_symlink():sign(p)
sign(root)
PY
codesign --verify --deep --strict --verbose=2 "$APP"
ZIP="$RELEASE/PowerMaster-II-Display-0.4.0-notarization.zip"
ditto -c -k --sequesterRsrc --keepParent "$APP" "$ZIP"
xcrun notarytool submit "$ZIP" --keychain-profile "$PROFILE" --wait --output-format json > "$RELEASE/notarization-result.json"
cat "$RELEASE/notarization-result.json"
python3 - "$RELEASE/notarization-result.json" <<'PY'
import json,sys
result=json.load(open(sys.argv[1]))
if result.get('status')!='Accepted':
    raise SystemExit('Notarization not accepted. Submission ID: '+str(result.get('id'))+'; inspect with xcrun notarytool log ID --keychain-profile DXCaliber-notary')
PY
xcrun stapler staple "$APP"
xcrun stapler validate "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"
spctl --assess --type execute --verbose=2 "$APP"
FINAL="$RELEASE/PowerMaster-II-Display-0.4.0-notarized.zip"
ditto -c -k --sequesterRsrc --keepParent "$APP" "$FINAL"
echo "Completed: $FINAL"
