import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {GTAOPass} from 'three/addons/postprocessing/GTAOPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
const GLB_B64="__GLB__";
function track(e){(window.dataLayer=window.dataLayer||[]).push({event:'flat3d_'+e});if(window.ym&&window.YM_ID)ym(window.YM_ID,'reachGoal','flat3d_'+e);}
window.__track=track;
window.__boot3d=()=>{


const $=id=>document.getElementById(id);
const cv=$('c'),stage=$('stage'),overlay=$('overlay');
const mobile=matchMedia('(max-width:860px)').matches;
const renderer=new THREE.WebGLRenderer({canvas:cv,antialias:false,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,mobile?1.5:2));
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene();
{const c=document.createElement('canvas');c.width=c.height=512;const g=c.getContext('2d');const gr=g.createRadialGradient(256,180,10,256,256,420);gr.addColorStop(0,'#fbfaf7');gr.addColorStop(.6,'#efebe4');gr.addColorStop(1,'#e2dbd0');g.fillStyle=gr;g.fillRect(0,0,512,512);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;scene.background=t;}
scene.environment=new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(renderer),0.04).texture;
const camera=new THREE.PerspectiveCamera(32,1,0.1,200);
scene.add(new THREE.HemisphereLight(0xfff6ea,0xc9b9a2,1.1));
const sun=new THREE.DirectionalLight(0xfff0dc,3.0);sun.castShadow=true;
sun.shadow.mapSize.set(mobile?1024:2048,mobile?1024:2048);Object.assign(sun.shadow.camera,{left:-6.5,right:6.5,top:6.5,bottom:-6.5,near:1,far:40});
sun.shadow.bias=-.0003;sun.shadow.normalBias=.02;sun.position.set(12.6,11,-5.3);sun.target.position.set(4,0,1.7);scene.add(sun,sun.target);
const fill=new THREE.DirectionalLight(0xe8eef5,.7);fill.position.set(-8,6,6);scene.add(fill);

const W=()=>stage.clientWidth,Hh=()=>stage.clientHeight;
const rt=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:mobile?2:4});
const composer=new EffectComposer(renderer,rt);
composer.addPass(new RenderPass(scene,camera));
const gtao=new GTAOPass(scene,camera,1,1);
gtao.updateGtaoMaterial({radius:.4,distanceExponent:1.4,thickness:1.4,scale:1.15,samples:mobile?8:16,distanceFallOff:1});
gtao.updatePdMaterial({lumaPhi:10,depthPhi:2,normalPhi:3,radius:5,rings:2,samples:mobile?8:16});
gtao.setSceneClipBox(new THREE.Box3(new THREE.Vector3(-.18,-.06,-.28),new THREE.Vector3(8.15,2.8,3.61)));gtao.blendIntensity=1;composer.addPass(gtao);composer.addPass(new OutputPass());

