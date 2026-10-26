const C='soc-skills-v26';
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(['index.html','manifest.json','verify.html','verify-lib.js','img/example-profile.webp','samples/sample-package.json'])));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));});
// Only same-origin GETs go through the cache; cross-origin requests (GoatCounter at gc.zgo.at /
// szzxli-sec.goatcounter.com, AI API providers) and non-GETs go straight to the network untouched.
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});
