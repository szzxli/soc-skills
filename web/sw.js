const C='soc-skills-v23';
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(['index.html','manifest.json','verify.html','verify-lib.js','img/example-profile.webp','samples/sample-package.json'])));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));});
self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});
