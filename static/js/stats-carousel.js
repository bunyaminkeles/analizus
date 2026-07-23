(function () {
    'use strict';

    /* ----------------------------------------------------------
       1. BAŞARI HİKAYELERİ CAROUSEL
       ---------------------------------------------------------- */
    const carousel   = document.getElementById('axTestimonialCarousel');
    const dotsWrap   = document.getElementById('axCarouselDots');
    const prevBtn    = document.getElementById('axCarouselPrev');
    const nextBtn    = document.getElementById('axCarouselNext');

    if (carousel && window.__testimonials && window.__testimonials.length > 0) {
        const stories = window.__testimonials;
        let current   = 0;
        let timer     = null;

        function avatarHtml(story) {
            if (story.avatar) {
                return `<img class="ax-testimonial-card__avatar" src="${story.avatar}" alt="${story.name}">`;
            }
            return `<div class="ax-testimonial-card__avatar">👤</div>`;
        }

        function badgesHtml(achievements) {
            if (!achievements || !achievements.length) return '';
            return `<div class="ax-testimonial-card__achievements">
                ${achievements.slice(0, 4).map(a =>
                    `<span class="ax-testimonial-card__badge">${a}</span>`
                ).join('')}
            </div>`;
        }

        function render(idx) {
            const s = stories[idx];
            carousel.innerHTML = `
                <div class="ax-testimonial-card">
                    ${avatarHtml(s)}
                    <p class="ax-testimonial-card__quote">${s.quote}</p>
                    <p class="ax-testimonial-card__name">${s.name}</p>
                    ${badgesHtml(s.achievements)}
                </div>`;

            dotsWrap.querySelectorAll('.ax-dot').forEach((d, i) =>
                d.classList.toggle('active', i === idx)
            );
        }

        function go(idx) {
            current = (idx + stories.length) % stories.length;
            render(current);
            resetTimer();
        }

        function resetTimer() {
            clearInterval(timer);
            timer = setInterval(() => go(current + 1), 6000);
        }

        // Dot'ları oluştur
        stories.forEach((_, i) => {
            const dot = document.createElement('button');
            dot.className = 'ax-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('aria-label', `Hikaye ${i + 1}`);
            dot.addEventListener('click', () => go(i));
            dotsWrap.appendChild(dot);
        });

        if (prevBtn) prevBtn.addEventListener('click', () => go(current - 1));
        if (nextBtn) nextBtn.addEventListener('click', () => go(current + 1));

        render(0);
        resetTimer();
    }

    /* ----------------------------------------------------------
       2. SAYAÇ ANİMASYONU (Intersection Observer)
       ---------------------------------------------------------- */
    const statEls = document.querySelectorAll('.ax-stat-item[data-target]');
    if (!statEls.length) return;

    function animateCount(el) {
        const target   = parseInt(el.dataset.target, 10);
        const suffix   = el.dataset.suffix ?? '+';
        const duration = 2000;
        const step     = 16;
        const steps    = Math.floor(duration / step);
        let count      = 0;

        const interval = setInterval(() => {
            count++;
            const value = Math.round((count / steps) * target);
            el.textContent = value.toLocaleString('tr-TR') + suffix;
            if (count >= steps) {
                el.textContent = target.toLocaleString('tr-TR') + suffix;
                clearInterval(interval);
            }
        }, step);
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                entry.target.dataset.animated = '1';
                animateCount(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    statEls.forEach(el => observer.observe(el));
}());
