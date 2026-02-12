// Brand link'i ana siteye yönlendir
// Jazzmin custom_js body sonunda yükleniyor, DOMContentLoaded zaten fire etmiş olabilir
(function() {
    function fixBrandLinks() {
        document.querySelectorAll('#jazzy-logo, .brand-link').forEach(function(el) {
            el.href = '/';
            el.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                window.location.href = '/';
                return false;
            };
        });
    }

    // Hem hemen çalıştır hem de DOMContentLoaded'da (hangisi geçerliyse)
    fixBrandLinks();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixBrandLinks);
    }
})();
