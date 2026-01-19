document.addEventListener('DOMContentLoaded', function() {
    // Select only headers within sidebar widgets
    const widgetHeaders = document.querySelectorAll('.sidebar-widget .widget-header');

    widgetHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const widget = header.closest('.sidebar-widget');
            if (widget) {
                widget.classList.toggle('collapsed');
            }
        });
    });
});