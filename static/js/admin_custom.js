document.addEventListener('DOMContentLoaded', function() {
    // Brand link'i ana siteye yönlendir (Analizus AI tıklanınca homepage)
    var brandLink = document.querySelector('.brand-link');
    if (brandLink) {
        brandLink.href = '/';
    }

    // Sidebar'dan "Dashboard" butonunu kaldır
    var sidebarItems = document.querySelectorAll('.nav-sidebar > .nav-item');
    sidebarItems.forEach(function(item) {
        var link = item.querySelector('.nav-link');
        if (!link) return;
        var icon = link.querySelector('.fa-tachometer-alt, .fas.fa-tachometer-alt');
        var text = link.textContent.trim();
        if (icon || text === 'Dashboard') {
            item.remove();
        }
    });

    // Content title'daki "Dashboard |" başlığını da kaldır
    var contentTitle = document.querySelector('#content-main');
    if (contentTitle) {
        var h2 = contentTitle.closest('.content-wrapper');
        if (h2) {
            var sectionTitle = h2.querySelector('.content-header h1');
            if (sectionTitle && sectionTitle.textContent.trim().startsWith('Dashboard')) {
                sectionTitle.textContent = '';
            }
        }
    }
});
