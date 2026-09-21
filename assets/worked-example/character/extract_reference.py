"""Reference-pixel authoring baseline. No separately generated replacements.
Masks are initial authored selections; hidden regions require further cleanup.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import cv2,json
R=Path(__file__).resolve().parent
im=Image.open(R/'Reference.png').convert('RGBA');a=np.array(im);a[:,:,3]=np.where(a[:,:,3]>=245,255,a[:,:,3]);h,w=a.shape[:2]
y,x=np.mgrid[:h,:w];rgb=a[:,:,:3]
def polygon(points):
 p=Image.new('L',(w,h));ImageDraw.Draw(p).polygon(points,fill=255);return np.array(p)>0
# Head ends at the skin neckline; cream collar pixels stay in the torso.
navy_head=(rgb[:,:,2]>rgb[:,:,0]*1.02)&(rgb[:,:,0]<145)
neck=polygon([(440,440),(660,440),(650,529),(623,544),(591,555),(552,561),(513,553),(480,541),(448,526)])
side_hair=(y>=440)&(y<501)&(x>397)&(x<690)&navy_head
head=(y<450)|neck|side_hair
# Keep the neckline with the torso; ears belong to the face, not a second overlay.
skin=polygon([(351,326),(391,318),(430,299),(453,220),(489,217),(515,303),(570,311),(630,271),(695,312),(727,322),(736,369),(709,418),(678,437),(649,493),(598,539),(548,552),(503,529),(459,498),(429,454),(391,434),(360,398)])
features={
 'EyeLeft':polygon([(424,330),(467,328),(502,340),(503,355),(482,365),(452,365),(427,353)]),
 'EyeRight':polygon([(572,331),(614,315),(654,317),(656,338),(636,350),(600,357),(575,351)]),
 'BrowLeft':polygon([(421,304),(461,301),(499,314),(499,328),(459,317),(422,319)]),
 'BrowRight':polygon([(572,306),(619,290),(653,291),(653,305),(614,304),(573,320)]),
 'Nose':polygon([(516,369),(545,369),(563,411),(563,439),(525,439),(510,413)]),
 'Mouth':polygon([(498,445),(610,443),(610,482),(500,484)]),
}
# Navy pixels in the head zone identify hair, while dark lash pixels remain eyes.
navy=(rgb[:,:,2].astype(float)>rgb[:,:,0]*1.02)&(rgb[:,:,0]<145)
feature_union=np.logical_or.reduce(list(features.values()))
hair=head & ~feature_union & (~skin | navy)
face=head & ~hair
remaining=face.copy();masks={}
for name,mask in features.items():
 masks[name]=mask&remaining;remaining &=~mask
masks['Face']=remaining;masks['Hair']=hair;masks['Body']=~head
order=['Body','Face','EyeLeft','EyeRight','BrowLeft','BrowRight','Nose','Mouth','Hair']
(R/'parts').mkdir(exist_ok=True);layers=[];composite=Image.new('RGBA',(w,h))
for name in order:
 # Overlap neighboring source pixels to prevent bilinear alpha cracks.
 coverage=masks[name] | ((cv2.dilate(masks[name].astype('uint8'),np.ones((17,17),np.uint8))>0) & (a[:,:,3]==255))
 b=a.copy();b[:,:,3]=np.where(coverage,a[:,:,3],0)
 if name=='Body':
  # Extend clean collar color behind moving side hair instead of duplicating its outline.
  hidden=(side_hair & (y>450)).astype('uint8')*255
  hidden=cv2.dilate(hidden,np.ones((5,5),np.uint8))
  filled_collar=cv2.inpaint(rgb,hidden,5,cv2.INPAINT_TELEA)
  b[hidden>0,:3]=filled_collar[hidden>0]

 full=Image.fromarray(b);box=full.getbbox()
 if not box:continue
 piece=full.crop(box);piece.save(R/'parts'/f'{name}.png')
 composite.alpha_composite(piece,(box[0],box[1]));layers.append({'name':name,'x':box[0],'y':box[1],'w':piece.width,'h':piece.height,'texture':'parts/'+name+'.png'})
composite.save(R/'Reassembled.png')
# An inpaint candidate underneath original feature layers; kept separate for review.
feature_mask=(feature_union & face).astype('uint8')*255
filled=cv2.inpaint(rgb,feature_mask,5,cv2.INPAINT_TELEA)
base=a.copy();base[:,:,:3]=filled;base[:,:,3]=np.where(face,a[:,:,3],0)
Image.fromarray(base).save(R/'Face-underpaint-candidate.png')
# Baseline verifies reference fidelity only, not rig or hidden-region quality.
c=np.array(composite);visible=a[:,:,3]>0
report={'width':w,'height':h,'layers':layers,'visibleRgbMaxDifference':int(np.abs(c[:,:,:3].astype(int)-rgb.astype(int))[visible].max()),'alphaMaxDifference':int(np.abs(c[:,:,3].astype(int)-a[:,:,3].astype(int)).max()),'comparisonBasis':'Reference RGB with interior alpha >=245 normalized to255; silhouette alpha preserved','sourceInteriorAlphaNormalized':True,'status':'AUTHORING_BASELINE_NOT_ANIMATED'}

if (R/'Face-underpaint-generated.png').exists():
 generated=np.array(Image.open(R/'Face-underpaint-generated.png').convert('RGB').resize((410,340),Image.Resampling.LANCZOS))
 canvas=rgb.copy();canvas[220:560,340:750]=generated
 eye_brow=np.logical_or.reduce([features[n] for n in ['EyeLeft','EyeRight','BrowLeft','BrowRight']]) & face
 base[eye_brow,:3]=canvas[eye_brow]
 # A separate extended skin layer for subsequent rigging; original cut parts stay intact.
 base[base[:,:,3]==0,:3]=0
 Image.fromarray(base).save(R/'Face-underpaint-reviewed.png')

(R/'layout.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='layers'},indent=2))
