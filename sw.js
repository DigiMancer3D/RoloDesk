const CACHE='rolodesk-v033-static-v1';
const APP='./RoloDesk_v0.3.4.html';
const ASSETS=[APP,'./manifest.webmanifest','./rolodesk-192.png','./rolodesk-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(Promise.all([self.clients.claim(),caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('rolodesk-')&&k!==CACHE).map(k=>caches.delete(k))))])));
function dbOpen(){return new Promise((res,rej)=>{let r=indexedDB.open('rolodesk_local_r2',1);r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains('kv'))r.result.createObjectStore('kv')};r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
async function put(k,v){let d=await dbOpen();return new Promise((res,rej)=>{let tx=d.transaction('kv','readwrite');tx.objectStore('kv').put(v,k);tx.oncomplete=()=>res();tx.onerror=()=>rej(tx.error)})}
self.addEventListener('fetch',event=>{
  const u=new URL(event.request.url);
  if(event.request.method==='POST' && u.pathname.endsWith('/share-target')){
    event.respondWith((async()=>{
      try{
        const f=await event.request.formData();
        let title=String(f.get('title')||'Shared note'), text=String(f.get('text')||''), url=String(f.get('url')||'');
        const files=f.getAll('files').filter(x=>x&&typeof x.text==='function');
        if(files.length){for(const file of files){try{text+=(text?'\n\n':'')+await file.text()}catch{}}}
        if(url)text+=(text?'\n':'')+url;
        await put('sharedIncoming',{title,text,received:new Date().toISOString()});
      }catch(e){}
      return Response.redirect('./RoloDesk_v0.3.4.html?shared=1',303);
    })());return;
  }
  if(event.request.method==='GET')event.respondWith(caches.match(event.request).then(r=>r||fetch(event.request)));
});
