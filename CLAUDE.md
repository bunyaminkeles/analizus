# Analizus.com — Claude Çalışma Kuralları

Tam sistem dokümantasyonu: `analizus.md` (proje kökünde) — stack, URL'ler, modeller, deploy, sık yapılan hatalar, görev listesi hepsi orada.

---

## KIRMIZI ÇİZGİ — DEĞİŞİKLİK KISITLARI

1. **Kapsam dışına çıkma.** İstenen dosya/satır dışında hiçbir şeye dokunma. "İyileştirme" fırsatı görsen bile yapma — ayrı görev olarak sor.
2. **Birden fazla dosya değişecekse önce listele, onay al, sonra uygula.**
3. **Değişiklik yapmadan önce ilgili dosyayı oku.** Tahmin yürütme.
4. **Bir şeyi düzeltirken başka şeyi bozma.** Şüpheliysen sor.
5. **Her değişiklik sonrası dur ve onay bekle.** Tek seferde tek görev.

> Bu kuralları ihlal etmek, doğru çözümden daha büyük zarar verir.

---

## CSS / Tasarım (ax- sistemi)
- Bootstrap yalnızca grid: `container`, `row`, `col-*`
- UI elementleri (`btn`, `card`, `badge`, `alert`) → `ax-` prefix'li özel sınıflar, Bootstrap bileşenleri kullanma
- Renk/spacing → `var(--ax-primary)` CSS değişkeni, asla hardcode renk/pixel yazma
- JS → `data-bs-toggle` yerine vanilla event listener

## Çalışma Prensipleri
- Tahmin yürütme — ilgili dosyayı oku, sonra yaz
- Her değişiklik sonrası dur ve onay bekle; tek seferde tek görev
- Migration gerekiyorsa mutlaka söyle (production DB etkilenir)
- Belirsizlik olunca sor — fiyat, oran, limit gibi iş kararlarını varsayma
- N+1 sorgu yasak — `select_related` / `prefetch_related` zorunlu
- `conn_max_age=0` — long-running transaction'dan kaçın
- Kullanıcıya görünen tüm metinler Türkçe ve akademik dile uygun

## Kritik Non-obvious Kurallar
- E-posta env var: `SMTP_*` prefix — `EMAIL_HOST` değil (`settings.py` içinde map'leniyor)
- `conf_int()` sonucunu `np.array()` ile sar — statsmodels versiyona göre DataFrame veya ndarray döner
- `result_data` kaydetmeden önce `inf`/`nan` temizle → JSON save patlar
- Polling URL: `STATUS_TEMPLATE.replace(sentinel, jobId)` — `STATUS_BASE + jobId + '/'` double slash üretir
- Docker'da migration: `docker compose exec web python manage.py migrate` — host'ta `db` hostname çözülmez
- `docker compose restart web` sonrası nginx da restart edilmeli (IP cache sorunu)
- `docker-compose` değil `docker compose` (Hetzner'de plugin kurulu, eski binary yok)

## Git & Deploy
- Tüm geliştirme `dev` branch'inde — `main`'e kullanıcı "merge et" demeden dokunma
- Commit mesajları: `feat:`, `fix:`, `refactor:` prefix (Türkçe veya İngilizce)
- `.env` değerlerini commit'e dahil etme

**Her zaman hatırla: Kullanıcılar analiz sonuçlarına güvenmek zorunda — hızlı değil, doğru.**
