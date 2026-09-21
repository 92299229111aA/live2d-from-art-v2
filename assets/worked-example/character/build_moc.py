"""Direct MOC3 authoring experiment; no Cubism Editor, no borrowed character rig."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tooling/py-moc3/src'))
from moc3 import Moc3
from moc3._core import SECTION_LAYOUT,ElemType
# Correct upstream's swapped vertex/index count entries against the format table.
SECTION_LAYOUT[41],SECTION_LAYOUT[44]=SECTION_LAYOUT[44],SECTION_LAYOUT[41]
SECTION_LAYOUT[82],SECTION_LAYOUT[83]=SECTION_LAYOUT[83],SECTION_LAYOUT[82]
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent
out=ROOT/'runtime';out.mkdir(exist_ok=True)
layout=json.loads((ROOT/'layout.json').read_text());layers=layout['layers'];n=len(layers)
COLS,ROWS=7,11
NV=COLS*ROWS; NF=NV*2; STRIDE=((NF+15)//16)*16; NI=(COLS-1)*(ROWS-1)*6
m=Moc3();m.canvas.pixels_per_unit=1000;m.canvas.origin_x=543;m.canvas.origin_y=724;m.canvas.canvas_width=1086;m.canvas.canvas_height=1448
m.counts[4]=n;m.counts[9]=n;m.counts[10]=STRIDE*n;m.counts[15]=NF*n;m.counts[16]=NI*n;m.counts[18]=1;m.counts[19]=n
m.counts[12]=1
for e in SECTION_LAYOUT:
 if e.elem_type!=ElemType.RUNTIME:m[e.name]=[('' if e.elem_type==ElemType.STR64 else 0)]*m.counts[e.count_idx]
def put(k,v):m[k]=v
put('art_mesh.ids',[l['name'] for l in layers])
for k in ['keyform_binding_band_indices','parent_part_indices','parent_deformer_indices']:put('art_mesh.'+k,[-1]*n)
put('art_mesh.keyform_binding_band_indices',[0]*n)
for k in ['visibles','enables']:put('art_mesh.'+k,[True]*n)
put('art_mesh.keyform_begin_indices',list(range(n)));put('art_mesh.keyform_counts',[1]*n)
put('art_mesh.vertex_counts',[NV]*n);put('art_mesh.position_index_counts',[NI]*n)
put('art_mesh.drawable_flags',[4]*n)
# Each iris is clipped by its own animated eye opening, never squashed.
mask_indices=[];mask_begins=[];mask_counts=[]
names=[l['name'] for l in layers]
for name in names:
 mask_begins.append(len(mask_indices))
 if name in ['EyeLeft','EyeRight']:
  mask_indices.append(names.index(name.replace('Eye','EyeMask',1)))
  mask_counts.append(1)
 else:mask_counts.append(0)
m.counts[17]=len(mask_indices)
put('art_mesh.mask_begin_indices',mask_begins)
put('art_mesh.mask_counts',mask_counts)
put('drawable_mask.art_mesh_indices',mask_indices)
put('art_mesh.uv_begin_indices',[i*NF for i in range(n)])
put('art_mesh.position_index_begin_indices',[i*NI for i in range(n)])
put('art_mesh_keyform.opacities',[1.]*n);put('art_mesh_keyform.draw_orders',[float(i) for i in range(n)])
put('art_mesh_keyform.keyform_position_begin_indices',[i*STRIDE for i in range(n)])
xy=[];uv=[];indices=[];atlas=Image.new('RGBA',(4096,4096));cx=cy=rowh=4
for l in layers:
 im=Image.open(ROOT/l['texture']);w,h=im.size
 if cx+w+4>4096:cx=4;cy+=rowh+4;rowh=0
 assert cy+h+4<=4096
 # Extrude texture edges so bilinear sampling cannot create dark crop borders.
 padded=Image.fromarray(np.pad(np.array(im),((2,2),(2,2),(0,0)),mode='edge'))
 atlas.paste(padded,(cx-2,cy-2))
 x,y=(l['x']-543)/1000,(l['y']-724)/1000;ww,hh=w/1000,h/1000
 for row in range(ROWS):
  for col in range(COLS):
   u,v=col/(COLS-1),row/(ROWS-1)
   uv.extend([(cx+w*u)/4096,(cy+h*v)/4096]);xy.extend([x+ww*u,y+hh*v])
 xy.extend([0.]*(STRIDE-NF))
 for row in range(ROWS-1):
  for col in range(COLS-1):
   a=row*COLS+col;b=a+1;c=a+COLS;d=c+1
   indices.extend([a,c,b,b,c,d])
 cx+=w+4;rowh=max(rowh,h)
put('uv.xys',uv);put('keyform_position.xys',xy);put('position_index.indices',indices)
for k,v in [('object_begin_indices',[0]),('object_counts',[n]),('object_total_counts',[n]),('min_draw_orders',[0]),('max_draw_orders',[n-1])]:put('draw_order_group.'+k,v)
put('draw_order_group_object.types',[0]*n);put('draw_order_group_object.indices',list(range(n)));put('draw_order_group_object.group_indices',[-1]*n)
# Independently controllable parameters with explicit keyforms.
params=[('ParamAngleZ',[-10.,0.,10.],0.),('ParamEyeLOpen',[0.,.2,.5,.75,1.],1.),('ParamEyeROpen',[0.,.2,.5,.75,1.],1.),('ParamMouthOpenY',[0.,.15,.45,1.],0.),('ParamBreath',[0.,1.],0.),('ParamHairSwing',[-1.,0.,1.],0.),('ParamBrowLY',[-1.,0.,1.],0.),('ParamBrowRY',[-1.,0.,1.],0.),('ParamAngleX',[-8.,0.,8.],0.),('ParamEyeBallX',[-1.,0.,1.],0.),('ParamBodySway',[-1.,0.,1.],0.),('ParamShoulderLift',[-1.,0.,1.],0.),('ParamHairRight',[-1.,0.,1.],0.),('ParamHairFront',[-1.,0.,1.],0.)]
p=len(params);m.counts[5]=p;m.counts[11]=p;m.counts[12]=p+1;m.counts[13]=p;m.counts[14]=sum(len(v) for _,v,_ in params)
put('parameter.ids',[a for a,_,_ in params]);put('parameter.min_values',[v[0] for _,v,_ in params]);put('parameter.max_values',[v[-1] for _,v,_ in params]);put('parameter.default_values',[d for _,_,d in params]);put('parameter.repeats',[False]*p);put('parameter.decimal_places',[3]*p)
put('parameter.keyform_binding_begin_indices',list(range(p)));put('parameter.keyform_binding_counts',[1]*p)
put('keyform_binding_index.indices',list(range(p)));put('keyform_binding_band.begin_indices',[0]+list(range(p)));put('keyform_binding_band.counts',[0]+[1]*p)
offsets=[];keys=[]
for _,v,_ in params:offsets.append(len(keys));keys+=v
put('keyform_binding.keys_begin_indices',offsets);put('keyform_binding.keys_counts',[len(v) for _,v,_ in params]);put('keys.values',keys)
m.counts[1]=1;m.counts[3]=1;m.counts[8]=3
for e in SECTION_LAYOUT:
 if e.group in ['deformer','rotation_deformer','rotation_deformer_keyform'] and e.elem_type!=ElemType.RUNTIME:m[e.name]=[0]*m.counts[e.count_idx]
put('deformer.ids',['HeadRotation']);put('deformer.keyform_binding_band_indices',[1]);put('deformer.visibles',[True]);put('deformer.enables',[True]);put('deformer.parent_part_indices',[-1]);put('deformer.parent_deformer_indices',[-1]);put('deformer.types',[1]);put('deformer.specific_indices',[0])
put('rotation_deformer.keyform_binding_band_indices',[1]);put('rotation_deformer.keyform_begin_indices',[0]);put('rotation_deformer.keyform_counts',[3]);put('rotation_deformer.base_angles',[0.])
put('rotation_deformer_keyform.opacities',[1.]*3);put('rotation_deformer_keyform.angles',[-10.,0.,10.]);put('rotation_deformer_keyform.origin_xs',[0.]*3);put('rotation_deformer_keyform.origin_ys',[-.16]*3);put('rotation_deformer_keyform.scales',[1.]*3)
band_axes=[[]]+[[i] for i in range(p)]
position=[];begins=[];counts=[];bands=[];opacities=[];orders=[];posbegins=[];parents=[]
for i,l in enumerate(layers):
 name=l['name'];pi=None
 if name.startswith(('EyeMask','EyeClosed')) or name in ['EyeLeft','EyeRight']:pi=1 if name.endswith('Left') else 2
 elif name in ['MouthOpen','MouthLower']:pi=3
 elif name=='Body':pi=4
 elif name=='HairTipsLeft':pi=5
 elif name=='HairTipsRight':pi=12
 elif name=='HairFrontFlow':pi=13
 elif name in ['BrowLeft','BrowRight']:pi=6 if name.endswith('Left') else 7
 vals=[0.] if pi is None else params[pi][1]
 is_head=not name.startswith(('Arm','Coat','Body','Neck','Pendant'))
 axes=([pi] if pi is not None else [])+([8,0] if is_head else [])+([9] if name.startswith('EyeBall') else [])+[10]+([11] if name=='Body' else [])
 if axes not in band_axes:band_axes.append(axes)
 bands.append(band_axes.index(axes));begins.append(len(opacities))
 turn_values=params[8][1] if is_head else [0.]
 gaze_values=params[9][1] if name.startswith('EyeBall') else [0.]
 rot_values=params[0][1] if is_head else [0.]
 shoulder_values=params[11][1] if name=='Body' else [0.]
 forms=[(value,turn,gaze,rotation,body,shoulder) for shoulder in shoulder_values for body in params[10][1] for gaze in gaze_values for rotation in rot_values for turn in turn_values for value in vals]
 counts.append(len(forms));parents.append(-1)
 for value,turn,gaze,rotation,body,shoulder in forms:
  points=list(xy[i*STRIDE:i*STRIDE+NF]);opacity=1.
  if name.startswith('EyeClosed'):
   opacity=(1-value)**.65
   for k in range(1,NF,2):points[k]-=.009*value
  elif pi in [1,2]:
   opacity=min(1.,value*20)
   if name.startswith('EyeMask'):
    for k in range(1,NF,2):
     gx=points[k-1]*1000+543
     u=max(0.,min(1.,(gx-(426 if name.endswith('Left') else 574))/(76 if name.endswith('Left') else 80)))
     gy=(345+9*u+5*math.sin(math.pi*u)) if name.endswith('Left') else (345-13*u+5*math.sin(math.pi*u))
     seam=(gy-724)/1000
     points[k]=seam+(points[k]-seam)*value**1.8
  elif pi==3:
   opacity=min(1.,value/.04) if name=='MouthOpen' else 1.
   for k in range(1,NF,2):
    gx=points[k-1]*1000+543;gy=points[k]*1000+724
    u=max(0.,min(1.,(gx-506)/95))
    seam=float(np.interp(gx,[506,514,537,553,571,590,601],[461,464,462,462,459,457,453]))
    if name=='MouthOpen':gy=seam+(gy-seam)*value
    else:
     taper=max(0.,min(1.,(l['y']+l['h']-gy)/14))
     gy+=14*value*math.sin(math.pi*u)**.9*taper
    points[k]=(gy-724)/1000
  elif pi==4:
   for k in range(1,NF,2):
    v=(k//2//COLS)/(ROWS-1)
    # Anchor neckline and lower torso; lift the chest very slightly.
    points[k]-=.003*value*math.sin(math.pi*v)**2
  elif pi in [5,12,13]:
   for k in range(0,NF,2):
    gy=points[k+1]*1000+724
    v=max(0.,min(1.,(gy-(100 if pi==13 else 160))/(300 if pi==13 else 330)))
    points[k]+=(.007 if pi==13 else .012)*value*v*v
    points[k+1]-=.002*abs(value)*v*v
  elif pi in [6,7]:
   for k in range(1,NF,2):
    u=(k//2%COLS)/(COLS-1)
    points[k]-=.004*value*(.6+.4*math.sin(math.pi*u))
  if name.startswith('EyeBall'):
   for k in range(0,NF,2):points[k]+=.010*gaze
  if is_head and turn:
   angle=math.radians(turn);cs=math.cos(angle);sn=math.sin(angle)
   # Shared smooth depth field: identical source coordinates deform identically
   # across skin, eye apertures, features, and hair, preventing pasted-on features.
   for k in range(0,NF,2):
    px,py=points[k:k+2]
    radial=max(0.,1-(px/.33)**2-((py+.40)/.42)**2)
    depth=.095*math.sqrt(radial)
    depth+=.022*math.exp(-((px/.09)**2+((py+.315)/.09)**2))
    neck_weight=max(0.,min(1.,(558-(py*1000+724))/75))
    neck_weight=neck_weight*neck_weight*(3-2*neck_weight)
    points[k]=px+(px*cs+depth*sn-px)*neck_weight
  if is_head and rotation:
   for k in range(0,NF,2):
    px,py=points[k:k+2]
    weight=max(0.,min(1.,(558-(py*1000+724))/75))
    weight=weight*weight*(3-2*weight)
    angle=math.radians(-rotation)*weight;cs=math.cos(angle);sn=math.sin(angle)
    dx,dy=px,py+.17
    points[k]=dx*cs-dy*sn;points[k+1]=dx*sn+dy*cs-.17
  # Bend the actual torso mesh from the waist; head follows the neckline.
  for k in range(0,NF,2):
   gy=points[k+1]*1000+724
   weight=max(0.,min(1.,(1400-gy)/850))
   points[k]+=.028*body*weight*weight
   if name=='Body':
    shoulder_weight=max(0.,min(1.,(gy-550)/130))*math.exp(-((gy-730)/260)**2)
    points[k+1]-=.010*shoulder*shoulder_weight
  if parents[-1]==0:
   for k in range(1,NF,2):points[k]+=.16
  posbegins.append(len(position));position+=points+[0.]*(STRIDE-NF);opacities.append(opacity);orders.append(float(i))
slot_indices=[];band_starts=[]
for axes in band_axes:
 band_starts.append(len(slot_indices));slot_indices.extend(axes)
m.counts[12]=len(band_axes);m.counts[11]=len(slot_indices);m.counts[13]=p
put('keyform_binding_index.indices',slot_indices)
put('keyform_binding_band.begin_indices',band_starts)
put('keyform_binding_band.counts',[len(a) for a in band_axes])
m.counts[9]=len(opacities);m.counts[10]=len(position)
put('art_mesh.keyform_binding_band_indices',bands);put('art_mesh.keyform_begin_indices',begins);put('art_mesh.keyform_counts',counts);put('art_mesh.parent_deformer_indices',parents)
put('art_mesh_keyform.opacities',opacities);put('art_mesh_keyform.draw_orders',orders);put('art_mesh_keyform.keyform_position_begin_indices',posbegins);put('keyform_position.xys',position)
# Emit Cubism 4.2's complete parameter-key and identity-color tables.
from moc3._core import SectionEntry
extra=[]
for slot in range(101,137):
 typ=ElemType.F32 if slot in list(range(108,114))+[135,136] else ElemType.I32
 extra.append(SectionEntry(f'v42.{slot}',typ,-1,64))
 m[f'v42.{slot}']=[]
extra[1]=SectionEntry('v42.102',ElemType.RUNTIME,5,64)
m.header.version=4;m._build_layout=lambda:list(SECTION_LAYOUT)+extra
colors=len(opacities)+3;m.counts.extend([colors,colors]+[0]*7)
put('v42.103',[len(keys)+o for o in offsets]);put('v42.104',[len(v) for _,v,_ in params])
put('keys.values',keys+keys);m.counts[14]=len(keys)*2
put('v42.106',[0]);put('v42.107',[b+3 for b in begins])
for slot in range(108,111):put(f'v42.{slot}',[1.]*colors)
for slot in range(111,114):put(f'v42.{slot}',[0.]*colors)
put('v42.114',[0]*p);put('v42.115',[0]*p);put('v42.116',[0]*p)
m.to_file(out/'Original.moc3');atlas.save(out/'texture_00.png')
curves=[]
def curve(id,values):
 seg=[0.,values[0]]
 for t,v in enumerate(values[1:],1):seg += [0,float(t),float(v)]
 curves.append({'Target':'Parameter','Id':id,'Segments':seg})
curve('ParamAngleX',[0,0,.25,.4,.4,.4,.25,0,0]);curve('ParamAngleZ',[0,0,.06,.1,.1,.1,.06,0,0]);curve('ParamBreath',[0,.12,.3,.42,.3,.15,.04,0,0])
curve('ParamBodySway',[0,0,.025,.05,.05,.05,.025,0,0])
curve('ParamShoulderLift',[0,.015,.04,.055,.04,.02,.005,0,0])
curve('ParamHairRight',[.04,.05,.06,.065,.06,.05,.035,.03,.04])
curve('ParamHairFront',[.02,.025,.03,.035,.03,.025,.02,.015,.02])
def blink(id):curves.append({'Target':'Parameter','Id':id,'Segments':[0,1,0,2.4,1,0,2.5,0,0,2.65,1,0,6.3,1,0,6.4,0,0,6.55,1,0,8,1]})
blink('ParamEyeLOpen');blink('ParamEyeROpen')
motion={'Version':3,'Meta':{'Duration':8.,'Fps':30.,'Loop':True,'AreBeziersRestricted':True,'CurveCount':len(curves),'TotalSegmentCount':sum((len(c['Segments'])-2)//3 for c in curves),'TotalPointCount':sum(1+(len(c['Segments'])-2)//3 for c in curves),'UserDataCount':0,'TotalUserDataSize':0},'Curves':curves,'UserData':[]}
(out/'idle.motion3.json').write_text(json.dumps(motion,indent=2))
physics={'Version':3,'Meta':{'PhysicsSettingCount':1,'TotalInputCount':1,'TotalOutputCount':1,'VertexCount':2,'Fps':30,'EffectiveForces':{'Gravity':{'X':0,'Y':-1},'Wind':{'X':0,'Y':0}},'PhysicsDictionary':[{'Id':'HairInertia','Name':'Hair inertia'}]},'PhysicsSettings':[{'Id':'HairInertia','Input':[{'Source':{'Target':'Parameter','Id':'ParamAngleZ'},'Weight':100,'Type':'Angle','Reflect':False}],'Output':[{'Destination':{'Target':'Parameter','Id':'ParamHairSwing'},'VertexIndex':1,'Scale':10.0,'Weight':100,'Type':'Angle','Reflect':False}],'Vertices':[{'Position':{'X':0,'Y':0},'Mobility':1,'Delay':1,'Acceleration':1,'Radius':0},{'Position':{'X':0,'Y':8},'Mobility':.85,'Delay':.3,'Acceleration':1.2,'Radius':8}],'Normalization':{'Position':{'Minimum':-10,'Default':0,'Maximum':10},'Angle':{'Minimum':-10,'Default':0,'Maximum':10}}}]}
(out/'Original.physics3.json').write_text(json.dumps(physics,indent=2))
expressions={
 'Calm':{'ParamEyeLOpen':.65,'ParamEyeROpen':.65,'ParamBrowLY':-.25,'ParamBrowRY':-.25,'ParamMouthOpenY':0},
 'Wink':{'ParamEyeLOpen':0,'ParamEyeROpen':1,'ParamBrowLY':.25,'ParamBrowRY':.15,'ParamMouthOpenY':.25,'ParamAngleZ':-4},
 'Surprised':{'ParamEyeLOpen':1,'ParamEyeROpen':1,'ParamBrowLY':1,'ParamBrowRY':1,'ParamMouthOpenY':.7},
}
refs=[]
for name,values in expressions.items():
 filename=name+'.exp3.json'
 (out/filename).write_text(json.dumps({'Type':'Live2D Expression','FadeInTime':.25,'FadeOutTime':.3,'Parameters':[{'Id':id,'Value':v,'Blend':'Overwrite'} for id,v in values.items()]},indent=2))
 refs.append({'Name':name,'File':filename})
(out/'Original.model3.json').write_text(json.dumps({'Version':3,'FileReferences':{'Moc':'Original.moc3','Textures':['texture_00.png'],'DisplayInfo':'Original.cdi3.json','Physics':'Original.physics3.json','Expressions':refs,'Motions':{'Idle':[{'File':'idle.motion3.json','FadeInTime':.5,'FadeOutTime':.5}]}},'Groups':[{'Target':'Parameter','Name':'EyeBlink','Ids':['ParamEyeLOpen','ParamEyeROpen']},{'Target':'Parameter','Name':'LipSync','Ids':['ParamMouthOpenY']}]},indent=2))
(out/'Original.cdi3.json').write_text(json.dumps({'Version':3,'Parameters':[{'Id':id,'GroupId':'','Name':id} for id,_,_ in params],'ParameterGroups':[],'Parts':[]},indent=2))
print(m.summary())

# Browser preview references are versioned independently of the portable model.
import hashlib
preview=json.loads((out/'Original.model3.json').read_text())
for field in ['Moc','Textures']:
 refs=preview['FileReferences'][field]
 def versioned(filename):
  digest=hashlib.sha256((out/filename).read_bytes()).hexdigest()[:16]
  return filename+'?v='+digest
 preview['FileReferences'][field]=[versioned(f) for f in refs] if isinstance(refs,list) else versioned(refs)
(out/'Preview.model3.json').write_text(json.dumps(preview,indent=2))
