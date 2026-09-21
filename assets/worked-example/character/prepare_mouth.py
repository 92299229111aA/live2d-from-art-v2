"""Preserve the source smile; author hidden oral cavity and independent lower lip."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
layout=json.loads((R/'layout.json').read_text());layers=layout['layers'];W,H=layout['width'],layout['height']
def seam(x):return np.interp(x,[506,514,537,553,571,590,601],[461,464,462,462,459,457,453])
maskim=Image.new('L',(W,H));ImageDraw.Draw(maskim).polygon([(498,443),(610,443),(610,482),(500,484)],fill=255);mask=np.array(maskim)>0
skin=np.array(Image.open(R/'Face-underpaint-candidate.png'))
for layer in layers:
 if layer['name']=='Mouth':continue
 p=R/layer['texture'];a=np.array(Image.open(p));x,y,w,h=[layer[k] for k in ['x','y','w','h']];local=mask[y:y+h,x:x+w]
 a[local,:3]=skin[y:y+h,x:x+w,:3][local];Image.fromarray(a).save(p)
new=[]
for layer in layers:
 if layer['name']!='Mouth':new.append(layer);continue
 x,y,w,h=[layer[k] for k in ['x','y','w','h']];original=np.array(Image.open(R/layer['texture']));yy,xx=np.mgrid[y:y+h,x:x+w];line=seam(xx)
 def save(name,a):
  Image.fromarray(a).save(R/'parts'/f'{name}.png');new.append(dict(layer,name=name,texture=f'parts/{name}.png'))
 under=original.copy();local=mask[y:y+h,x:x+w];under[local,:3]=skin[y:y+h,x:x+w,:3][local];save('MouthSkin',under)
 u=np.clip((xx-506)/95,0,1);depth=14*np.sin(np.pi*u)**.9;v=(yy-line)/np.maximum(depth,1)
 cavity=np.zeros_like(original);inside=(xx>=506)&(xx<=601)&(yy>=line)&(yy<=line+depth)
 cavity[:,:,:3]=[63,26,32];cavity[:,:,3]=np.where(inside,255,0)
 teeth=inside&(v<.18)&(u>.17)&(u<.86);cavity[teeth,:3]=[233,215,199]
 tongue=inside&(v>.68)&(u>.25)&(u<.75);cavity[tongue,:3]=[150,77,81]
 save('MouthOpen',cavity)
 upper=original.copy();upper[:,:,3]=np.where(yy<=line+1,original[:,:,3],0);save('MouthUpper',upper)
 lower=original.copy();lower[:,:,3]=np.where(yy>=line,original[:,:,3],0);save('MouthLower',lower)
layout['layers']=new;layout['status']='EYE_AND_MOUTH_BINDING_IN_PROGRESS';(R/'layout.json').write_text(json.dumps(layout,indent=2));print('Mouth layers:',len(new),'total meshes')
