"""Authoring diagnostic only; browser/Core visual inspection remains required."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;d=json.loads((R/'layout.json').read_text());W,H=d['width'],d['height']
comp=Image.new('RGBA',(W,H))
for l in d['layers']:
 if l['name'].startswith(('EyeMask','EyeClosed')) or l['name']=='MouthOpen':continue
 comp.alpha_composite(Image.open(R/l['texture']),(l['x'],l['y']))
comp.save(R/'Neutral-authoring.png')
ref=Image.open(R/'Reference.png').convert('RGBA')
def matte(im):
 bg=Image.new('RGBA',im.size,(52,68,94,255));bg.alpha_composite(im);return bg.convert('RGB')
a,b=matte(ref),matte(comp);face=np.abs(np.array(a).astype(float)-np.array(b).astype(float))[220:555,350:735]
pair=Image.new('RGB',(W*2,H));pair.paste(a,(0,0));pair.paste(b,(W,0));pair.save(R/'Neutral-authoring-comparison.jpg',quality=95)
report={'type':'AUTHORING_COMPOSITE_NOT_CORE_SCREENSHOT','faceMeanAbsoluteRgbDifference':float(face.mean()),'face99thPercentileAbsoluteRgbDifference':float(np.percentile(face,99)),'note':'Reference retains original slight interior transparency; rig normalizes near-opaque alpha. This comparison diagnoses lost source pixels but does not validate animation.'}
(R/'neutral-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