function canvasTex(draw,w,h){const c=document.createElement('canvas');c.width=w;c.height=h||w;draw(c.getContext('2d'),c.width,c.height);const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=renderer.capabilities.getMaxAnisotropy();return t;}
let seed=5;const rnd=()=>{seed=(seed*16807)%2147483647;return (seed-1)/2147483646;};
const lam=canvasTex((g,w)=>{const rows=6,rh=w/rows;for(let r=0;r<rows;r++){let x=-rnd()*w;while(x<w){const len=w*(.55+rnd()*.45);const l=56+rnd()*8,s=30+rnd()*10,hh=29+rnd()*5;g.fillStyle=`hsl(${hh},${s}%,${l}%)`;g.fillRect(x,r*rh,len,rh);for(let i=0;i<16;i++){g.strokeStyle=`rgba(95,60,30,${.03+rnd()*.05})`;g.lineWidth=.6+rnd();g.beginPath();const y=r*rh+rnd()*rh;g.moveTo(x,y);g.bezierCurveTo(x+len*.3,y+rnd()*4-2,x+len*.6,y+rnd()*4-2,x+len,y+rnd()*2-1);g.stroke();}if(rnd()<.35){g.fillStyle='rgba(90,55,25,.12)';g.beginPath();g.ellipse(x+len*rnd(),r*rh+rh*rnd(),6+rnd()*6,2,0,0,7);g.fill();}g.fillStyle='rgba(55,32,15,.32)';g.fillRect(x,r*rh,1.2,rh);x+=len;}g.fillStyle='rgba(55,32,15,.28)';g.fillRect(0,r*rh,w,1.2);}},1024);
function tiles(base,line,n,size){return canvasTex((g,w)=>{g.fillStyle=base;g.fillRect(0,0,w,w);for(let i=0;i<n;i++)for(let j=0;j<n;j++){g.fillStyle=`rgba(${rnd()<.5?0:255},${rnd()<.5?0:255},0,${rnd()*.025})`;g.fillRect(i*w/n,j*w/n,w/n,w/n);for(let k=0;k<30;k++){g.fillStyle=`rgba(0,0,0,${rnd()*.03})`;g.fillRect(i*w/n+rnd()*w/n,j*w/n+rnd()*w/n,2,2);}}g.strokeStyle=line;g.lineWidth=2.5;for(let i=0;i<=n;i++){g.beginPath();g.moveTo(i*w/n,0);g.lineTo(i*w/n,w);g.stroke();g.beginPath();g.moveTo(0,i*w/n);g.lineTo(w,i*w/n);g.stroke();}},size||512);}
const TEX={Laminate:[lam,1.6],Floor_Hall:[tiles('#d8d2c7','#b9b1a4',2),1.2],Tile_Bath:[tiles('#e2e6e5','#c1c9c8',4),1.2],Tile_Wall:[tiles('#e8ecec','#cdd5d5',5),1.2],Loggia_Floor:[tiles('#c6bfb3','#a9a295',3),1.2]};
function planarUV(geo,scale){const p=geo.attributes.position,n=geo.attributes.normal,uv=new Float32Array(p.count*2);for(let i=0;i<p.count;i++){const nx=Math.abs(n.getX(i)),ny=Math.abs(n.getY(i));let u,v;if(ny>.5){u=p.getX(i);v=p.getZ(i);}else if(nx>.5){u=p.getZ(i);v=p.getY(i);}else{u=p.getX(i);v=p.getY(i);}uv[i*2]=u/scale;uv[i*2+1]=v/scale;}geo.setAttribute('uv',new THREE.BufferAttribute(uv,2));}
function bake(o){const g=o.geometry,m=o.matrixWorld,nm=new THREE.Matrix3().getNormalMatrix(m);const p=g.attributes.position,n=g.attributes.normal;const P=new Float32Array(p.count*3),Nn=n?new Float32Array(n.count*3):null;const v=new THREE.Vector3();for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m);P.set([v.x,v.y,v.z],i*3);if(n){v.fromBufferAttribute(n,i).applyMatrix3(nm).normalize();Nn.set([v.x,v.y,v.z],i*3);}}
const ng=new THREE.BufferGeometry();ng.setAttribute('position',new THREE.BufferAttribute(P,3));if(Nn)ng.setAttribute('normal',new THREE.BufferAttribute(Nn,3));if(g.index)ng.setIndex(g.index.clone());o.geometry=ng;o.position.set(0,0,0);o.quaternion.identity();o.scale.set(1,1,1);o.updateMatrix();o.updateMatrixWorld(true);}

const CUT=1.25;
function clampMesh(o){const g=o.geometry;g.computeBoundingBox();const bb=g.boundingBox;if(bb.min.y>=CUT-.005){o.visible=false;o.userData.cut=true;return false;}if(bb.max.y>CUT){const p=g.attributes.position;for(let i=0;i<p.count;i++)if(p.getY(i)>CUT)p.setY(i,CUT);p.needsUpdate=true;g.computeBoundingBox();g.computeBoundingSphere();}return true;}
const capMat=new THREE.MeshBasicMaterial({color:new THREE.Color(0x3d3a36)});
const ITEMS=[['Kitchen','Кухонный гарнитур','Фасады, столешница, подсветка'],['Sink','Мойка','Нержавеющая сталь'],['Faucet','Смеситель','С поворотным изливом'],['Cooktop','Варочная поверхность','Индукционная, 4 конфорки'],['Hood','Вытяжка','Встраивается в гарнитур'],['Fridge','Холодильник','Двухкамерный'],['Table','Обеденный стол','Круглый, на 2–3 человек'],['Chair','Стул','2 шт.'],['TV_Unit','Тумба под ТВ','С ящиками'],['TV','Телевизор','На стене над тумбой'],['Wardrobe','Шкаф','Распашной, 3 секции'],['Sofa','Диван','С мягкими подушками'],['Hook','Панель с крючками','В прихожей'],['Rod','Карниз',''],['Curtain','Шторы','Плотные, светлый лён'],['Tulle','Тюль','Лёгкий, пропускает свет']];
function itemOf(name){const k=name.replace(/^F_/,'');for(const it of ITEMS)if(k.startsWith(it[0]))return it;return null;}
const furniture=[],walls=[],pickF=[],decals=[];const items={};let tvMat=null;

