"""Create independent eye aperture masks, stationary source eyes, and hidden skin."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
layout=json.loads((R/'layout.json').read_text());layers=layout['layers'];W,H=layout['width'],layout['height']
ref=np.array(Image.open(R/'Reference.png').convert('RGBA'));ref[:,:,3]=np.where(ref[:,:,3]>=245,255,ref[:,:,3])
generated=np.array(Image.open(R/'Face-underpaint-generated.png').convert('RGB').resize((410,340),Image.Resampling.LANCZOS))
skin=np.array(Image.open(R/'Face-underpaint-reviewed.png'))[:,:,:3]
# Feature extraction masks define the original eye region, without enlarged overlap.
polys={'Left':[(424,330),(467,328),(502,340),(503,355),(482,365),(452,365),(427,353)],'Right':[(572,331),(614,315),(654,317),(656,338),(636,350),(600,357),(575,351)]}
allmask=np.zeros((H,W),bool)
for points in polys.values():
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);allmask|=np.array(im)>0
# Existing overlapping meshes must not retain duplicate eye pixels under the aperture.
for layer in layers:
 if layer['name'].startswith('Eye'):continue
 p=R/layer['texture'];a=np.array(Image.open(p));x,y,w,h=[layer[k] for k in ['x','y','w','h']];mask=allmask[y:y+h,x:x+w]
 a[mask,:3]=skin[y:y+h,x:x+w][mask]
 if layer['name']=='Hair':a[mask,3]=0
 Image.fromarray(a).save(p)
new=[]
for layer in layers:
 name=layer['name']
 if name not in ['EyeLeft','EyeRight']:
  new.append(layer);continue
 side=name[3:];x,y,w,h=[layer[k] for k in ['x','y','w','h']]
 # Full original image remains unscaled, clipped by the animated white aperture.
 eye=np.array(Image.open(R/layer['texture']))
 under=eye.copy();local=allmask[y:y+h,x:x+w];under[local,:3]=skin[y:y+h,x:x+w][local]
 skin_name='EyeSkin'+side;Image.fromarray(under).save(R/'parts'/f'{skin_name}.png')
 new.append(dict(layer,name=skin_name,texture=f'parts/{skin_name}.png'))
 mask=eye.copy();mask[:,:,:3]=255
 mask_name='EyeMask'+side;Image.fromarray(mask).save(R/'parts'/f'{mask_name}.png')
 new.append(dict(layer,name=mask_name,texture=f'parts/{mask_name}.png'))
 new.append(layer)
 # Fine closed eyelash follows the original eye corner slant.
 scale=4;line=Image.new('RGBA',(w*scale,h*scale));d=ImageDraw.Draw(line)
 pts=[]
 for i in range(81):
  u=i/80;gx=(426+76*u) if side=='Left' else (574+80*u)
  gy=(345+9*u+5*np.sin(np.pi*u)) if side=='Left' else (345-13*u+5*np.sin(np.pi*u))
  pts.append(((gx-x)*scale,(gy-y)*scale))
 d.line(pts,fill=(71,48,46,255),width=5,joint='curve')
 line=line.resize((w,h),Image.Resampling.LANCZOS);closed='EyeClosed'+side;line.save(R/'parts'/f'{closed}.png')
 new.append(dict(layer,name=closed,texture=f'parts/{closed}.png'))
layout['layers']=new;layout['status']='EYE_APERTURE_BINDING_IN_PROGRESS';layout['baselineReportBeforeEyePreparation']=True
(R/'layout.json').write_text(json.dumps(layout,indent=2))
print('Prepared eye masks and stationary eye textures:',len(new),'meshes')
