// Service worker'ı sabit/hash'siz bir path'ten register eder — SW spec'i aynı URL'de
// byte-byte güncelleme kontrolü yaptığı için {% static %} ile hash'lenemez (bkz. nginx
// /static/js/service-worker.js no-cache override).
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js', { scope: '/' })
            .catch((err) => console.warn('Service worker kaydı başarısız:', err));
    });
}