const raw=atob(GLB_B64),buf=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)buf[i]=raw.charCodeAt(i);
const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
loader.parse(buf.buffer,'',gltf=>{
const root=gltf.scene;scene.add(root);root.updateMatrixWorld(true);
const meshes=[];root.traverse(o=>{if(o.isMesh)meshes.push(o);});
meshes.forEach(o=>{
 const isF=o.name.startsWith('F_');let m=o.material;
 o.castShadow=!/Glass|Tulle|Floor|LED|Screen/.test(o.name+m.name);o.receiveShadow=true;
 bake(o);
 if(isF){m=o.material=m.clone();const it=itemOf(o.name);if(it){(items[it[1]]=items[it[1]]||[]).push(o);o.userData.item=it;pickF.push(o);}furniture.push(o);o.userData.y0=0;}
 m.envMapIntensity=.55;
 if(TEX[m.name]){planarUV(o.geometry,TEX[m.name][1]);m.map=TEX[m.name][0];m.color.set(0xffffff);m.needsUpdate=true;}
 if(m.name==='Wall'){const g=o.geometry;g.computeBoundingBox();const bb=g.boundingBox;
  if(bb.min.y>=CUT-.01){o.visible=false;return;}
  if(bb.max.y>CUT){const p=g.attributes.position;for(let i=0;i<p.count;i++)if(p.getY(i)>CUT)p.setY(i,CUT);p.needsUpdate=true;}
  const top=Math.min(bb.max.y,CUT);const cap=new THREE.Mesh(new THREE.BoxGeometry(bb.max.x-bb.min.x+.003,.012,bb.max.z-bb.min.z+.003),capMat);cap.position.set((bb.max.x+bb.min.x)/2,top+.006,(bb.max.z+bb.min.z)/2);o.add(cap);walls.push(o);
  m.color.set(0xf4f0ea);m.roughness=.95;}
 else if((!isF&&!/^Laminate|Floor|Tile_Bath|Loggia/.test(m.name))||/Curtain|Tulle|Rod/.test(o.name)){if(!clampMesh(o))return;}
 if(/Curtain|Tulle/.test(o.name))m.side=THREE.DoubleSide;
 if(m.name==='Glass'){m.transparent=true;m.opacity=.14;m.depthWrite=false;m.roughness=.02;}
 if(m.name==='Tulle'){m.transparent=true;m.opacity=.55;m.depthWrite=false;}
 if(m.name==='Mirror'||m.name==='Chrome'){m.envMapIntensity=1.2;}
 if(m.name==='Door_Entry'){m.color.set(0x8a827a);}
 if(m.name==='LED'){m.emissive=new THREE.Color(0xffd9a0);m.emissiveIntensity=2.2;}
 if(m.name==='TV_Screen'){tvMat=m;const t=canvasTex((g,w,h)=>{const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#f6b56b');gr.addColorStop(.5,'#e07a5f');gr.addColorStop(1,'#3d405b');g.fillStyle=gr;g.fillRect(0,0,w,h);g.fillStyle='#ffe8b0';g.beginPath();g.arc(w*.62,h*.52,h*.13,0,7);g.fill();g.fillStyle='#2b2d42';g.beginPath();g.moveTo(0,h);g.lineTo(w*.18,h*.66);g.lineTo(w*.36,h*.8);g.lineTo(w*.58,h*.58);g.lineTo(w*.8,h*.74);g.lineTo(w,h*.62);g.lineTo(w,h);g.fill();},512,288);t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping;m.map=t;m.emissiveMap=t;m.emissive=new THREE.Color(0xffffff);m.emissiveIntensity=.55;m.color.set(0x222222);const g=o.geometry,p=g.attributes.position,uvA=new Float32Array(p.count*2),wv=new THREE.Vector3();for(let i=0;i<p.count;i++){wv.fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);uvA[i*2]=1-(wv.x-4.64)/1.12;uvA[i*2+1]=(wv.y-.84)/.62;}g.setAttribute('uv',new THREE.BufferAttribute(uvA,2));}
});
const slab=new THREE.Mesh(new THREE.BoxGeometry(9.0,.3,4.45),new THREE.MeshStandardMaterial({color:0xd9d2c6,roughness:.95,envMapIntensity:.5}));slab.position.set(3.98,-.2,1.67);slab.receiveShadow=true;slab.castShadow=true;scene.add(slab);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(80,80),new THREE.ShadowMaterial({opacity:.16}));ground.rotation.x=-Math.PI/2;ground.position.y=-.351;ground.receiveShadow=true;scene.add(ground);
const blob=new THREE.Mesh(new THREE.PlaneGeometry(13,7.5),new THREE.MeshBasicMaterial({map:canvasTex((g,w,h)=>{const gr=g.createRadialGradient(w/2,h/2,0,w/2,h/2,w/2);gr.addColorStop(0,'rgba(60,45,30,.28)');gr.addColorStop(.55,'rgba(60,45,30,.12)');gr.addColorStop(1,'rgba(60,45,30,0)');g.fillStyle=gr;g.fillRect(0,0,w,h);},256),transparent:true,depthWrite:false}));blob.rotation.x=-Math.PI/2;blob.position.set(3.98,-.35,1.67);scene.add(blob);
buildDims();setMode('empty',true);intro();
$('loading').style.opacity=0;setTimeout(()=>$('loading').remove(),700);
},e=>{$('loading').textContent='Не удалось загрузить модель';console.error(e);});

/* зоны с площадями на полу */
const ZONES=[['Кухня-гостиная','15,26 м²',4.55,1.75],['Санузел','3,12 м²',1.45,1.25],['Прихожая','3,01 м²',.95,2.55],['Лоджия','4,24 м²',7.45,1.75]];
const zoneEls=ZONES.map(z=>{const d=document.createElement('div');d.className='zone';d.innerHTML=`<span>${z[0]}</span><b>${z[1]}</b>`;overlay.appendChild(d);return d;});
/* точки отделки */
const PINS=[
{k:'Отделка',t:'Пол — ламинат',p:'Износостойкий ламинат 33 класса в тёплом дубовом оттенке. Единое покрытие кухни-гостиной без порогов.',c:['33 класс','Без порогов','Плинтус в цвет стен'],pos:[5.5,.03,2.95]},
{k:'Отделка',t:'Стены под покраску',p:'Выровненные стены, финишная окраска в светлом тёплом тоне. Освежить цвет можно без ремонта.',c:['Моющаяся краска','Тёплый белый'],pos:[3.15,.95,.02]},
{k:'Окна',t:'Окна ПВХ с подоконником',p:'Двухкамерный стеклопакет, поворотно-откидные створки, широкий подоконник.',c:['2-камерный','Микропроветривание'],pos:[5.35,1.05,-.02]},
{k:'Санузел',t:'Санузел под ключ',p:'Керамогранит на полу и в зоне душа. Душевой поддон со стеклом, унитаз, тумба с раковиной и зеркалом, полотенцесушитель.',c:['Керамогранит','Сантехника','Полотенцесушитель'],pos:[.46,.75,.46]},
{k:'Безопасность',t:'Входная дверь',p:'Металлическая утеплённая дверь с двумя замками и глазком.',c:['Утеплённая','2 замка'],pos:[.42,.05,2.4]},
{k:'Лоджия',t:'Остеклённая лоджия, 4,24 м²',p:'Выход из жилой зоны. Хватит места для кресла и столика или мини-кабинета.',c:['Остекление','Выход из комнаты'],pos:[7.45,.55,.45]}];
const pinEls=PINS.map((p,i)=>{const b=document.createElement('button');b.className='pin';b.innerHTML='<i></i>';b.setAttribute('aria-label',p.t);b.onclick=e=>{e.stopPropagation();openInfo(i);};overlay.appendChild(b);return b;});
let openPin=-1;
function openInfo(i){if(openPin===i){closeInfo();return;}openPin=i;track('pin_'+i);const p=PINS[i];$('infoK').textContent=p.k;$('infoT').textContent=p.t;$('infoP').textContent=p.p;$('infoC').innerHTML=p.c.map(x=>`<span>${x}</span>`).join('');pinEls.forEach((e,j)=>e.classList.toggle('on',j===i));$('info').classList.add('show');hideHint();placeInfo();dirty=8;}
function closeInfo(){openPin=-1;$('info').classList.remove('show');pinEls.forEach(e=>e.classList.remove('on'));}
$('infoX').onclick=closeInfo;
function placeInfo(){if(openPin<0||mobile)return;const el=pinEls[openPin];const x=parseFloat(el.style.left),y=parseFloat(el.style.top);const info=$('info');let L=x+24,T=y-40;if(L+300>W())L=x-24-290;T=Math.max(70,Math.min(T,Hh()-info.offsetHeight-16));info.style.left=L+'px';info.style.top=T+'px';}

/* размеры для вида «План» */
const dimGroup=new THREE.Group();scene.add(dimGroup);const dimEls=[];
function buildDims(){const y=CUT+.03,mat=new THREE.LineBasicMaterial({color:0x6e6a62,transparent:true,opacity:0});dimGroup.userData.mat=mat;
const D=[['x',-.62,0,2.27,'2,27 м'],['x',-.62,2.27,6.52,'4,25 м'],['x',-.62,6.82,8.07,'1,25 м'],['z',-.62,0,1.73,'1,73 м'],['z',-.62,1.78,3.48,'1,70 м'],['z',8.62,0,3.48,'3,48 м']];
D.forEach(d=>{const pts=[];const [ax,c,a,b]=d;const P=(u,off)=>ax==='x'?new THREE.Vector3(u,y,c+off):new THREE.Vector3(c+off,y,u);
pts.push(P(a,0),P(b,0),P(a,-.08),P(a,.08),P(b,-.08),P(b,.08));
const g=new THREE.BufferGeometry().setFromPoints(pts);g.setIndex([0,1,2,3,4,5]);dimGroup.add(new THREE.LineSegments(g,mat));
const el=document.createElement('div');el.className='dim';el.textContent=d[4];el.style.opacity=0;overlay.appendChild(el);dimEls.push({el,pos:P((a+b)/2,0)});});}

/* камера */
const tgt=new THREE.Vector3(3.95,.1,1.72);
const VIEWS=mobile?{iso:{th:-1.18,ph:.86,r:14.5,fov:38},top:{th:-Math.PI/2,ph:.0006,r:20.5,fov:36}}:{iso:{th:-.62,ph:.86,r:14.4,fov:32},top:{th:0,ph:.0006,r:17,fov:28}};
let th=VIEWS.iso.th,ph=VIEWS.iso.ph,r=VIEWS.iso.r,view='iso';let vth=0,vph=0;let tween=null,interacted=false,dirty=60;
const rScale=()=>(!mobile&&camera.aspect<1)?1.55:1;
function camPos(){const R=r*rScale();return new THREE.Vector3(tgt.x+R*Math.sin(ph)*Math.sin(th),tgt.y+R*Math.cos(ph),tgt.z+R*Math.sin(ph)*Math.cos(th));}
function go(k){track('view_'+k);view=k;segSet('view',k);const v=VIEWS[k];tween={t0:performance.now(),d:1100,f:{th,ph,r,fov:camera.fov},t:{th:k==='top'?v.th+Math.round((th-v.th)/(Math.PI*2))*Math.PI*2:v.th,ph:v.ph,r:v.r,fov:v.fov}};if(k==='top')closeInfo();dirty=90;}
function intro(){const t0=performance.now();th=VIEWS.iso.th-.9;ph=.42;r=19;tween={t0:t0+150,d:2200,f:{th,ph,r,fov:32},t:{th:VIEWS.iso.th,ph:VIEWS.iso.ph,r:VIEWS.iso.r,fov:32}};
walls.forEach(w=>{w.scale.y=.001;const b=w.geometry.boundingBox;const c=(b.min.x+b.max.x)/2-4;w.userData.delay=200+Math.abs(c)*90+Math.random()*120;});introT0=t0;dirty=400;}
let introT0=0;

/* ввод */
let drag=false,moved=0,lx=0,ly=0;const pts=new Map();let pinch=0;
cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);pts.set(e.pointerId,[e.clientX,e.clientY]);drag=true;moved=0;lx=e.clientX;ly=e.clientY;interacted=true;cv.classList.add('grabbing');});
cv.addEventListener('pointermove',e=>{if(!drag){hover(e);return;}pts.set(e.pointerId,[e.clientX,e.clientY]);if(pts.size===2){const a=[...pts.values()];const d=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]);if(pinch)r=Math.min(24,Math.max(6,r*pinch/d));pinch=d;dirty=30;return;}
const dx=e.clientX-lx,dy=e.clientY-ly;moved+=Math.abs(dx)+Math.abs(dy);lx=e.clientX;ly=e.clientY;if(tween)tween=null;vth=-dx*.006;vph=-dy*.006;th+=vth;ph=Math.max(.0006,Math.min(1.25,ph+vph));if(moved>6&&view==='top'&&ph>.15){view='iso';segSet('view','iso');}dirty=30;tip.style.opacity=0;});
const up=e=>{pts.delete(e.pointerId);if(pts.size<2)pinch=0;if(!pts.size){drag=false;cv.classList.remove('grabbing');if(moved<6){if(furnOn)hover(e,true);else closeInfo();}}};
cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);cv.addEventListener('pointerleave',()=>{if(!drag)clearHover();});
cv.addEventListener('wheel',e=>{e.preventDefault();interacted=true;r=Math.min(24,Math.max(6,r*(1+e.deltaY*.001)));dirty=30;},{passive:false});

