document.addEventListener('DOMContentLoaded', function() {
    loadMarketRates();
    loadLatestProposals();
});

// 1. Altınkaynak Verilerini Yükle
async function loadMarketRates() {
    const container = document.getElementById('widget-market-rates');
    if (!container) return;

    try {
        const response = await fetch('/api/widgets/rates/');
        const data = await response.json();

        if (data.rates && data.rates.length > 0) {
            let html = '<ul class="market-list">';
            data.rates.forEach(item => {
                html += `
                    <li class="market-item">
                        <span class="market-name">${item.name}</span>
                        <span class="market-price">${item.price} TL</span>
                    </li>
                `;
            });
            html += '</ul>';
            html += '<div style="padding:8px; text-align:right; font-size:0.7rem; color:#aaa;">Veriler: Altınkaynak</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="p-3 text-muted">Veri alınamadı.</div>';
        }
    } catch (error) {
        console.error('Market rates error:', error);
        container.innerHTML = '<div class="p-3 text-danger">Bağlantı hatası.</div>';
    }
}

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
