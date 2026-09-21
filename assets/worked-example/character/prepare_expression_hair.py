"""Add brow underpainting and source-pixel side-hair groups."""
from pathlib import Path
import json
import numpy as np
import cv2
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;layout=json.loads((R/'layout.json').read_text());layers=layout['layers'];W,H=layout['width'],layout['height']
skin=np.array(Image.open(R/'Face-underpaint-reviewed.png'))
polys={'Left':[(421,304),(461,301),(499,314),(499,328),(459,317),(422,319)],'Right':[(572,306),(619,290),(653,291),(653,305),(614,304),(573,320)]}
mask=np.zeros((H,W),bool)
for points in polys.values():
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);mask|=np.array(im)>0
for layer in layers:
 if layer['name'].startswith('Brow'):continue
 p=R/layer['texture'];a=np.array(Image.open(p));x,y,w,h=[layer[k] for k in ['x','y','w','h']];local=mask[y:y+h,x:x+w]
 a[local,:3]=skin[y:y+h,x:x+w,:3][local]
 if layer['name']=='Hair':a[local,3]=0
 Image.fromarray(a).save(p)
new=[]
for layer in layers:
 name=layer['name'];x,y,w,h=[layer[k] for k in ['x','y','w','h']];a=np.array(Image.open(R/layer['texture']))
 def save(name,img):
  Image.fromarray(img).save(R/'parts'/f'{name}.png');new.append(dict(layer,name=name,texture=f'parts/{name}.png'))
 if name.startswith('Brow'):
  under=a.copy();local=mask[y:y+h,x:x+w];under[local,:3]=skin[y:y+h,x:x+w,:3][local];save('BrowSkin'+name[4:],under);new.append(layer)
 elif name=='Hair':
  yy,xx=np.mgrid[y:y+h,x:x+w];navy=(a[:,:,2]>a[:,:,0]*1.02)&(a[:,:,0]<145)
  left=(xx<435)&(yy>170)&navy;right=(xx>640)&(yy>170)&navy
  front=(xx>=435)&(xx<=640)&(yy>90)&(yy<420)&(a[:,:,3]>0)
  hair_coverage=np.zeros((H,W),bool);hair_coverage[y:y+h,x:x+w]=a[:,:,3]>0
  selected=left|right|front;remaining=~selected
  base=a.copy();base[:,:,3]=np.where(cv2.dilate(remaining.astype('uint8'),np.ones((9,9),np.uint8))>0,a[:,:,3],0);save('Hair',base)
  for side,m in [('Left',left),('Right',right),('Front',front)]:
   piece=a.copy();piece[:,:,3]=np.where(m,a[:,:,3],0);save('HairFrontFlow' if side=='Front' else 'HairTips'+side,piece)
 else:new.append(layer)
# Grow hidden skin only underneath existing hair coverage, preserving the silhouette.
for l in new:
 if l['name']!='Face':continue
 a=np.array(Image.open(R/l['texture']));x,y,w,h=[l[k] for k in ['x','y','w','h']]
 full=np.zeros((H,W,4),dtype=np.uint8);full[y:y+h,x:x+w]=a
 valid=(full[:,:,3]>240);colors=full[:,:,:3].astype(np.float32)
 for _ in range(14):
  counts=cv2.boxFilter(valid.astype(np.float32),-1,(3,3),normalize=False)
  grow=(counts>0)&~valid&hair_coverage
  sums=cv2.boxFilter(colors*valid[:,:,None],-1,(3,3),normalize=False)
  colors[grow]=sums[grow]/counts[grow,None]
  valid|=grow;full[grow,3]=255
 full[:,:,:3]=np.clip(colors,0,255).astype(np.uint8)
 im=Image.fromarray(full);box=im.getbbox();im.crop(box).save(R/l['texture'])
 l.update(x=box[0],y=box[1],w=box[2]-box[0],h=box[3]-box[1])
layout['layers']=new;layout['status']='FULL_RIG_VISUAL_REFINEMENT';(R/'layout.json').write_text(json.dumps(layout,indent=2));print('Brow and side-hair groups:',len(new),'meshes')
