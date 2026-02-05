console.log("--- DEBUG: Bildirim scripti (AJAX) yüklendi. ---");

// Bildirim sistemi - AJAX Polling (Redis gerektirmez)
class NotificationManager {
    constructor() {
        this.pollInterval = 15000; // 15 saniyede bir kontrol
        this.storageKey = 'analizus_seen_notifications';
        this.seenNotifications = this.loadSeenNotifications(); // localStorage'dan yükle
        this.init();
    }

    init() {
        // Container oluştur
        this.createContainer();

        // İlk kontrol
        this.checkNotifications();

        // Periyodik kontrol başlat
        setInterval(() => this.checkNotifications(), this.pollInterval);

        // Eski bildirimleri temizle (7 günden eski)
        this.cleanupOldNotifications();

        console.log("--- DEBUG: AJAX Bildirim sistemi başlatıldı ---");
    }

    loadSeenNotifications() {
        // localStorage'dan görülmüş bildirimleri yükle
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                // Object formatında saklanıyor: { id: timestamp }
                return new Map(Object.entries(data));
            }
        } catch (e) {
            console.log("localStorage okuma hatası:", e.message);
        }
        return new Map();
    }

    saveSeenNotifications() {
        // localStorage'a kaydet
        try {
            const obj = Object.fromEntries(this.seenNotifications);
            localStorage.setItem(this.storageKey, JSON.stringify(obj));
        } catch (e) {
            console.log("localStorage yazma hatası:", e.message);
        }
    }

    cleanupOldNotifications() {
        // 7 günden eski bildirimleri temizle
        const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
        let cleaned = false;

        for (const [id, timestamp] of this.seenNotifications) {
            if (timestamp < sevenDaysAgo) {
                this.seenNotifications.delete(id);
                cleaned = true;
            }
        }

        if (cleaned) {
            this.saveSeenNotifications();
        }
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            Object.assign(container.style, {
                position: 'fixed',
                top: '80px',
                right: '20px',
                zIndex: '1055',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
            });
            document.body.appendChild(container);
        }
        this.container = container;
    }

    async checkNotifications() {
        try {
            const response = await fetch('/api/notifications/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                if (response.status === 403) {
                    // Kullanıcı giriş yapmamış, sessizce devam et
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Navbar'daki bildirim sayısını güncelle
            this.updateBadge(data.unread_count);

            // Yeni bildirimleri göster (daha önce gösterilmemişleri)
            data.notifications.forEach(notif => {
                const notifId = String(notif.id);
                if (!this.seenNotifications.has(notifId)) {
                    this.showToast(notif);
                    // Bildirimi gösterildi olarak işaretle
                    this.seenNotifications.set(notifId, Date.now());
                    this.saveSeenNotifications();
                }
            });

        } catch (error) {
            // Hata durumunda sessizce devam et
            console.log("Bildirim kontrolü başarısız:", error.message);
        }
    }

    updateBadge(count) {
        // Navbar'daki bildirim badge'ini güncelle
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    showToast(notification) {
        const toastEl = document.createElement('div');
        toastEl.classList.add('toast');
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.style.minWidth = '320px';
        toastEl.dataset.notificationId = notification.id;

        toastEl.innerHTML = `
            <div class="toast-header bg-info text-dark">
                <i class="bi bi-bell-fill me-2"></i>
                <strong class="me-auto">Yeni Bildirim</strong>
                <small class="text-muted">${notification.created_at}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body" style="cursor: pointer;">
                ${notification.message}
            </div>
        `;

        // Toast body'ye tıklanınca URL'e git ve okundu olarak işaretle
        const toastBody = toastEl.querySelector('.toast-body');
        if (toastBody && notification.url) {
            toastBody.addEventListener('click', async () => {
                await this.markAsRead(notification.id);
                window.location.href = notification.url;
            });
        }

        // Toast kapatılınca okundu olarak işaretle
        toastEl.addEventListener('hidden.bs.toast', async () => {
            await this.markAsRead(notification.id);
            toastEl.remove();
        });

        this.container.appendChild(toastEl);

        // Bootstrap Toast'ı başlat - 10 saniye sonra otomatik kapanır
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 10000
        });
        toast.show();
    }

    async markAsRead(notificationId) {
        try {
            await fetch(`/api/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
        } catch (error) {
            console.log("Bildirim okundu işaretlenemedi:", error.message);
        }
    }

    async markAllAsRead() {
        try {
            await fetch('/api/notifications/read-all/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            this.updateBadge(0);
        } catch (error) {
            console.log("Bildirimler okundu işaretlenemedi:", error.message);
        }
    }

    getCSRFToken() {
        // Cookie'den CSRF token al
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Sayfa yüklendiğinde bildirim yöneticisini başlat
document.addEventListener('DOMContentLoaded', function() {
    // Sadece giriş yapmış kullanıcılar için çalıştır
    // Dropdown menüdeki userDropdown veya logout form'u varsa kullanıcı giriş yapmış demektir
    const userLoggedIn = document.querySelector('[data-user-authenticated="true"]') ||
                         document.querySelector('form[action*="logout"]') ||
                         document.querySelector('#userDropdown');

    if (userLoggedIn) {
        window.notificationManager = new NotificationManager();
        console.log("--- DEBUG: Kullanıcı giriş yapmış, bildirim sistemi aktif ---");
    }
});