/* подсветка мебели */
const tip=$('tip'),ray=new THREE.Raycaster(),mv=new THREE.Vector2();let hl=null,tipTimer=0;
function setHL(name){if(hl===name)return;if(hl&&items[hl])items[hl].forEach(o=>{o.material.emissive.setHex(o.userData.e0??0);o.material.emissiveIntensity=o.userData.ei0??1;});hl=name;if(hl&&items[hl])items[hl].forEach(o=>{if(o.userData.e0===undefined){o.userData.e0=o.material.emissive.getHex();o.userData.ei0=o.material.emissiveIntensity;}if(o.material.name!=='TV_Screen'&&o.material.name!=='LED'){o.material.emissive.setHex(0xfff4e0);o.material.emissiveIntensity=.14;}});dirty=10;}
function clearHover(){setHL(null);tip.style.opacity=0;cv.style.cursor='';}
function hover(e,tap){if(!furnOn||anim){return;}const rc=cv.getBoundingClientRect();mv.set((e.clientX-rc.left)/rc.width*2-1,-(e.clientY-rc.top)/rc.height*2+1);ray.setFromCamera(mv,camera);
const hit=ray.intersectObjects(pickF,false).find(h=>h.object.visible&&!(/Curtain|Tulle|Rod/.test(h.object.name)&&h.point.y>CUT));
if(hit){const it=hit.object.userData.item;setHL(it[1]);tip.querySelector('b').textContent=it[1];tip.querySelector('small').textContent=it[2]?it[2]+' · в пакете':'Входит в пакет';tip.style.left=(e.clientX-rc.left)+'px';tip.style.top=(e.clientY-rc.top)+'px';tip.style.opacity=1;cv.style.cursor='pointer';if(tap){clearTimeout(tipTimer);tipTimer=setTimeout(clearHover,2200);}}else clearHover();}

