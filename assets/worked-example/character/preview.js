(async () => {
  const $ = id => document.getElementById(id);
  try {
    const stage = $('stage');
    const app = new PIXI.Application({view:document.querySelector('canvas'),resizeTo:stage,backgroundAlpha:0,antialias:true,resolution:Math.min(devicePixelRatio,2),autoDensity:true});
    const model = await PIXI.live2d.Live2DModel.from('runtime/Preview.model3.json',{autoInteract:false});
    app.stage.addChild(model);
    // This page supplies its own deliberate idle; avoid layered implicit breathing/focus.
    model.internalModel.updateNaturalMovements=()=>{};
    model.internalModel.updateFocus=()=>{};
    let closeUp=false,showBefore=false;
    $('showBefore').onclick=()=>{showBefore=!showBefore;document.querySelector('.view img').src=showBefore?'Previous-Assembly.png':'Reference.png';$('referenceTitle').textContent=showBefore?'旧版组装图（已替换）':'原始设定';$('showBefore').textContent=showBefore?'对比原始设定':'对比旧版组装图';};
    function fit() {
      model.scale.set(1);
      model.scale.set(Math.min(app.screen.width/1086,app.screen.height/1448)*(closeUp?2.5:1));
      model.position.set((app.screen.width-model.width)/2,closeUp?0:(app.screen.height-model.height)/2);
    }
    fit(); new ResizeObserver(fit).observe(stage);
    $('zoom').onclick=()=>{closeUp=!closeUp;document.querySelector('.view img').style.transform=closeUp?'scale(2.5)':'none';document.querySelector('.view img').style.transformOrigin='50% 0';$('zoom').textContent=closeUp?'恢复全身对比':'面部近景对比';fit();};
    let idle=false, analyser, audio, context, data, blobURL, mouth=0, last=performance.now();
    function stopAudio() {
      if(audio) { audio.pause(); audio.src=''; audio=null; }
      if(context) { context.close();context=null; }
      if(blobURL) { URL.revokeObjectURL(blobURL);blobURL=null; }
      analyser=null; $('mouth').value=0;
      $('audioState').textContent='音频已停止 · 嘴型回到闭合';
    }
    async function playAudio(url) {
      stopAudio();
      try {
        audio=new Audio(url);
        context=new AudioContext(); await context.resume();
        analyser=context.createAnalyser();analyser.fftSize=512;data=new Uint8Array(analyser.fftSize);
        context.createMediaElementSource(audio).connect(analyser);analyser.connect(context.destination);
        audio.onended=stopAudio;
        await audio.play();
      } catch(e) { stopAudio();$('audioState').textContent='音频播放失败：'+e.message; }
    }
    $('sampleAudio').onclick=()=>playAudio('audio-check.wav');
    $('stopAudio').onclick=stopAudio;
    $('localAudio').onchange=async e=>{if(e.target.files[0]){const url=URL.createObjectURL(e.target.files[0]);await playAudio(url);blobURL=url;}};
    $('mouth').oninput=()=>{if(analyser){const v=$('mouth').value;stopAudio();$('mouth').value=v;}};
    let idleStart=performance.now();
    $('idle').onclick=()=>{idle=!idle;if(idle)idleStart=performance.now();$('idle').textContent=idle?'暂停待机':'播放轻微待机';};
    let demoStart=null,audit=null;
    $('demo').onclick=()=>{demoStart=performance.now();audit={frames:0,nonFinite:0,maxVertexStep:0,hairMin:Infinity,hairMax:-Infinity,previous:null};idle=true;idleStart=performance.now();$('idle').textContent='暂停待机';$('wind').value=.2;playAudio('audio-check.wav');};
    const smooth={};
    const springs=[{x:0,v:0},{x:0,v:0},{x:0,v:0}];
    const apply=()=>{
      const now=performance.now(),t=now/1000,dt=Math.min(.1,(now-last)/1000);last=now;
      const c=model.internalModel.coreModel;
      const elapsed=demoStart===null?null:(now-demoStart)/1000;
      if(elapsed!==null&&elapsed>=30){demoStart=null;idle=false;$('reset').click();}
      let target=+$('mouth').value;
      if(analyser) {
        analyser.getByteTimeDomainData(data);
        const rms=Math.sqrt(data.reduce((sum,x)=>sum+((x-128)/128)**2,0)/data.length);
        target=Math.min(.85,Math.max(0,rms-.012)*4.5);
        $('audioState').textContent=`语音 ${audio.currentTime.toFixed(1)} 秒 · 嘴型 ${mouth.toFixed(2)}`;
      }
      const tau=target>mouth?.035:.075;
      mouth+=(target-mouth)*(1-Math.exp(-dt/tau));
      // Hold small, coordinated poses; never continuously rock each body part.
      const it=(now-idleStart)/1000;
      const poses=[0,.07,.035,-.045,0,.04];
      const durations=[12,17,14,19,13,18];
      let phase=((it%93)+93)%93,index=0;
      while(phase>=durations[index])phase-=durations[index++];
      const u=Math.max(0,Math.min(1,phase/3.5));
      const ease=u*u*u*(u*(u*6-15)+10);
      const pose=poses[index]+(poses[(index+1)%poses.length]-poses[index])*ease;
      const breathing=(1-Math.cos(it*2*Math.PI/5.7))/2;
      const blinkTimes=[3.2,8.5,12.3,18.1,22.6,28.4];
      const blinkPhase=it%32;
      let eye=+$('eye').value;
      if(idle){eye=1;for(const start of blinkTimes){const x=blinkPhase-start;if(x>=0&&x<.24)eye=x<.085?1-x/.085:(x-.085)/.155;}}
      const params={ParamAngleZ:idle?pose*2:+$('tilt').value,ParamBreath:idle?breathing*.45:+$('breath').value,ParamMouthOpenY:mouth,ParamEyeLOpen:eye,ParamEyeROpen:eye,ParamAngleX:idle?pose*8:+$('turn').value,ParamBrowLY:+$('brow').value,ParamBrowRY:+$('brow').value,ParamEyeBallX:0,ParamBodySway:idle?pose:+$('body').value,ParamShoulderLift:idle?breathing*.055:+$('shoulder').value};
      for(const [id,value] of Object.entries(params)) {
        const tau=id.includes('Eye')?.025:.12;
        if(smooth[id]===undefined)smooth[id]=value;
        smooth[id]+=(value-smooth[id])*(1-Math.exp(-dt/tau));
        c.setParameterValueById(id,id==='ParamMouthOpenY'?value:smooth[id]);
      }
      const wind=+$('wind').value;
      // Gentle prevailing breeze; no self-feedback from last frame's hair output.
      const gust=wind*(.24+.09*Math.sin(t*.48)+.045*Math.sin(t*.83+.9));
      for(let i=0;i<springs.length;i++){
        const spring=springs[i],target=gust*[1,.8,.5][i]+wind*Math.sin(t*(.52+i*.07)+i*1.7)*.025;
        const stiffness=[16,12,20][i],damping=[8,7,9][i];
        spring.v+=(stiffness*(target-spring.x)-damping*spring.v)*dt;
        spring.x=Math.max(-1,Math.min(1,spring.x+spring.v*dt));
        c.setParameterValueById(['ParamHairSwing','ParamHairRight','ParamHairFront'][i],spring.x);
      }
      const physicalHair=springs[0].x;
      if(audit){audit.hairMin=Math.min(audit.hairMin,physicalHair);audit.hairMax=Math.max(audit.hairMax,physicalHair);}
      $('physicsState').textContent='发丝弹性 · 左 '+springs[0].x.toFixed(2)+' / 右 '+springs[1].x.toFixed(2)+' / 刘海 '+springs[2].x.toFixed(2);
      $('liveValues').textContent=`嘴型 ${mouth.toFixed(2)} · 眼睛 ${eye.toFixed(2)} · 重心 ${smooth.ParamBodySway.toFixed(2)} · 肩部 ${smooth.ParamShoulderLift.toFixed(2)}`;
    };
    model.internalModel.on('afterMotionUpdate',apply);model.internalModel.on('beforeModelUpdate',apply);
    $('reset').onclick=()=>{idle=false;demoStart=null;stopAudio();$('idle').textContent='播放轻微待机';$('tilt').value=0;$('turn').value=0;$('brow').value=0;$('body').value=0;$('shoulder').value=0;$('wind').value=0;for(const s of springs){s.x=0;s.v=0;}$('breath').value=0;$('eye').value=1;$('mouth').value=0;};
    app.ticker.add(()=>{
      if(!audit)return;
      const c=model.internalModel.coreModel,positions=[];
      for(let i=0;i<c.getDrawableCount();i++)positions.push(...c.getDrawableVertexPositions(i));
      for(let i=0;i<positions.length;i++){
        if(!Number.isFinite(positions[i]))audit.nonFinite++;
        if(audit.previous)audit.maxVertexStep=Math.max(audit.maxVertexStep,Math.abs(positions[i]-audit.previous[i])*1000);
      }
      audit.previous=positions;audit.frames++;
      // Physics values are captured before Core restores its saved parameter array.
      $('auditState').textContent=`${demoStart===null?'检查结束':'组合播放中'} · ${audit.frames}帧 · 非有限坐标${audit.nonFinite} · 最大帧位移${audit.maxVertexStep.toFixed(2)}px · 头发参数${audit.hairMin.toFixed(2)}～${audit.hairMax.toFixed(2)}`;
      if(demoStart===null)audit=null;
    });
    $('status').textContent='官方 Cubism Core 已加载 · '+model.internalModel.coreModel.getDrawableCount()+' 个网格';
  }catch(e){$('status').textContent='加载失败：'+e.message;}
})();
