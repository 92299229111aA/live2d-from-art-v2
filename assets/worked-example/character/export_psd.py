from pathlib import Path
import sys,json
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
R=Path(__file__).resolve().parent;d=json.loads((R/'layout.json').read_text());size=(d['width'],d['height']);psd=PSDImage.new('RGBA',size);preview=Image.new('RGBA',size)
for l in d['layers']:
 im=Image.open(R/l['texture']);layer=PixelLayer.frompil(im,psd,name=l['name'],left=l['x'],top=l['y'])
 hidden=l['name'].startswith(('EyeMask','EyeClosed')) or l['name']=='MouthOpen';layer.visible=not hidden
 if not hidden:preview.alpha_composite(im,(l['x'],l['y']))
psd._record.image_data.set_data([ch.tobytes() for ch in preview.split()],psd._record.header)
with (R/'Character-Layers.psd').open('wb') as f:psd._record.write(f)
check=PSDImage.open(R/'Character-Layers.psd');assert check.size==size and len(check)==len(d['layers']);print('PSD verified:',check.size,len(check),'layers')
