/* =============================================================
   ANALIZUS — MODERN KATMAN: ax-dropdown.js
   Genel amaçlı vanilla JS dropdown controller (navbar.js'teki
   site-nav__dropdown-wrap deseninin genel/yeniden kullanılabilir hâli).
   navbar.js'e dokunmaz, ayrı ve bağımsız çalışır.
   Markup: .ax-dropdown-wrap > [data-ax-dropdown] + .ax-dropdown
   ============================================================= */

document.addEventListener('DOMContentLoaded', function () {
    const wraps = document.querySelectorAll('.ax-dropdown-wrap');
    if (!wraps.length) return;

    function closeAll() {
        wraps.forEach(function (wrap) {
            wrap.classList.remove('is-open');
            const btn = wrap.querySelector('[data-ax-dropdown]');
            if (btn) btn.setAttribute('aria-expanded', 'false');
        });
    }

    wraps.forEach(function (wrap) {
        const btn = wrap.querySelector('[data-ax-dropdown]');
        if (!btn) return;

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const isOpen = wrap.classList.contains('is-open');
            closeAll();
            if (!isOpen) {
                wrap.classList.add('is-open');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    });

    document.addEventListener('click', closeAll);

    document.querySelectorAll('.ax-dropdown').forEach(function (dd) {
        dd.addEventListener('click', function (e) { e.stopPropagation(); });
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAll();
    });
});
