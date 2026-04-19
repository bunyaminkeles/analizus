(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        // 1. Scroll Spy — navbar'a .navbar--scrolled ekle
        var nav = document.getElementById('siteNav');
        if (nav) {
            function onScroll() {
                if (window.scrollY > 60) {
                    nav.classList.add('site-nav--scrolled');
                } else {
                    nav.classList.remove('site-nav--scrolled');
                }
            }
            window.addEventListener('scroll', onScroll, { passive: true });
            onScroll(); // sayfa yüklenince de uygula
        }

        // 2. Lazy Loading — loading attribute'u olmayan görsellere ekle
        document.querySelectorAll('img:not([loading])').forEach(function (img) {
            img.setAttribute('loading', 'lazy');
        });

    });
}());
