/* Display-only state. No serial, radio, CAT or connection writes. */
(function(){
'use strict';
const ranges=[5,10,25,50,100,250,500,1000,1500,3000,5000,10000];
class DisplayModel{
 constructor(){this.peak=0;this.peakAt=0;this.frame=-1;this.forwardRange=0;this.reflectedRange=0;this.rangeAt={};}
 reset(){this.peak=0;this.peakAt=0;this.frame=-1;}
 sample(d,now,hold){
  const live=d.status==='Live'&&typeof d.age==='number'&&d.age>=0&&d.age<2;
  if(!live){this.reset();return {live:false,forward:0,reflected:0,swr:null,peak:null};}
  const [forward,reflected,swr]=d.values;
  if(d.frames!==this.frame){
   if(forward>=this.peak||hold===0||(hold>0&&now-this.peakAt>=hold*1000)){this.peak=forward;this.peakAt=now;}
   this.frame=d.frames;
  }
  return {live:true,forward,reflected,swr:forward>0&&swr>=1?swr:null,peak:hold===0?null:this.peak};
 }
 scale(which,value,selected,now){
  if(selected!=='auto')return Number(selected);
  const key=which+'Range',desired=ranges.find(r=>r>=value*1.12)||ranges[ranges.length-1];
  if(!this[key]||desired>this[key]){this[key]=desired;this.rangeAt[which]=now;}
  else if(desired<this[key]){if(now-this.rangeAt[which]>=5000){this[key]=desired;this.rangeAt[which]=now;}}
  else this.rangeAt[which]=now;
  return this[key];
 }
}
if(typeof module!=='undefined')module.exports={DisplayModel,ranges};
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),model=new DisplayModel();
const defaults={profile:'modern',scale:'auto',refScale:'auto',hold:'2',callsign:'',compact:false,top:false,warn:'2.0',alarm:'3.0'};
let prefs={...defaults};
try{const saved=JSON.parse(localStorage.getItem('pm-display-v2')||'null');if(saved)prefs={...prefs,...saved};else{
 for(const id of ['scale','refScale','warn','alarm']){const v=localStorage.getItem('pm-led-'+id);if(v)prefs[id]=v;}
 if(localStorage.getItem('pm-led-peakOn')==='false')prefs.hold='0';
}}catch{}
if(!['modern','console','daylight'].includes(prefs.profile))prefs.profile='modern';
for(const id of ['scale','refScale'])if(prefs[id]!=='auto'&&!ranges.includes(Number(prefs[id])))prefs[id]='auto';
if(!['0','2','5','10','-1'].includes(String(prefs.hold)))prefs.hold='2';
prefs.callsign=String(prefs.callsign).slice(0,24);prefs.compact=prefs.compact===true;prefs.top=prefs.top===true;
prefs.warn=Math.min(4.8,Math.max(1.1,Number(prefs.warn)||2)).toFixed(1);prefs.alarm=Math.min(5,Math.max(Number(prefs.warn)+.1,Number(prefs.alarm)||3)).toFixed(1);
let lastData=null,connectionInitialized=false,refreshRequested=true,requestBusy=false;
const native=window.webkit?.messageHandlers?.displayWindow;
function save(){try{localStorage.setItem('pm-display-v2',JSON.stringify(prefs));}catch{}}
function applyPrefs(){
 document.documentElement.dataset.profile=prefs.profile;document.body.classList.toggle('compact',prefs.compact);
 for(const id of ['profile','scale','refScale','hold','callsign','warn','alarm'])$(id).value=prefs[id];
 $('stayTop').checked=prefs.top;$('stayTop').disabled=!native;$('stayTopLabel').title=native?'Keep this window above other applications':'Stay on top is available in the Mac app';
 $('compact').textContent=prefs.compact?'Expand':'Compact';$('compact').setAttribute('aria-pressed',String(prefs.compact));
 $('stationLabel').textContent='RF power & standing wave ratio';$('operatorCallsign').textContent=prefs.callsign;$('operatorCallsign').hidden=!prefs.callsign;
 native?.postMessage({compact:prefs.compact,alwaysOnTop:prefs.top});
 if(lastData)paint(lastData);
}
for(const id of ['profile','scale','refScale','hold','callsign','warn','alarm'])$(id).onchange=()=>{prefs[id]=$(id).value;if(['warn','alarm'].includes(id)){prefs.warn=Math.min(4.8,Math.max(1.1,Number(prefs.warn)||2)).toFixed(1);prefs.alarm=Math.min(5,Math.max(Number(prefs.warn)+.1,Number(prefs.alarm)||3)).toFixed(1);}if(id==='callsign')prefs[id]=prefs[id].trim().toUpperCase().slice(0,24);if(id==='hold')model.reset();save();applyPrefs();};
$('compact').onclick=()=>{prefs.compact=!prefs.compact;save();applyPrefs();};
$('stayTop').onchange=()=>{prefs.top=$('stayTop').checked;save();applyPrefs();};
$('displaySettings').onclick=()=>$('displayDialog').showModal();$('closeDisplay').onclick=()=>$('displayDialog').close();
$('reset').onclick=()=>{model.reset();if(lastData)paint(lastData);$('peakNotice').textContent='Peak reset';};
for(const id of ['forwardBar','refBar','swrBar'])for(let i=0;i<50;i++){const el=document.createElement('i');el.className='led';$(id).append(el);}
function connectionControls(d){
 if(!connectionInitialized||refreshRequested){
  const selected=connectionInitialized?$('serialPort').value:d.port;
  const choices=[...new Set([...(d.ports||[]),...(selected?[selected]:[])])];
  $('serialPort').replaceChildren(...['',...choices].map(p=>{const o=document.createElement('option');o.value=p;o.textContent=p||'Select port…';return o;}));
  $('serialPort').value=selected||'';if(!connectionInitialized)$('baud').value=String(d.baud||38400);
  $('shareReadings').checked=d.share_readings===true;connectionInitialized=true;refreshRequested=false;
 }
 $('disconnectMeter').disabled=!d.connected;
}
async function connectionAction(action){
 $('connectMeter').disabled=true;$('disconnectMeter').disabled=true;
 try{
  const token=location.pathname.split('/')[1];const response=await fetch('connection',{method:'POST',headers:{'Content-Type':'application/json','X-Meter-Token':token},body:JSON.stringify({action,port:$('serialPort').value,baud:Number($('baud').value),enabled:$('shareReadings').checked})});
  const d=await response.json();if(!response.ok)throw Error(d.error);model.reset();lastData=d;paint(d);
  $('connectionHelp').textContent=action==='sharing'?(d.share_readings?'Sharing enabled on this Mac.':'Sharing disabled.'):action==='connect'?'Connection settings saved. Baud must match the meter.':'Disconnected. Click Connect to resume.';
 }catch(e){$('connectionHelp').textContent=String(e);connectionInitialized=false;}finally{$('connectMeter').disabled=false;}
}
$('shareReadings').onchange=()=>connectionAction('sharing');$('connectMeter').onclick=()=>connectionAction('connect');$('disconnectMeter').onclick=()=>connectionAction('disconnect');$('refreshPorts').onclick=()=>{refreshRequested=true;};
function ticks(id,max,base=0){$(id).replaceChildren(...[0,.25,.5,.75,1].map(n=>{const s=document.createElement('span');s.textContent=(base+n*max).toLocaleString(undefined,{maximumFractionDigits:1});return s;}));}
function bar(id,value,max,mark,valid,type){
 const fraction=Math.min(1,Math.max(0,value/max)),count=valid?Math.ceil(fraction*50):0;
 $(id).style.setProperty('--fill',(valid?fraction*100:0)+'%');
 $(id).setAttribute('aria-valuenow',valid?String(value):'0');$(id).setAttribute('aria-valuemax',String(max));$(id).setAttribute('aria-valuetext',valid?value.toFixed(2)+(type==='swr'?' above 1:1':' watts'):'No live reading');
 [...$(id).children].forEach((el,i)=>{const position=i/49;const color=type==='swr'?(1+position*4>=Number(prefs.alarm)?'var(--red)':1+position*4>=Number(prefs.warn)?'var(--amber)':'var(--mint)'):type==='ref'?'var(--amber)':position>=.9?'var(--amber)':'var(--mint)';el.style.setProperty('--color',color);el.removeAttribute('title');el.className='led'+(i<count?' on':'')+(valid&&mark>0&&i===Math.min(49,Math.ceil(mark/max*50)-1)?' peak':'');});
 const marker=$(id).querySelector('.peak');if(marker)marker.title='Held peak '+mark.toFixed(2)+' W';
}
function paint(d){
 connectionControls(d);const now=performance.now(),v=model.sample(d,now,Number(prefs.hold));
 document.body.classList.toggle('stale',!v.live);$('status').textContent=d.demo?'DEMO':v.live?'LIVE':d.status==='Live'?'STALE':d.status.toUpperCase();
 $('badge').dataset.live=String(v.live);$('fwd').textContent=v.live?v.forward.toFixed(2):'—';$('ref').textContent=v.live?v.reflected.toFixed(2):'—';$('swr').textContent=v.swr===null?'—':v.swr.toFixed(2);
 $('swr').dataset.level=v.swr===null?'none':v.swr>=Number(prefs.alarm)?'alarm':v.swr>=Number(prefs.warn)?'warn':'good';
 $('swrHint').textContent=v.swr===null?(v.live?'No RF':'Waiting'):v.swr>=Number(prefs.alarm)?'High SWR':v.swr>=Number(prefs.warn)?'Elevated SWR':'Valid RF';
 $('peaktext').textContent=!v.live?'Peak —':v.peak===null?'Peak hold off':'Peak '+v.peak.toFixed(2)+' W';
 const fmax=model.scale('forward',Math.max(v.forward,v.peak||0),prefs.scale,now),rmax=model.scale('reflected',v.reflected,prefs.refScale,now);
 bar('forwardBar',v.forward,fmax,v.peak||0,v.live,'fwd');bar('refBar',v.reflected,rmax,0,v.live,'ref');bar('swrBar',Math.max(0,(v.swr||1)-1),4,0,v.swr!==null,'swr');
 ticks('forwardTicks',fmax);ticks('refTicks',rmax);ticks('swrTicks',4,1);
 $('forwardRange').textContent=(prefs.scale==='auto'?'Auto · ':'')+fmax.toLocaleString()+' W';$('refRange').textContent=(prefs.refScale==='auto'?'Auto · ':'')+rmax.toLocaleString()+' W';
 $('port').textContent=(d.port||'USB')+' · '+(d.baud||38400)+' 8N1';$('age').textContent=d.age===null?'Waiting for data':d.age.toFixed(1)+'s since last reading';
 $('notice').textContent=!v.live?d.notice||'Waiting for valid readings':v.forward>fmax?'Forward reading exceeds selected bar scale':v.reflected>rmax?'Reflected reading exceeds selected bar scale':'';
 $('diag').textContent=JSON.stringify(d,null,2);
}
async function update(){
 if(requestBusy)return;requestBusy=true;
 try{const response=await fetch('state',{cache:'no-store'});if(!response.ok)throw Error('Reader unavailable');lastData=await response.json();paint(lastData);}
 catch(e){lastData={status:'Disconnected',age:null,values:[0,0,0],port:'USB reader unavailable',notice:String(e),demo:false};paint(lastData);}
 finally{requestBusy=false;setTimeout(update,200);}
}
applyPrefs();update();
})();
