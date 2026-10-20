"""Sign a macOS app inside out for notarization; invoked by packaging script."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1]);identity=sys.argv[2]
magic={bytes.fromhex(x) for x in ('feedface','cefaedfe','feedfacf','cffaedfe','cafebabe','bebafeca','cafebabf','bfbafeca')}
def sign(path):subprocess.run(['codesign','--force','--options','runtime','--timestamp','--sign',identity,str(path)],check=True)
files=[]
for p in root.rglob('*'):
 if p.is_symlink() or not p.is_file():continue
 with p.open('rb') as stream:head=stream.read(4)
 if head in magic:files.append(p)
for p in sorted(files,key=lambda x:len(x.parts),reverse=True):sign(p)
for p in sorted([p for p in root.rglob('*') if p.suffix in ('.app','.framework') and p.is_dir() and not p.is_symlink()],key=lambda x:len(x.parts),reverse=True):sign(p)
sign(root)
subprocess.run(['codesign','--verify','--deep','--strict',str(root)],check=True)
