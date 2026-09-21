from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parent
with zipfile.ZipFile(R/'Character-Runtime.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((R/'runtime').iterdir()):
  if f.is_file() and f.name!='Preview.model3.json':z.write(f,'Character/'+f.name)
files=[]
for name in ['runtime','vendor','parts']:
 files.extend(f for f in (R/name).rglob('*') if f.is_file())
files.extend(f for f in R.iterdir() if f.is_file() and f.suffix in ['.py','.md','.json','.js','.cjs','.txt','.html','.psd','.png','.jpg','.wav'] and f.name!='package-manifest.json')
files.extend((R.parent/'tooling'/'py-moc3'/'src').rglob('*.py'))
files.extend((R.parent/'tooling'/'py-moc3').glob('LICENSE*'))
with zipfile.ZipFile(R/'Character-Source-Web.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(set(files)):z.write(f,str(f.relative_to(R.parent)))
report={}
for name in ['Character-Runtime.zip','Character-Source-Web.zip']:
 p=R/name
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 report[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(R/'package-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
