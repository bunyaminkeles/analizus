/* =============================================================
   ANALIZUS — MODERN KATMAN: ax-modal.js
   Vanilla JS modal controller — bootstrap.Modal API'sinin yerini alır.
   Markup: .ax-modal-backdrop > .ax-modal > .ax-modal__header/body/footer
   Tetikleyici: data-ax-toggle="modal" data-ax-target="#id"
   Kapatma:     data-ax-dismiss="modal" (backdrop'a veya Escape'e tıklama da kapatır)
   Programatik: AxModal.open(el) / AxModal.close(el)
   ============================================================= */

(function () {
    function resolveTarget(selector) {
        if (!selector) return null;
        return document.querySelector(selector.startsWith('#') ? selector : '#' + selector);
    }

    function openModal(modal) {
        if (!modal) return;
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('ax-no-scroll');
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        if (!document.querySelector('.ax-modal-backdrop.is-open')) {
            document.body.classList.remove('ax-no-scroll');
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-ax-toggle="modal"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openModal(resolveTarget(btn.getAttribute('data-ax-target')));
            });
        });
    });

    document.addEventListener('click', function (e) {
        const dismissBtn = e.target.closest('[data-ax-dismiss="modal"]');
        if (dismissBtn) {
            closeModal(dismissBtn.closest('.ax-modal-backdrop'));
            return;
        }
        // Backdrop'un kendisine (diyalog kutusunun dışına) tıklanınca kapat
        if (e.target.classList.contains('ax-modal-backdrop')) {
            closeModal(e.target);
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const open = document.querySelector('.ax-modal-backdrop.is-open');
            if (open) closeModal(open);
        }
    });

    window.AxModal = { open: openModal, close: closeModal };
})();