/* режимы */
let furnOn=false,anim=null;
function segSet(id,val){const s=$(id);const bs=[...s.querySelectorAll('button')];bs.forEach(b=>b.classList.toggle('on',(b.dataset.m||b.dataset.v)===val));const on=bs.find(b=>b.classList.contains('on'));const pill=s.querySelector('.pill');pill.style.width=on.offsetWidth+'px';pill.style.transform=`translateX(${on.offsetLeft-4}px)`;}
function setMode(m,instant){furnOn=m==='furn';segSet('mode',m);$('furnBlock').classList.toggle('active',furnOn);if(furnOn&&mobile&&!instant)setTimeout(()=>$('furnBlock').scrollIntoView({block:'start',behavior:'smooth'}),300);track(furnOn?'furniture_on':'furniture_off');closeInfo();clearHover();
if(furnOn)hideHint();
if(instant){furniture.forEach(o=>o.visible=furnOn&&!o.userData.cut);return;}
furniture.forEach(o=>{o.visible=!o.userData.cut;});anim={t0:performance.now(),on:furnOn};dirty=120;}
document.querySelectorAll('#mode button').forEach(b=>b.onclick=()=>setMode(b.dataset.m));
document.querySelectorAll('#view button').forEach(b=>b.onclick=()=>{interacted=true;go(b.dataset.v);});
['mCta','mCta2'].forEach(id=>$(id).onclick=e=>{track(id==='mCta'?'cta_lead':'cta_furniture');e.currentTarget.textContent='Спасибо! Это прототип — заявка не отправлена';});
function hideHint(){$('hint').style.opacity=0;}
setTimeout(()=>{if(!furnOn)$('hint').style.opacity=0;},9000);

