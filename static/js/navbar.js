/* =============================================================
   ANALIZUS — MODERN KATMAN: navbar.js
   Vanilla JS — Bootstrap bağımlılığı yok.
   ============================================================= */

document.addEventListener('DOMContentLoaded', function () {

    // -------------------------------------------------------
    // Element referansları
    // -------------------------------------------------------
    const navbar      = document.getElementById('siteNav');
    const hamburger   = document.getElementById('navHamburger');
    const drawer      = document.getElementById('navDrawer');
    const overlay     = document.getElementById('navOverlay');
    const drawerClose = document.getElementById('navDrawerClose');
    const hamOpen     = document.getElementById('hamIconOpen');
    const hamClose    = document.getElementById('hamIconClose');

    // -------------------------------------------------------
    // 1. Desktop Dropdown Toggle
    // -------------------------------------------------------
    const dropdownWraps = document.querySelectorAll('.site-nav__dropdown-wrap');

    function closeAllDropdowns() {
        dropdownWraps.forEach(function (wrap) {
            wrap.classList.remove('is-open');
            const btn = wrap.querySelector('[data-dropdown]');
            if (btn) btn.setAttribute('aria-expanded', 'false');
        });
    }

    dropdownWraps.forEach(function (wrap) {
        const btn = wrap.querySelector('[data-dropdown]');
        if (!btn) return;

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const isOpen = wrap.classList.contains('is-open');
            closeAllDropdowns();
            if (!isOpen) {
                wrap.classList.add('is-open');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // Dışa tıklayınca kapat
    document.addEventListener('click', closeAllDropdowns);

    // Dropdown içine tıklayınca kapanmasın
    document.querySelectorAll('.site-nav__dropdown').forEach(function (dd) {
        dd.addEventListener('click', function (e) { e.stopPropagation(); });
    });

    // -------------------------------------------------------
    // 1b. Flyout submenu (mouseenter/mouseleave — JS class toggle)
    // -------------------------------------------------------
    document.querySelectorAll('.site-nav__flyout-wrap').forEach(function (wrap) {
        wrap.addEventListener('mouseenter', function () {
            document.querySelectorAll('.site-nav__flyout-wrap.is-open').forEach(function (w) {
                if (w !== wrap) w.classList.remove('is-open');
            });
            wrap.classList.add('is-open');
        });
        wrap.addEventListener('mouseleave', function () {
            wrap.classList.remove('is-open');
        });
    });

    // -------------------------------------------------------
    // 2. Mobile Drawer Aç / Kapat
    // -------------------------------------------------------
    function openDrawer() {
        if (!drawer || !overlay || !hamburger) return;
        drawer.classList.add('is-open');
        overlay.classList.add('is-open');
        document.body.classList.add('ax-no-scroll');
        drawer.setAttribute('aria-hidden', 'false');
        overlay.setAttribute('aria-hidden', 'false');
        hamburger.setAttribute('aria-expanded', 'true');
        if (hamOpen)  hamOpen.style.display  = 'none';
        if (hamClose) hamClose.style.display = 'block';
    }

    function closeDrawer() {
        if (!drawer || !overlay || !hamburger) return;
        drawer.classList.remove('is-open');
        overlay.classList.remove('is-open');
        document.body.classList.remove('ax-no-scroll');
        drawer.setAttribute('aria-hidden', 'true');
        overlay.setAttribute('aria-hidden', 'true');
        hamburger.setAttribute('aria-expanded', 'false');
        if (hamOpen)  hamOpen.style.display  = 'block';
        if (hamClose) hamClose.style.display = 'none';
    }

    if (hamburger)   hamburger.addEventListener('click', openDrawer);
    if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
    if (overlay)     overlay.addEventListener('click', closeDrawer);

    // -------------------------------------------------------
    // 3. Mobile Accordion (Analizler, Araçlar)
    // -------------------------------------------------------
    document.querySelectorAll('.nav-drawer__accordion-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = btn.getAttribute('data-accordion');
            const body     = targetId ? document.getElementById(targetId) : null;
            if (!body) return;

            const isOpen = body.classList.contains('is-open');

            // Diğer accordion'ları kapat
            document.querySelectorAll('.nav-drawer__accordion-body').forEach(function (b) {
                b.classList.remove('is-open');
            });
            document.querySelectorAll('.nav-drawer__accordion-btn').forEach(function (b) {
                b.setAttribute('aria-expanded', 'false');
            });

            // Bu accordion'u toggle
            if (!isOpen) {
                body.classList.add('is-open');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // -------------------------------------------------------
    // 4. Escape tuşu
    // -------------------------------------------------------
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeAllDropdowns();
            closeDrawer();
        }
    });

    // -------------------------------------------------------
    // 5. Scroll davranışı
    // -------------------------------------------------------
    function handleScroll() {
        if (!navbar) return;
        if (window.scrollY > 10) {
            navbar.classList.add('site-nav--scrolled');
        } else {
            navbar.classList.remove('site-nav--scrolled');
        }
    }

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // İlk yüklemede kontrol et

});
