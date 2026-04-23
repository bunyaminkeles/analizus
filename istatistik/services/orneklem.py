"""
Örneklem Büyüklüğü Hesaplayıcı — scipy tabanlı güç analizi.
Test tipleri: t-test (bağımsız/bağımlı), ANOVA, korelasyon.
"""
from scipy import stats


def calculate(test_type: str, effect_size: float, alpha: float,
              power: float, groups: int = 2) -> dict:
    """
    Verilen parametreler için gerekli örneklem büyüklüğünü hesaplar.
    Dönüş: {n, n_total, achieved_power, test_type, inputs, interpretation}
    """
    if not (0 < alpha < 1):
        raise ValueError('Alfa 0 ile 1 arasında olmalıdır.')
    if not (0 < power < 1):
        raise ValueError('Güç 0 ile 1 arasında olmalıdır.')
    if effect_size <= 0:
        raise ValueError('Etki büyüklüğü 0\'dan büyük olmalıdır.')

    if test_type == 'ttest_independent':
        n, achieved = _ttest_independent(effect_size, alpha, power)
        n_total = n * 2
        label = 'Bağımsız Örneklem t-Testi'
        unit = f'{n} kişi/grup × 2 grup'
    elif test_type == 'ttest_paired':
        n, achieved = _ttest_paired(effect_size, alpha, power)
        n_total = n
        label = 'Bağımlı Örneklem t-Testi (Eşleştirilmiş)'
        unit = f'{n} çift'
    elif test_type == 'anova':
        if groups < 2:
            raise ValueError('ANOVA için en az 2 grup gereklidir.')
        n, achieved = _anova(effect_size, alpha, power, groups)
        n_total = n * groups
        label = f'Tek Yönlü ANOVA ({groups} grup)'
        unit = f'{n} kişi/grup × {groups} grup'
    elif test_type == 'correlation':
        n, achieved = _correlation(effect_size, alpha, power)
        n_total = n
        label = 'Korelasyon Analizi'
        unit = f'{n} çift gözlem'
    else:
        raise ValueError(f'Bilinmeyen test tipi: {test_type}')

    return {
        'test_type': test_type,
        'label': label,
        'n_per_group': n,
        'n_total': n_total,
        'unit': unit,
        'achieved_power': round(achieved, 4),
        'inputs': {
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power,
            'groups': groups,
        },
        'effect_interpretation': _interpret_effect(test_type, effect_size),
        'recommendation': _recommendation(n_total),
    }


# ── İç hesaplama fonksiyonları ────────────────────────────────────────────────

def _ttest_power(n: int, d: float, alpha: float, paired: bool) -> float:
    """
    t-test gücü — normal dağılım yaklaşımı (n≥10 için yeterince doğru).
    scipy.nct büyük df/ncp değerlerinde sayısal kararsızlık gösterdiğinden
    Laubscher normal yaklaşımı kullanılır.
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    if paired:
        delta = d * (n ** 0.5)
    else:
        delta = d * (n / 2) ** 0.5
    # two-sided: güç = Φ(δ − z_α/2) + Φ(−δ − z_α/2)
    power = stats.norm.cdf(delta - z_alpha) + stats.norm.cdf(-delta - z_alpha)
    return float(power)


def _ttest_independent(d: float, alpha: float, target_power: float):
    return _binary_search(lambda n: _ttest_power(n, d, alpha, paired=False), target_power)


def _ttest_paired(d: float, alpha: float, target_power: float):
    return _binary_search(lambda n: _ttest_power(n, d, alpha, paired=True), target_power)


def _anova_power(n: int, f: float, alpha: float, k: int) -> float:
    """Verilen n (grup başına) için ANOVA gücünü hesaplar."""
    dfn = k - 1
    dfd = k * (n - 1)
    ncp = n * k * (f ** 2)
    f_crit = stats.f.ppf(1 - alpha, dfn=dfn, dfd=dfd)
    power = 1 - stats.ncf.cdf(f_crit, dfn=dfn, dfd=dfd, nc=ncp)
    return float(power)


def _anova(f: float, alpha: float, target_power: float, k: int):
    return _binary_search(lambda n: _anova_power(n, f, alpha, k), target_power)


def _correlation_power(n: int, r: float, alpha: float) -> float:
    """Verilen n için korelasyon testinin gücünü hesaplar (Fisher z dönüşümü)."""
    import math
    z_r = math.atanh(r)
    z_crit = stats.norm.ppf(1 - alpha / 2)
    se = 1 / ((n - 3) ** 0.5) if n > 3 else 1
    power = (1 - stats.norm.cdf(z_crit - z_r / se)
             + stats.norm.cdf(-z_crit - z_r / se))
    return float(power)


def _correlation(r: float, alpha: float, target_power: float):
    return _binary_search(lambda n: _correlation_power(n, r, alpha), target_power)


def _binary_search(power_fn, target: float, lo: int = 2, hi: int = 10000):
    """Hedef güce ulaşan minimum n'i binary search ile bulur."""
    while lo < hi:
        mid = (lo + hi) // 2
        if power_fn(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo, power_fn(lo)


# ── Yorum fonksiyonları ───────────────────────────────────────────────────────

def _interpret_effect(test_type: str, effect_size: float) -> str:
    if test_type in ('ttest_independent', 'ttest_paired'):
        # Cohen's d
        if effect_size < 0.2:
            return f'd = {effect_size} — Çok küçük etki'
        if effect_size < 0.5:
            return f'd = {effect_size} — Küçük etki (Cohen, 1988)'
        if effect_size < 0.8:
            return f'd = {effect_size} — Orta düzey etki (Cohen, 1988)'
        return f'd = {effect_size} — Büyük etki (Cohen, 1988)'
    elif test_type == 'anova':
        # Cohen's f
        if effect_size < 0.1:
            return f'f = {effect_size} — Çok küçük etki'
        if effect_size < 0.25:
            return f'f = {effect_size} — Küçük etki (Cohen, 1988)'
        if effect_size < 0.40:
            return f'f = {effect_size} — Orta düzey etki (Cohen, 1988)'
        return f'f = {effect_size} — Büyük etki (Cohen, 1988)'
    else:
        # Pearson r
        if effect_size < 0.1:
            return f'r = {effect_size} — Çok küçük etki'
        if effect_size < 0.3:
            return f'r = {effect_size} — Küçük etki (Cohen, 1988)'
        if effect_size < 0.5:
            return f'r = {effect_size} — Orta düzey etki (Cohen, 1988)'
        return f'r = {effect_size} — Büyük etki (Cohen, 1988)'


def _recommendation(n_total: int) -> str:
    if n_total <= 30:
        return 'Küçük örneklem — pilot çalışma için uygun olabilir, genel çalışmalar için kayıp gözetilerek artırın.'
    if n_total <= 100:
        return 'Orta örneklem — çoğu sosyal bilim araştırması için yeterli kabul edilir.'
    if n_total <= 300:
        return 'İyi örneklem — güvenilir sonuçlar için uygun büyüklük.'
    return 'Büyük örneklem — yüksek güç ve genellenebilirlik sağlar; pratik uygulanabilirliği değerlendirin.'
