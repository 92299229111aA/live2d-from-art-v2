const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
global.require=require;global.__dirname=__dirname;
vm.runInThisContext(fs.readFileSync(path.join(__dirname,'vendor/live2dcubismcore.min.js'),'utf8'));
setTimeout(()=>{
 const C=Live2DCubismCore,data=fs.readFileSync(path.join(__dirname,'runtime/Original.moc3'));
 const moc=C.Moc.fromArrayBuffer(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength));assert(moc);
 const m=C.Model.fromMoc(moc);assert(m);const d=m.drawables,p=m.parameters,checks=[];
 const reset=()=>{p.values.set(p.defaultValues);m.update();};
 const set=(id,v)=>{const i=p.ids.indexOf(id);assert(i>=0);p.values[i]=v;m.update();};
 const positions=id=>Array.from(d.vertexPositions[d.ids.indexOf(id)]);
 const same=(a,b)=>a.every((v,i)=>Math.abs(v-b[i])<1e-6);
 assert.equal(d.count,23);reset();
 for(const side of ['Left','Right']){
  const eye=positions('Eye'+side),other=positions('Eye'+(side==='Left'?'Right':'Left'));
  set(side==='Left'?'ParamEyeLOpen':'ParamEyeROpen',.5);
  assert(same(eye,positions('Eye'+side)));assert(same(other,positions('Eye'+(side==='Left'?'Right':'Left'))));
  const i=d.ids.indexOf('Eye'+side);assert.equal(d.maskCounts[i],1);assert.equal(d.masks[i][0],d.ids.indexOf('EyeMask'+side));
  set(side==='Left'?'ParamEyeLOpen':'ParamEyeROpen',0);assert(d.opacities[i]<.01);assert(d.opacities[d.ids.indexOf('EyeClosed'+side)]>.99);reset();
 }
 checks.push('Both eyes use independent masks; source eye geometry stays unchanged while blinking; closed-eye line appears.');
 const upper=positions('MouthUpper'),lower=positions('MouthLower');set('ParamMouthOpenY',1);assert(same(upper,positions('MouthUpper')));assert(!same(lower,positions('MouthLower')));assert(d.opacities[d.ids.indexOf('MouthOpen')]>.99);checks.push('Upper lip stays fixed, lower lip deforms, oral cavity opens.');
 reset();const body=positions('Body'),face=positions('Face');set('ParamAngleX',8);set('ParamAngleZ',5);assert(same(body,positions('Body')));assert(!same(face,positions('Face')));checks.push('Head turn/tilt deform the head without moving the collar/body.');
 reset();const hair=positions('HairTipsLeft');set('ParamHairSwing',1);const shifted=positions('HairTipsLeft');assert(!same(hair,shifted));assert(Math.abs(hair[0]-shifted[0])<1e-6);checks.push('Side-hair tips deform while roots remain fixed.');
 reset();const right=positions('BrowRight'),left=positions('BrowLeft');set('ParamBrowLY',1);assert(same(right,positions('BrowRight')));assert(!same(left,positions('BrowLeft')));checks.push('Eyebrows move independently.');
 reset();const torso0=positions('Body'),face0=positions('Face');set('ParamBodySway',1);
 const torso1=positions('Body');assert(!same(torso0,torso1));assert(!same(face0,positions('Face')));assert(Math.abs(torso0[torso0.length-2]-torso1[torso1.length-2])<1e-6);
 checks.push('Body sway bends torso and carries head; lower canvas/waist stays anchored.');
 reset();const faceStill=positions('Face');set('ParamShoulderLift',1);assert(!same(torso0,positions('Body')));assert(same(faceStill,positions('Face')));checks.push('Shoulders deform independently without dragging the face.');
 for(const [param,mesh]of [['ParamHairSwing','HairTipsLeft'],['ParamHairRight','HairTipsRight'],['ParamHairFront','HairFrontFlow']]){
  reset();const before=positions(mesh),others=['HairTipsLeft','HairTipsRight','HairFrontFlow'].filter(n=>n!==mesh).map(n=>[n,positions(n)]);set(param,1);assert(!same(before,positions(mesh)));for(const[n,xy]of others)assert(same(xy,positions(n)));assert(Math.abs(before[0]-positions(mesh)[0])<1e-6);
 }
 checks.push('Left, right and front hair groups deform independently with fixed roots.');
 for(const body of[-1,1])for(const shoulder of[-1,1])for(const wind of[-1,1]){
  reset();for(const[id,v]of Object.entries({ParamBodySway:body,ParamShoulderLift:shoulder,ParamHairSwing:wind,ParamHairRight:-wind,ParamHairFront:wind,ParamAngleX:8,ParamAngleZ:5,ParamEyeLOpen:.2,ParamMouthOpenY:.7}))set(id,v);
  for(const xy of d.vertexPositions)assert(Array.from(xy).every(Number.isFinite));
 }
 checks.push('Body/shoulder/wind extremes combine with face motion without invalid geometry.');
 let combinations=0;
 for(const turn of [-8,0,8])for(const tilt of[-5,0,5])for(const eye of[0,.5,1])for(const mouth of[0,.5,1]){
  reset();set('ParamAngleX',turn);set('ParamAngleZ',tilt);set('ParamEyeLOpen',eye);set('ParamEyeROpen',eye);set('ParamMouthOpenY',mouth);
  for(const xy of d.vertexPositions)assert(Array.from(xy).every(Number.isFinite));combinations++;
 }
 checks.push(combinations+' turn/tilt/eye/mouth combinations have finite geometry.');
 const runtime=path.join(__dirname,'runtime'),settings=JSON.parse(fs.readFileSync(path.join(runtime,'Original.model3.json'))),r=settings.FileReferences;
 const files=[r.Moc,r.Physics,r.DisplayInfo,...r.Textures,...r.Expressions.map(e=>e.File),...Object.values(r.Motions).flat().map(e=>e.File)];
 for(const f of files)assert(fs.existsSync(path.join(runtime,f)));
 for(const e of r.Expressions){const exp=JSON.parse(fs.readFileSync(path.join(runtime,e.File)));for(const q of exp.Parameters){const i=p.ids.indexOf(q.Id);assert(i>=0&&q.Value>=p.minimumValues[i]&&q.Value<=p.maximumValues[i]);}}
 checks.push('Portable model references and expression parameter ranges resolve.');
 const report={status:'PASS',scope:'Core structural and behavioral checks; NOT a visual-quality verdict',coreVersion:C.Version.csmGetVersion(),meshes:d.count,combinations,checks};
 fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));m.release();moc._release();
},1000);
