// Brand link'i ana siteye yönlendir
document.addEventListener('DOMContentLoaded', function() {
    var brandLink = document.querySelector('.brand-link');
    if (brandLink) {
        brandLink.href = '/';
    }
});
