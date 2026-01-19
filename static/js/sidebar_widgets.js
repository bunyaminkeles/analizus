document.addEventListener('DOMContentLoaded', function() {
    loadLatestProposals();
});

// 2. Son Teklifleri Yükle
async function loadLatestProposals() {
    const container = document.getElementById('widget-latest-proposals');
    if (!container) return;

    try {
        const response = await fetch('/api/widgets/proposals/');
        const data = await response.json();

        if (data.proposals && data.proposals.length > 0) {
            let html = '<ul class="proposal-list">';
            data.proposals.forEach(p => {
                html += `
                    <li class="proposal-item">
                        <a href="#" class="proposal-job text-truncate">${p.job_title}</a>
                        <div class="proposal-meta">
                            <span>👤 ${p.expert_name}</span>
                            <span class="proposal-price">${p.price}</span>
                        </div>
                        <div style="font-size:0.7rem; color:#ccc; margin-top:2px;">${p.time_ago}</div>
                    </li>
                `;
            });
            html += '</ul>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="p-3 text-muted">Henüz teklif yok.</div>';
        }
    } catch (error) {
        console.error('Proposals error:', error);
    }
}