function resize(){const w=W(),h=Hh();renderer.setSize(w,h,false);composer.setSize(w,h);gtao.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();segSet('mode',furnOn?'furn':'empty');segSet('view',view);dirty=10;}
window.addEventListener('resize',resize);resize();window.__3dResize=resize;

const ease=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;const easeOut=x=>1-Math.pow(1-x,3);const back=x=>{const c1=1.4,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);};
const v3=new THREE.Vector3(),camDir=new THREE.Vector3();
function project(p,el,extra){v3.set(p[0]??p.x,p[1]??p.y,p[2]??p.z).project(camera);const vis=v3.z<1;el.style.left=((v3.x+1)/2*W())+'px';el.style.top=((1-v3.y)/2*Hh())+'px';return vis;}
let last=performance.now();
function loop(now){if(!window.__3dOpen){last=now;requestAnimationFrame(loop);return;}const dt=Math.min(.05,(now-last)/1000);last=now;
if(tween){const k=Math.min(1,Math.max(0,(now-tween.t0)/tween.d));const e=ease(k);th=tween.f.th+(tween.t.th-tween.f.th)*e;ph=tween.f.ph+(tween.t.ph-tween.f.ph)*e;r=tween.f.r+(tween.t.r-tween.f.r)*e;camera.fov=tween.f.fov+(tween.t.fov-tween.f.fov)*e;camera.updateProjectionMatrix();if(k>=1)tween=null;dirty=Math.max(dirty,2);}
else if(!drag&&(Math.abs(vth)>1e-4||Math.abs(vph)>1e-4)){th+=vth;ph=Math.max(.0006,Math.min(1.25,ph+vph));vth*=.9;vph*=.9;dirty=Math.max(dirty,2);}
else if(!interacted&&!tween&&view==='iso'){th=VIEWS.iso.th+Math.sin((now-introT0-2400)/4000)*.14*Math.min(1,Math.max(0,(now-introT0-2400)/3000));dirty=Math.max(dirty,1);}
if(walls.length&&walls[0].scale.y<1){walls.forEach(w=>{const k=Math.min(1,Math.max(0,(now-introT0-w.userData.delay)/700));w.scale.y=Math.max(.001,back(k));});dirty=Math.max(dirty,2);}
if(anim){const k=Math.min(1,(now-anim.t0)/750);furniture.forEach((o,i)=>{const d=Math.min(1,Math.max(0,k*1.7-((o.userData.y0*7+i)%9)*.06));const s=anim.on?back(d):1-easeOut(d);o.position.y=o.userData.y0+(1-Math.min(1,s))*.8;o.visible=s>.01&&!o.userData.cut;});if(k>=1){furniture.forEach(o=>{o.position.y=o.userData.y0;o.visible=anim.on&&!o.userData.cut;});anim=null;}dirty=Math.max(dirty,2);}
camera.position.copy(camPos());camera.lookAt(tgt);camera.updateMatrixWorld();
const topK=Math.max(0,1-ph/.35);
if(dimGroup.userData.mat){dimGroup.userData.mat.opacity=topK;dimEls.forEach(d=>{project(d.pos,d.el);d.el.style.opacity=topK;});}
zoneEls.forEach((el,i)=>{const z=ZONES[i];project([z[2],.02,z[3]],el);el.style.opacity=furnOn?0:1;});
camera.getWorldDirection(camDir);
pinEls.forEach((el,i)=>{const p=PINS[i].pos;const vis=project(p,el);const show=!furnOn&&topK<.5&&vis;el.style.opacity=show?1:0;el.style.pointerEvents=show?'auto':'none';});
if(openPin>=0)placeInfo();
if(dirty>0){composer.render(dt);dirty--;}
requestAnimationFrame(loop);}
requestAnimationFrame(loop);

};
if(window.__3dOpen&&!window.__booted){window.__booted=true;window.__boot3d();}
