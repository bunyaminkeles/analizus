// PWA service worker — yalnız statik varlıkları (CSS/JS/font/ikon) önbellekler.
// Sayfa/API/WebSocket isteklerine kasıtlı olarak dokunmaz: kimlik doğrulamalı
// dinamik sayfaları önbelleklemek oturum/CSRF tutarsızlığı riski taşır.
// Mantık değişirse CACHE_NAME'i elle artır (projenin ?v=XXXX disipliniyle aynı).
const CACHE_NAME = 'analizus-static-v1';
const STATIC_PREFIX = '/static/';

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const { request } = event;
    if (request.method !== 'GET' || !request.url.includes(STATIC_PREFIX)) {
        return;
    }

    event.respondWith(
        caches.open(CACHE_NAME).then((cache) =>
            cache.match(request).then((cached) => {
                const network = fetch(request)
                    .then((response) => {
                        if (response.ok) {
                            cache.put(request, response.clone());
                        }
                        return response;
                    })
                    .catch(() => cached);
                return cached || network;
            })
        )
    );
});
