# Çok Dilli Yayın (EN/DE) — DEVAM EDİYOR

**Durum:** 23 Eylül 2026 — devam ediyor. Aşağıdaki "DEVAM NOKTASI"
bölümünden başla.

## DEVAM NOKTASI (bir sonraki oturum buradan başlasın)

### AÇIK İŞLER — TEK LİSTE (24 Eylül 2026 sonu; 25 Eylül buradan başla)
Kullanıcı kuralı: **bütün eksiklikler mutlaka bu listede olmalı.** Yeni
bulgu çıktığında buraya ekle; bitince [x] yap. Ayrıntılar alttaki ilgili
maddelerde.

**A. Kod işleri (öncelik sırasıyla)**
- [x] **WhatsApp hazır mesajları Türkçe** — ÇEVRİLDİ (26 Eylül 2026): 6 şablon, `{% filter urlencode:"" %}{% trans %}`; TR mesajları aynen. Eski not:
  `wa.me/...?text=Merhaba%2C...` URL-kodlu sabit TR metin — footer, iletişim, proje
  talebi, eğitim, eğitim talebi, ilan verme sayfaları (6 yer). EN/DE'de mesaj
  kullanıcının dilinde olmalı (`{% trans %}` + `|urlencode`).
- [x] **Footer "Akademik Kaynaklar" EN/DE** — TAMAMLANDI (26 Eylül 2026, kullanıcı
  kararı "uluslararası 4'lü"): EN/DE → Google Scholar, Semantic Scholar, OpenAlex,
  BASE (Bielefeld); TR listesi aynen. `LANGUAGE_CODE` koşulu, yeni ikonlar
  Bootstrap Icons (dış favicon indirilmedi). Eski not (25 Eylül 2026): `templates/partials/footer.html` ~69-92 — başlık çevrili ama liste
  sabit ve Türkiye'ye özgü: Google Scholar, DergiPark, Semantic Scholar, YÖK Tez
  Merkezi (+ yerel favicon'lar `static/img/favicon-*.ico`). EN/DE'de DergiPark ve
  YÖK yerine uluslararası kaynaklar (ör. PubMed, arXiv, OpenAlex, BASE / DE için
  DNB) — dile göre liste (`LANGUAGE_CODE`); kaynak seçimi kullanıcıyla
  netleştirilecek. TR listesi aynı kalır.
- [x] **Hesap silme cron'u kullanıcı kararlarına uydurulacak** (25 Eylül 2026) — 3 adım TAMAMLANDI.
  DÜZELTME: 24 Eylül'deki "silen kod yok" bulgusu YANLIŞTI — işlev var:
  `forum/api_views.py` `cron_process_account_deletions`, Hetzner crontab
  `0 3 * * *`, nginx logunda 23-25 Eylül her gün 200 (processed: 0).
  Kullanıcı kararları (25 Eylül): açık içerik anonimleştir ✅ (zaten öyle);
  DM'ler karşı tarafta kalsın ❌ (kod ikisini de siliyor); mali kayıt anonim
  sakla ⚠️ (Donation.name/email temizlenmiyor); 30 gün içinde giriş yapınca
  iptal ❌ (yok). Ek eksik: tarama/analiz işleri+dosyaları, bildirim,
  PageView, quiz skorları, oda üyelikleri, takip listesi silinmiyor; açık
  ilanlar iptal edilmiyor. Silme mesajı çevrilmemiş.
  - [x] 1. Cron kararlara uyduruldu (25 Eylül 2026): `_anonymize_deleted_account`
    — DM'ler kalır, bağış scrub, siparişli iş korunur (URL+S3 dosyası silinir),
    özel veriler silinir, açık ilan iptal, tek transaction + S3 on_commit.
    Rollback testinde doğrulandı. Canlıya merge ile gider (cron aynı URL).
  - [x] 2. "Geri al" akışı (25 Eylül 2026): custom_login pasif + 30 gün içi +
    şifre doğru → oturuma 10 dk'lık işaret → `/account/restore/` (i18n);
    "Hesabımı geri al" / "Silme işlemi devam etsin". 7 senaryo test edildi.
  - [x] 3. Metinler (25 Eylül 2026): `account_delete.html` gerçek davranışa göre
    yeniden yazıldı (3 yanlış ifade düzeltildi) + EN/DE; silme e-postası alıcının
    dilinde, onay linki `reverse()` ile dil önekli (URL'ler urls_i18n'e taşındı,
    TR yolları aynı); flash mesajları çevrildi; gizlilik metnine "30 gün" +
    anonim mali kayıt geri eklendi.
- [x] **Silinmiş hesabın görünen adı** — ÇÖZÜLDÜ (25 Eylül 2026, kullanıcı
  kararı "okunur kullanıcı adı"): cron artık `silinmis-kullanici-<hex>` üretiyor;
  mevcut `deleted_<hex>` hesaplar **veri migration 0155** ile dönüştürülüyor
  (yalnızca `@deleted.invalid` e-postalılar; ileri/geri test edildi).
  Dile göre "Silinmiş kullanıcı / Deleted user" gösterimi YAPILMADI (37 şablon,
  83 yer + Python tarafı) — istenirse ayrı iş.
- [x] **Profil sayfaları tek dilli** — ÇEVRİLDİ (26 Eylül 2026): `profile_detail`,
  `profile_edit`, `profile_private` + 6 view mesajı; URL'ler `urls_i18n.py`'ye
  taşındı (TR yolları aynı). Telefon (kullanıcı kararı "+90 ekleyebiliriz"):
  `_normalize_tr_phone` 05…/5…/+90/90/0090 kabul eder, `05XXXXXXXXX` saklar;
  yurt dışı numara hâlâ reddedilir. 116 msgid EN/DE. Eski not: profil/profil düzenleme (ve "Hesabımı Sil"
  butonu) i18n dışında — EN/DE kullanıcı silme sayfasına TR olarak ulaşır.
- [x] **Rütbe adları tek dilli** — ÇEVRİLDİ (26 Eylül 2026): `pgettext('rütbe', …)` bağlamı
  ("Üye"/"Aktif Üye" başka yerde çoğul çevrili olduğu için); RANK_CHOICES + RANK_INFO +
  "Ziyaretçi"; migration ÇIKMADI (makemigrations "No changes"). Kullanıcının kendi
  yazdığı Ünvan (`profile.title`, ör. "Platform Yöneticisi") kullanıcı içeriği — çevrilmez.
  Çalışma odası kartındaki "… seviye üye" odalar tek dilli olduğu için kapsam dışı. Eski not: `forum/templatetags/forum_extras.py`
  `RANK_INFO` ("🌱 Çaylak", "Uzman"…) ve `Profile.RANK_CHOICES` (models.py ~156)
  çeviri dışı — site genelinde (navbar, forum, profil) görünür. `gettext_lazy`
  ile sarılınca `RANK_CHOICES` için **no-op AlterField migration** çıkar.
- [x] **Rozet adları/açıklamaları** — ÇEVRİLDİ (26 Eylül 2026, kullanıcı kararı "DB'de dil
  alanları"): `Badge.name_en/_de`, `description_en/_de` + `localized_name` /
  `localized_description` (boşsa TR'ye düşer). **Migration 0156** (4 AddField + mevcut
  18 rozeti slug ile dolduran RunPython; yalnız boş alanları doldurur; geri alma
  test edildi). Admin'de yeni alanlar otomatik görünür. Kullanım yerleri: profil,
  `render_badge`/`render_user_badges`, `can_propose()` gerekçesi.
  **Canlıya çıkışta:** migration'lı deploy → önce DB yedeği.
- [ ] **`create_badges` komutu EN/DE içermiyor** (26 Eylül 2026): boş DB'de komutla
  oluşan rozetler TR'ye düşer (0156 yalnız mevcut kayıtları doldurur).
- [ ] **Quiz rozet bildirimi TR sabit** (26 Eylül 2026): `forum/views.py` ~3010
  `category_badge_map` / `'Quiz Efsanesi'` sabit Türkçe adlar — `Badge.localized_name`
  ile slug'dan alınmalı (quiz modülü genel olarak tek dilli mi — önce ölç).
- [ ] **EDU "Doğrulanmış Akademisyen" DM metni TR sabit** (26 Eylül 2026):
  `forum/views.py` ~1330 — DM DB'ye yazılıyor; alıcının dilinde (`recipient_language`) üretilmeli.
- [ ] **Profil modal view'ı kırık olabilir** (26 Eylül 2026): `views.py` ~3043
  `forum/partials/profile_modal_content.html` render ediyor ama bu şablon yok
  (`forum/profile_modal_content.html` ve `templates/profile_modal_content.html` var,
  ikisi farklı). URL'nin kullanılıp kullanılmadığı ölçülecek.
- [ ] **Rozet adları/açıklamaları tek dilli** — eski not (26 Eylül 2026): `Badge.name` /
  `Badge.description` DB içeriği ("Profesör", "2500 akademik puan kazandınız -
  TEKLİF VEREBİLİR"…) EN/DE profilde TR. Strateji kararı gerekli: slug→çeviri
  sözlüğü (kod) mi, DB'de dil alanları (migration) mı. `can_propose()` rozet
  adını gerekçe olarak döndürüyor — o da etkilenir.
- [x] **Yetenek (JobCategory) başlıkları** — YAPILDI (26 Eylül 2026, kullanıcı kararları:
  DB dil alanları + yeni kategori admin onayına + onaylı temizlik tablosu).
  **Migration 0157**: `title_en/_de` + veri adımı — 6 birleştirme (37,41,42→3;
  39→25; 35→23; 34→6; ilan FK + uzman yetenekleri taşınır, çift bağ oluşmaz),
  6 ad düzeltme, 5 pasife alma (C++, Java, Javascript, SEO, Web tasarımı),
  32 aktif kaydın EN/DE çevirisi. Her adım id+başlık eşleşirse çalışır;
  idempotent; geri alma veri için no-op → **deploy öncesi DB yedeği şart**.
  Canlı kopyasıyla (43 kayıt + yabancı kayıt) test edildi: 43→37, aktif 32.
  `JobPostForm`: yazılan metin TR/EN/DE başlıkla (iexact) eşleşir; yoksa
  `is_active=False` oluşur. Gösterim: profil, düzenleme, uzman dizini,
  expert showcase, market liste/detay, ilan datalist'i.
- [ ] **Kategori eşleşmesinde Türkçe İ/i** (26 Eylül 2026): `title__iexact`
  PostgreSQL'de "YENİ" ile "yeni"yi eşleştirmiyor → ayrı pasif kayıt açılır
  (admin onayına düştüğü için etkisi düşük). Gerekirse Python tarafında
  `casefold` + TR i/İ normalizasyonu.
- [ ] **Yeni pasif kategoriler için admin bildirimi yok** (26 Eylül 2026): ilan
  formundan açılan kategori admin'de yalnız "Aktif" filtresiyle görülür.
- [ ] **Kategori sıralaması TR başlığa göre** (26 Eylül 2026): EN/DE listelerde
  `order_by('order','title')` Türkçe başlığa göre sıralar; `order` alanı hepsi 0.
- [ ] **İlan e-postasındaki kategori TR** (26 Eylül 2026): `views.py` ~2191
  `job.category.title` / varsayılan 'Veri Analizi'.
- [ ] **Yetenek (JobCategory) başlıkları** — eski not (26 Eylül 2026): profil düzenleme
  chip'leri ve profil etiketleri DB `JobCategory.title` — EN/DE'de TR olup
  olmadığı kontrol edilecek (market ile ortak).
  **ÖLÇÜM (26 Eylül 2026):** Evet, tek dilli. Kritik bulgu: kategoriler kullanıcı
  girişiyle oluşuyor — `JobPostForm.save()` (forms.py ~168) ilan verirken yazılan
  metni `JobCategory.objects.get_or_create(title=…)` ile YENİ kategori yapıyor; bu
  kayıtlar `is_active=True` olduğu için profil düzenlemedeki yetenek listesine ve
  ilan datalist'ine de düşüyor. Gösterim yerleri: profil (2), profil düzenleme,
  uzman dizini, `_expert_showcase`, `_studyroom_founder_card`, market liste/detay,
  post_job/edit_job datalist, ilan e-postası (views ~2191, varsayılan 'Veri Analizi' TR).
  Yerel DB'de 0 kayıt → canlı liste ölçülmeden çeviri verisi yazılamaz.
  **Canlı liste ölçüldü (26 Eylül 2026): 43 kayıt, hepsi aktif, `order` hepsi 0.**
  - id 2–33 (32 kayıt) seed/küratörlü görünüyor; id 34–44 (11) ilan formundan
    kullanıcı girişiyle oluşmuş: "SPSS ve içerik analizi", "Maxquda ile 27 kişiye
    ait verinin çalışılması" (ilan başlığı kategori olmuş), "Nitel Veri Analizi",
    "Yapay zeka modelleme", "Veri etiketleme", "Python", "Python eğitimi",
    "Ai modelleme", "Yapay Zeka & ML, Python, Otomasyon", "Makale Desteği",
    "Tez danışmanlığı".
  - Yinelenenler: yapay zeka (3, 37, 41, 42), Python (39, 40, 25), nitel (36, 22, 23).
  - Yazım: "MAXQUDA"→MAXQDA (23, 35), "modlellemesi" (5), "Geçerlik" (29).
  - 11 kaydın hiç ilanı/uzmanı yok (C++, Java, Javascript, SEO, Web tasarımı…).
  Bekleyen: (1) ~~canlıdaki kategori listesi~~ ölçüldü,
  (2) karar: rozetlerdeki gibi `title_en/_de` + migration mı; kullanıcı kaynaklı
  kategoriler ne olacak (admin onayı / serbest metin kalır).
- [x] **Profil düzenleme: geçersiz telefonda çift mesaj** — DÜZELTİLDİ (26 Eylül 2026):
  diğer alanlar kaydedilir, başarı + hata yerine tek uyarı ("Diğer bilgileriniz
  kaydedildi; ancak telefon numarası … kaydedilmedi") — TR/EN/DE test edildi.
- [ ] **Profil kaydı hata verse de "başarıyla güncellendi" deniyor** (26 Eylül 2026,
  önceden var): `profile_edit` `profile.save()` istisnasını loglayıp yutuyor, sonra
  başarı mesajı gösteriyor (views.py ~1440). Hata mesajı gösterilmeli — karar/iş.
- [x] (eski not) **Profil düzenleme: geçersiz telefonda çift mesaj** (26 Eylül 2026, önceden
  var olan davranış): hata mesajının yanında "Profiliniz başarıyla güncellendi"
  da çıkıyor (diğer alanlar kaydediliyor). Mesaj akışı düzeltilecek mi — karar.
- [ ] **Profil düzenleme JS hatası** (26 Eylül 2026, önceden var): `profile_edit.html`
  scripti olmayan `#custom-skill-input` / `#custom-skills-hidden` elemanlarını
  kullanıyor → konsolda TypeError (chip seçimi ve arama etkilenmiyor, hata
  onlardan sonra). Ölü kod silinmeli ya da manuel yetenek alanı eklenmeli — karar.
- [ ] **Profil şablonları ax- sistemine aykırı** (26 Eylül 2026, önceden var):
  `profile_edit.html` Bootstrap `card`/`btn`/`nav-tabs` + `data-bs-toggle`,
  hardcode renkler; `profile_detail.html` "Hesabımı Sil" `btn btn-outline-danger`.
- [ ] **Takip API hata metni tek dilli** (düşük öncelik): `api_views.toggle_follow_user`
  "Kendinizi takip edemezsiniz." — arayüzden ulaşılamıyor.
- [x] **Ana sayfa hero test çipleri** — ÇEVRİLDİ (25 Eylül 2026) "t-testi · korelasyon · regresyon"
  EN/DE'de Türkçe.
- [x] **"Güvenilir Üye" rozet mesajı** — ÇEVRİLDİ (25 Eylül 2026) (`_check_and_award_trust_badge`,
  forum/views.py ~1700) Türkçe — e-posta doğrulama sonrasında çıkabiliyor.
- [x] **AI Asistan `/istatistik/…` linkleri** — ÇÖZÜLDÜ (25 Eylül 2026):
  EN/DE'de `/istatistik/<slug>/` → `/<dil>/analiz/<slug>/` (18 slug birebir,
  hepsi 200, bilinmeyen slug 404 — doğrulandı). TR davranışı aynı.
- [x] **AI Asistan ölü/koşullu linkler** — ÇÖZÜLDÜ (25 Eylül 2026): `/makaleanaliz/` kaldırıldı (giriş sayfası yok → talimatta `/tarama/` + "tarama sonucundan başlatılır"); `_PATH_FEATURE_FLAGS` ile bayrağı kapalı sayfaların talimat satırları ve izinli linkleri istek anında çıkarılıyor. Açık tüm hedefler 3 dilde 200/302 doğrulandı. Eski not:
  `/makaleanaliz/` her ortamda 404 (izinli listede + talimatta var ama kökte
  sayfa yok); `/ai-cozumler/`, `/egitim/`, `/egitim-talebi/` feature flag
  kapalıyken 404 — talimat/izinli liste flag'e göre filtrelenmeli.
- [x] **AI Asistan kapasite** — İYİLEŞTİRİLDİ (25 Eylül 2026): talimat kural
  kaybı olmadan sıkıştırıldı; ölçülen istek başı token TR 2625→1772 (-%32), EN
  ~2994→1868 (-%38) → dakikada ~3 → ~4,5 soru (~1,5x). 5 senaryo canlı test
  (test seçimi, uzman isteği, NVivo yok, kapalı eğitim sayfası, tez yazdırma
  reddi) + EN/DE dil: OK. `reasoning_effort=low` ölçüldü (+%15) ama yanıtları
  kısalttığı için EKLENMEDİ.
- [ ] **AI Asistan — kalan kapasite sınırı:** ücretsiz katman yine site geneli
  8000 token/dk + **1000 istek/gün**. Trafik artarsa: Groq ücretli katman
  (kullanıcı kararı) ya da `reasoning_effort=low` (kalite ödünü).
- [x] ~~`manage.py test forum` 0 test buluyor~~ — ÇÖZÜLDÜ: proje pytest
  kullanıyor (`conftest.py`, `analizdestek/test_settings.py`); doğru komut
  `docker compose exec web python -m pytest forum/tests.py` (61 test).
- [x] **Başarısız test: `test_yoktez_job_daily_limit_normal_user`** — ÇÖZÜLDÜ
  (25 Eylül 2026): test eskimişti; limit fa1c281 (18 Mayıs 2026) ile bilinçli
  olarak herkese 3 yapılmış. Test 3'e güncellendi → pytest 61/61.
- [x] **Ölü kod temizliği** — TAMAMLANDI (25 Eylül 2026, kullanıcı onayı):
  forum/templates/registration/password_reset_{form,done,confirm,complete}.html
  (templates/registration gölgeliyordu — get_template ile doğrulandı),
  forum/ai_service.py (import yok), istatistik/tool_base.html (referans yok).
  Sayfalar 200, pytest 61/61. `forum/tasks.py` (Celery, bağlı değil — analizus.md
  §23) bu tura dahil edilmedi.
- [x] **Gizlilik tablosu mobilde yatay kayıyor** — ÇÖZÜLDÜ (25 Eylül 2026): mobil önce kart düzeni (data-label ile sütun adı, 3 dil), 576px+ tablo; 390/1100px ekran görüntüsüyle doğrulandı.
- [x] **Float buton çakışması** — ARTIK YOK (25 Eylül 2026 doğrulandı): kodda
  sabit (position:fixed) duran tek buton AI Asistan; WhatsApp/Destekçi sabit
  butonları kaldırılmış (sayfa içi link olarak duruyor). 390px ve 700px ekran
  görüntüsünde çakışma yok. (Alttaki "AYRI BULGU" notu tarihçe.)

**B. Kullanıcı / avukat kararı bekleyen**
- [ ] Gizlilik metnine eklenecekler: ABD aktarım güvencesi (SCC/DPF), KVKK
  md. 9 bildirimi, GA saklama süresi, AB temsilcisi (md. 27) — "Gizlilik
  metnine eklenecekler" maddesi.
- [ ] Etik Protokolü: 4. ve 7. maddeler yalnızca TCK/KVKK'ya atıf (GDPR?),
  başlık "Akademik Etik Protokolü" yeni konumlandırmayla uyumsuz.
- [ ] Avukat kontrolü — EN/DE canlıya açılmadan önce (gizlilik + etik).
- [x] **"Türkiye/Türkçe" vurgusu genelleştirildi** (25 Eylül 2026, kullanıcı
  onayı): ana sayfa alt başlığı + og/twitter → "Uçtan uca analiz ekosistemi…",
  AI Asistan/blog/forum/Tez Analizi açıklamaları, forum kategori açıklaması,
  AI talimatı son satırı; Hakkımızda "Türkçe Arayüz" satırı KALDIRILDI.
  Olgusal olanlar korundu (TR Dizin/YÖK/19 Türk üniversitesi, KVKK/TCK, Türkçe
  NLP dersi, transkript dil listesi, blog yazı içerikleri).
- [x] **"Tez" vurgusu genelleştirildi** (25 Eylül 2026, kullanıcı onayı, 14 madde):
  varsayılan meta + keywords, ana sayfa JSON-LD (Tez Danışmanlığı → Araştırma
  Danışmanlığı) + AI kartı, Hangi Test/AI Asistan/blog/forum/bölüm/örneklem/
  uzman dizini/başarı hikayeleri açıklamaları; forum açıklamasındaki kaçak
  "Ücretsiz, Türkçe." da düzeltildi. E-posta imzası zaten "Araştırma ve Analiz
  Platformu"ydu; doğrulama + hoş geldin e-postası altlığı "© 2024 … Akademik
  Analiz ve Veri Bilimi Forumu" → "© {yıl} … Araştırma ve Analiz Platformu".
  Korunan: öğrenci segmentine özel "Tezin için:", onboarding "Akademik Destek",
  tez araçları. JSON-LD geçerli, pytest 61/61.
- [x] **"Tez için" kalıbı** — genelleştirildi (Adım 6 altındaki maddeye bak).
- [x] **Adım 6 — TAMAMLANDI (25 Eylül 2026). KARAR: hepsi, aşamalı (ekran + PDF birlikte); PDF başlığı
  "Tezinde Nasıl Raporlarsın?" → "APA Formatında Raporlama"** (25 Eylül 2026)
  - [x] Aşama 1 altyapı: dil işçi thread'ine taşındı (`_pending_job_languages`,
    run_job yakalar, `_execute_job` translation.override) — gerçek kuyrukla
    TR/EN/DE doğrulandı; job_runner (6) + data_validator (9) mesajları EN/DE;
    Likert uyarısındaki numpy repr sızıntısı ("np.int64(9)") düzeltildi.
  - EK ÖLÇÜM: şablonlardaki JS (ekranda APA cümlesi üretimi) 46 metin / ~790
    kelime, 18 şablon — ilk ölçüm yalnız .py taradığı için eksikti; partilere dahil.
  - [x] Parti 2 (25 Eylül 2026): normallik, betimsel, cronbach, korelasyon,
    orneklem — servis (ekran+PDF) + şablon JS; APA cümleleri {süslü} yer
    tutucu ile Python/JS ORTAK msgid ({% trans %} %-işaretini kaçışladığından
    %(x)s ortak olamaz). Yan düzeltmeler: "p = < .001" → "p < .001"; Cronbach
    cümlesinde etiket aralıksız + TR'ye duyarlı küçük harf ("İyi".lower() →
    "i̇yi" sorunu); 3b-2d'den kalan kaçaklar (örneklem "Orta etki…" ×3,
    "Hesapla" butonu, cronbach "' madde'"). Doğrulama: PDF metni (pdftotext)
    EN'de TR kalıntı yok; 15 sayfa JS node --check + APA node'da üretildi.
    NOT: AST tarayıcı Türkçe harfsiz metinleri ("Yorum", "Madde", "Hesapla")
    kaçırıyor — kalan partilerde dosyalar ayrıca gözle okunmalı.
  - [x] Parti 3 (25 Eylül 2026): ttesti, anova, mann_whitney, kruskal_wallis,
    ki_kare — servis + şablon JS (ANOVA JS tablo başlıkları, Post-Hoc başlığı,
    ki-kare "Toplam" dahil); parça birleştirmeli sonuç/APA cümleleri tam cümle
    msgid'lerine bölündü; JS'te de "p < .001" (pStr). **DOĞRULUK HATASI
    DÜZELTİLDİ:** eşleştirilmiş t-testinde yön tersti (son > ilk iken "ölçüm
    azalmıştır" diyordu). Ki-kare tablosunda 'Toplam' → pgettext('tablo')
    (bağlamsız çevirisi "Total of"). EN PDF'lerde TR kalıntı yok; 15 sayfa JS OK.
  - [x] Sonuç cümlelerinde "p = 0.0000" → "p < .001" (7 servis, 18 msgid; p ifadesi
    tek parça) — 25 Eylül 2026.
  - [x] Wilcoxon yön kontrolü — hata yok (Parti 4).
  - [x] Parti 4 (25 Eylül 2026): wilcoxon, friedman, tekrarli_anova, afa —
    servis + şablon JS. Wilcoxon yönü DOĞRU (diff = col2 − col1). Düzeltilen
    önceden var hatalar: APA'da "p 0.123" (eşittir eksikti) — 4 araç, ekran+PDF;
    **AFA: Bartlett anlamsızken de "anlamlı bulunmuştur" yazıyordu** (PDF+ekran);
    faktör sayısı elle seçilince de "Özdeğer > 1 kriteri" diyordu; ekran ve PDF
    APA metinleri farklıydı → tek ortak metin (afa._apa_text + JS). Yüzde biçimi
    dile göre ('%%%(value)s' / '%{value}' msgid'leri: %62.3 / 62.3% / 62.3 %).
    Kaçaklar: wilcoxon "(Medyan)", afa "madde". EN PDF TR kalıntı yok; 12 sayfa JS OK.
  - [x] Parti 5 yüzde kalıpları düzeltildi.
  - [x] Parti 5 (25 Eylül 2026): lineer_regresyon, lojistik_regresyon,
    karar_agaci, svm — servis + şablon JS. **Tuzak düzeltildi:** JS ve PDF sabit
    terimi `c.name !== 'Sabit'` ile tanıyordu (Türkçe harfsiz olduğu için
    karşılaştırma taramasında görünmedi) → `is_const` bayrağı; ad artık
    çevriliyor (Intercept/Konstante). Önceden var: APA'da "p = < .001",
    yüzdeler karışık ("85.2%" tabloda / "%85.2" APA'da) → dile göre tek biçim
    (betimsel frekans tablosu dahil). Kaçaklar: "Kriter:", "Yaprak:", "Polinom".
  - [x] **ADIM 6 TAMAMLANDI (25 Eylül 2026):** 20 servis + 18 şablon; son tam
    taramada kalan yalnız yöntem/terim adları (Bonferroni, Pearson, Wald…),
    HTML etiketleri ve dosya yolları.
  - [x] Ekran APA başlığı → "APA Formatında Raporlama" (18 şablon) + "Tez için"
    kalıbı genelleştirildi (4 araç açıklaması, ana sayfa açıklaması + SSS sorusu,
    AI Asistan örnek sorusu, betimsel tanıtım metni) — 25 Eylül 2026. Korunan:
    eğitici metinlerdeki olgusal "tezlerde ve raporlarda", tez tarama aracı,
    öğrenci segmentine özel öneri.
  Ölçüm notu: istatistik
  servislerinde (20 dosya) çeviriye işaretlenmemiş Türkçe: EKRAN 221 metin /
  ~1380 kelime (APA cümleleri, etki yorumları, veri uyarıları, hata mesajları),
  PDF 300 metin / ~1190 kelime (başlık/tablo etiketleri). Türkçe değerle mantık
  karşılaştırması YOK (güvenli). Mimari bulgular: (1) PDF ekran metinlerini
  yeniden kullanıyor (`Paragraph(result['conclusion'])`) → yalnız ekran
  çevrilirse PDF karışık dilli olur; (2) analiz işçi thread'inde çalışıyor
  (`job_queue.enqueue`) → dil thread'e taşınmalı (aktif dil thread-local).
  PDF başlığında "Tezinde Nasıl Raporlarsın?" (tez vurgusu) var. Tarayıcı:
  scratchpad `scan_tr.py` (AST; docstring/log/gettext hariç).
- [ ] "Ufak tefek aksamalar" listesi kullanıcıdan alınacak (cilalama turu).

- [x] **GÜVENLİK — `_verify_cron_secret` beklenen anahtarı loga yazıyor** —
  DÜZELTİLDİ (25 Eylül 2026): anahtar hiç loglanmıyor (yalnızca yol + IP),
  `hmac.compare_digest`, env yoksa varsayılan anahtar yalnızca DEBUG'da
  geçerli (prod'da red + error log). pytest: 60/61 (tek hata yoktez — önceden
  bilinen). NOT: canlıdaki mevcut loglarda eski anahtar düz metin duruyor →
  anahtar yenileme maddesi hâlâ geçerli.
- [ ] **CRON_SECRET_KEY yenileme:** 25 Eylül 2026'da anahtarın TAMAMI
  nginx log çıktısıyla sohbete yapıştırıldı (yerel oturum). Ayrıca anahtar
  `?secret=` ile URL'de gittiği için nginx access loguna düz metin yazılıyor —
  yenilerken `X-Cron-Secret` header'ına geçmek de değerlendirilmeli. Yenilenirse
  `.env` + Hetzner crontab'daki TÜM `/api/cron/*` satırları birlikte güncellenmeli.

**C. Canlıya alma (yalnızca kullanıcı "merge et" deyince)** — 25 Eylül 2026 ölçümü:
dev, main'den 78 commit ileride, main'de dev'de olmayan commit yok (fast-forward);
requirements.txt değişmedi (--build GEREKMEZ); settings.py: 3 middleware +
hreflang context processor + 'de' dili; .mo dosyaları git'te (compilemessages
şart değil); container başlarken deploy.sh migrate + collectstatic çalıştırır
(yine de elle çalıştırıp çıktıyı görmek önerilir). Staging (analizus-dev.onrender.com)
en son dev'i çalıştırıyor, 200.
**Gerekli migration'lar: forum 0153 (SiteSettings.feature_multilingual, şema),
0154 (Profile.preferred_language, şema, varsayılan 'tr' — mevcut kullanıcılar
TR), 0155 (anonim kullanıcı adları, veri, geri alınabilir).** Başka uygulamada yok.
- [x] 0. Canlı DB yedeği (kullanıcı aldı, 25 Eylül 2026): `docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > /root/yedek_$(date +%F).sql`
- [x] 1. main ← dev fast-forward merge + push (132327f, 25 Eylül 2026)
- [x] 2. Hetzner: git pull
- [x] 3-4. migrate + collectstatic — container yeniden başlarken deploy.sh uyguladı (0153-0155 applied 2026-09-25 21:07 UTC; 0152 23 Temmuz → staging canlı DB'yi kullanmıyor, doğrulandı)
- [x] 5. web + nginx yeniden başlatıldı
- [x] 6. Kontroller (curl): tüm sayfalar 200, /en/ 404 (bayrak kapalı), inter.css + font 200, log temiz; canlı HTML: yeni og açıklaması, Yandex yok, Google Fonts yok, GDPR bölümü var. Tarayıcıda AI Asistan testi kullanıcıda. Eski not: ana sayfa/giriş/araç sayfası 200; çerez banner'ı (GA ID varsa);
      AI Asistan bir soru; `showmigrations` hepsi [X]; nginx/web log hata yok.
- [ ] 7. Admin'de `feature_multilingual` aç — AVUKAT KONTROLÜNDEN SONRA (kapalıyken EN/DE sayfaları 404, TR etkilenmez).
- [ ] **Canlıda `GOOGLE_ANALYTICS_ID` TANIMLI DEĞİL** (25 Eylül 2026, canlı HTML'de GA script/banner yok; deploy öncesi de yoktu) → sitede hiç analiz aracı çalışmıyor. İstenirse .env'e eklenir, banner otomatik devreye girer. Eski not: Canlıda kontrol: `GOOGLE_ANALYTICS_ID` tanımlı mı (banner ona bağlı);
  canlı `GROQ_API_KEY` ile gpt-oss-120b yanıt veriyor mu.
- [ ] Yandex Metrica hesabı/sayacı kapatılabilir (kod kaldırıldı).
- [ ] **Deploy sonrası (bayrak kapalı) — arama/analitik panelleri:**
  Google Search Console: sitemap.xml yeniden gönder; ana sayfa + gizlilik için
  URL denetimi → dizine eklenmeyi iste; 1-2 hafta "Sayfalar" raporunda 404/5xx
  artışı izle. GA4: Yönetici → Veri ayarları → Veri saklama süresini kontrol et
  (2/14 ay → gizlilik metnine yazılacak), Google sinyalleri kapalı mı; onay
  banner'ı nedeniyle trafik düşüşünü açıklama (annotation) olarak not et.
  Bing Webmaster Tools: site doğrulandı mı (BING_SITE_VERIFICATION ya da GSC'den
  içe aktar), sitemap gönder. Canlı .env'de GOOGLE/BING_SITE_VERIFICATION dolu mu.
- [ ] **feature_multilingual açıldıktan sonra:** GSC + Bing'e sitemap'i yeniden
  gönder (artık /en/ /de/ + hreflang içerir); /en/ ve /de/ ana sayfa + birkaç
  araç sayfası için URL denetimi → dizine eklenmeyi iste; oluşturulan HTML'de
  hreflang ve <html lang> doğrula (GSC'de ayrı hreflang raporu yok).
- [ ] 8. `feature_agentic_landing` flag'i merge sonrası elle açılmalı (önceki
  turdan hatırlatma).


**Tamamlanan:** Adım 1 (ayarlar), 2 (URL yapısı + 3 kritik bug), 3a
(base+footer), 3b-1 (register+login), 3b-2a (home.html), 3b-2b
(makaleanaliz/openalex/semanticscholar), 3b-2c (proje talebi/AI
çözümler/eğitim), 4 — ilk çeviri turu (601 metin), 5a (dil seçici +
admin flag), Market arayüzü (commit `52bd6dc`, 176 metin daha — bkz.
"Kapsam Kararı"). Detaylar aşağıdaki ilgili maddelerde.

**3b-2d TAMAMLANDI (23 Eylül 2026):** `/analiz/` hub + 18 araç şablonu +
landing view metinleri + yükleme/önizleme hata mesajları (commit'ler
`ddff5d4`, `e363169`). `tool_base.html` ölü dosya (hiçbir yerden
kullanılmıyor). Kullanıcı kararıyla APA cümleleri + sunucu sonuç
metinleri Türkçe bırakıldı (Adım 6'da PDF ile birlikte).

**23 Eylül 2026 devamı — TAMAMLANDI:** base.html kalıntıları (skip-link,
quiz/profil/hikaye modalları, AI widget), DE terim birliği (Ausschreibung →
Auftrag), `seo_content.py` rehberi (18 araç, 176 metin), footer "Bize Destek
Ol" + bağış modalı (paket adları `gettext_noop` ile), footer alt satırı
"Araştırma ve Analiz Platformu", yeni slogan "Veriden karara…".
EN/DE araç sayfalarında kalan Türkçe: yalnızca yasal adres satırı (kasıtlı).

**24 Eylül 2026 — TAMAMLANDI (kullanıcı isteği: eğitim kataloğu, kayıt/giriş, e-postalar):**
- Eğitim kataloğu (`training_catalog.py`, 362 metin) — `56c597f`
- Kayıt formu hataları + kayıt mesajları — `9bfad5d` (giriş formu hataları
  Django kataloğundan zaten çevrili)
- E-postalar (alıcının dilinde): E1 `Profile.preferred_language` +
  middleware + `forum/i18n_utils.py` (`91154b0`) → E2 hesap e-postaları →
  E3 kullanıcı bildirimleri (admin bildirimleri TR sabit) → E4 Makale
  Analiz/OpenAlex/Semantic Scholar sonuç e-postaları → E5 destek/eğitim/
  proje talebi onayları (`0cc2b4d`).
  ⚠ **Canlıya alırken MIGRATION 0154 zorunlu:** `docker compose exec web
  python manage.py migrate` — mevcut tüm kullanıcılar 'tr' etiketlenir.
  Kasıtlı TR kalan: yoktez/trdizin/tezanaliz/bibliometrics e-postaları,
  TXT/PDF sonuç dosyası içerikleri (Adım 6), havale açıklaması.

**Menüden erişilen tek dilli sayfalar (kullanıcı isteği, 24 Eylül 2026):**
Hiçbiri i18n_patterns'te değil ve şablonları işaretlenmemiş — her biri için
URL taşıma + şablon + sitemap(static-i18n) + robots.txt.
- [x] Hakkımızda (+ "Neden Analizus?") — TR metin güncellendi (11 madde,
  kullanıcı onayı) + EN/DE — `fc543cc`
- [x] İletişim — form + flash mesajları EN/DE — `fc543cc`
- [x] Hangi Test? — karar ağacı (233 metin) + SSS JSON-LD + araç linkleri
  dile duyarlı. Açık soru: meta açıklama "Tezin için…" (tez vurgusu) TR'de
  aynen bırakıldı
- [x] **AI Asistan** — TAMAMLANDI (24 Eylül 2026): `ai-asistan/` sayfası
  urls_i18n'e taşındı (API `/api/ai/chat/` öneksiz kaldı — doğrulanmamış
  kullanıcı `/api/` muafiyeti), sayfa + limit/hata mesajları EN/DE. Widget
  `lang` gönderiyor (tr/en/de dışı → tr). EN/DE'de sistem talimatının başına
  ve sonuna dil kuralı ekleniyor (TR talimatı birebir aynı). Yanıttaki
  platform linkleri `translate_url` ile dil önekini alıyor (/en/hangi-test/);
  tek dilli sayfalar (/istatistik/…, /forum/) öneksiz kalıyor. Gerçek API
  testi (gpt-oss-120b ile, betikte geçici): EN/DE yanıtlar tamamen hedef
  dilde. İlk denemede DE gövde Türkçe kalmıştı → dil kuralı başa da eklendi.
  Açık soru: TR meta açıklama "anında Türkçe yanıt… tez yazımı" (EN/DE'de
  "Türkçe" düşürülerek çevrildi).
- [x] **ACİL — AI Asistan hiç yanıt vermiyor** — ÇÖZÜLDÜ (24 Eylül 2026): kullanıcı kararı "ücretsiz en yüksek limitli model" → ölçüldü (API yanıt başlıkları): gpt-oss-120b = gpt-oss-20b (8000 TPM, 1000 RPD, 131K bağlam) > qwen3.8-27b (16K çıktı) > allam-2-7b (4K bağlam); `openai/gpt-oss-120b` seçildi, uçtan uca test OK. Eski not:
  Groq `llama-3.3-70b-versatile` modelini artık tanımıyor (404, 24 Eylül
  2026). Hesapta erişilebilen: openai/gpt-oss-120b, openai/gpt-oss-20b,
  qwen/qwen3.8-27b… Model seçimi kullanıcı kararı. Not: gpt-oss-120b
  ücretsiz katmanda 8000 token/dk limitine takılıyor (istek başına ~2900
  token: talimat + 1024 yanıt payı → dakikada ~2-3 soru).
- [x] **A. Çerez onayı + Yandex kaldırma** — TAMAMLANDI (24 Eylül 2026,
  kullanıcı kararı: Yandex kaldır). `partials/cookie_consent.html`: Reddet /
  Kabul et (eşit boyut), `ax_cookie_consent` çerezi 180 gün; GA yalnızca
  onayla yüklenir (`axLoadAnalytics`), onay geri çekilince _ga* silinir;
  eski `_ym_*` çerezleri temizlenir; footer'da "Çerez ayarları". GA ID
  yoksa banner/bağlantı hiç çıkmaz. `yandex-verification` meta etiketi
  (yalnızca Webmaster sahiplik doğrulaması, veri göndermez) bırakıldı.
- [x] **B. Google Fonts self-host** — TAMAMLANDI (24 Eylül 2026): Inter
  değişken font (latin + latin-ext, Google Fonts v20) `static/fonts/inter/`
  + OFL.txt, `static/css/inter.css`; base.html ve admin_theme_v2.css artık
  yerelden yüklüyor, gstatic preconnect / googleapis dns-prefetch kaldırıldı.
  Net-log ile doğrulandı: sayfadan fonts.googleapis/gstatic isteği yok.
  Deploy'da `collectstatic` şart (yeni statik dosyalar).
- [x] ~~ÖNEMLİ — Hesap silme vaadi uygulanmıyor~~ — YANLIŞ BULGU (25 Eylül 2026 düzeltildi): cron mevcut ve çalışıyor; bkz. AÇIK İŞLER'deki "Hesap silme cron'u kullanıcı kararlarına uydurulacak".
- [x] **Küçük i18n kaçağı (B sırasında görüldü)** — ÇEVRİLDİ (88c10d5): ana sayfa hero'sundaki test
  çipleri "t-testi · korelasyon · regresyon" EN/DE'de Türkçe kalıyor.
- [x] **C. Gizlilik sayfası: KVKK çevirisi + GDPR bölümü** — TAMAMLANDI
  (24 Eylül 2026, kullanıcı onayı): TR metni güncellendi (tablo: AI soruları,
  talep formları, zorunlu/analiz çerezi ayrımı; alıcılar adıyla; çerez
  bölümü banner'a göre; yeni 7. GDPR bölümü; sabit tarih 24.09.2026), EN/DE
  çevrildi, URL i18n'e + StaticI18nSitemap'e taşındı. [KARAR] cümleleri ve
  "30 gün içinde silinir" BİLEREK çıkarıldı — aşağıdaki maddeye bak.
- [ ] **Gizlilik metnine eklenecekler — karar/uygulama bekliyor:**
  - **"Hesap silme talebinden sonra 30 gün içinde silinir"** — işlev zaten
    çalışıyor (24 Eylül bulgusu yanlıştı); cron kullanıcı kararlarına
    uydurulunca GDPR "Saklama süreleri" maddesine geri eklenir.
  - **AB dışı aktarım güvencesi** (Google, Groq → ABD): SCC ve/veya AB-ABD
    Veri Gizliliği Çerçevesi — sağlayıcı sözleşmeleri kontrol edilmeli.
  - **KVKK md. 9 yurt dışı aktarım** (2024 değişikliği): standart sözleşme +
    KVK Kurumu'na bildirim yapıldıysa bölüm 3'e cümle eklenir.
  - **Google Analytics saklama süresi** (GA hesabındaki ayar: 2 / 14 ay).
  - **AB temsilcisi (GDPR md. 27)** — avukat görüşü.
  - Avukat kontrolü EN/DE canlıya açılmadan önce önerildi.
  Olgular: Olgular: Hetzner (DE), AWS S3
  eu-north-1 (SE), Groq (ABD, AI soruları), Google Analytics (ABD, onaylı),
  e-posta Gmail üzerinden (Google, ABD; alan adı hosting.com.tr), Render
  yalnızca test verisi (metne girmez). "Son güncelleme" `{% now %}` → sabit
  tarih. Açık: AB temsilcisi (GDPR md. 27), somut saklama süreleri.
- [x] **Gizlilik/KVKK** — çevrildi (C paketi, 3f648ee) (`gizlilik_politikasi.html`) — hukuki metin;
  çeviri kullanıcı onayıyla yayına girer (etik protokol modalıyla aynı tur)

**Kayıt akışı — yapılacaklar (kullanıcı isteği, 23 Eylül 2026):**
- [x] **Giriş/kayıt sayfasında dil seçici yok** (kullanıcı raporu, 24 Eylül
  2026) — TAMAMLANDI: `templates/partials/auth_lang_switcher.html` (set_language
  formu, `features.multilingual` kapalıysa gizli) iki sayfanın `.top-bar`'ına
  eklendi. Mobilde top-bar akışa alındı (`position: static`) ve form
  `margin-block: auto` ile ortalandı — uzun kayıt formunda üst kısım artık
  kırpılmıyor.
- [x] **Kullanım Şartları / Akademik Etik Protokolü modalı** — TAMAMLANDI
  (24 Eylül 2026): 7 maddelik gövde `blocktrans trimmed` ile işaretlendi,
  EN/DE çeviri kullanıcı onayıyla ("devam") yayına alındı. Açık kalan
  (hukuki karar, çeviri değil): 4. ve 7. maddeler yalnızca TCK/KVKK'ya atıf
  yapıyor — AB kullanıcıları için DSGVO/GDPR atfı eklenip eklenmeyeceği;
  modal başlığı "Akademik Etik Protokolü" yeni konumlandırmayla uyumsuz;
  yayın öncesi avukat kontrolü önerildi.
- [x] **Kayıt sonrası akış tek dilli** — TAMAMLANDI (24 Eylül 2026):
  verify-email, verification-pending, resend-verification, onboarding
  (forum/urls.py → urls_i18n.py) ve 4 şifre sıfırlama URL'i i18n_patterns'e
  alındı (TR adresleri değişmedi, eski linkler çalışır). Şablonlar, view
  mesajları, SEGMENT_CHOICES (gettext_lazy — migration YOK, `makemigrations
  --check` doğrulandı) ve middleware doğrulama uyarısı EN/DE. Şifre sıfırlama
  sayfalarına dil seçici + dinamik `<html lang>` + login'deki mobil düzeltme.
  Doğrulama e-postasındaki link artık alıcının dil önekiyle (`reverse()` +
  `recipient_language`). robots.txt: /en|de/accounts/, /en|de/onboarding/.
  Not: `forum/templates/registration/password_reset_*.html` kopyaları
  `templates/registration/` tarafından gölgeleniyor (ölü kod, dokunulmadı);
  `_check_and_award_trust_badge` mesajı hâlâ Türkçe (nadir, kapsam dışı).

**Not (kullanıcıya sorulacak):** ana sayfa og/twitter açıklaması hâlâ
"Türkiye'nin analiz ekosistemi…" diyor — yeni sloganla aynı konumlandırma
sorunu (yalnızca Türkiye vurgusu); değiştirilsin mi?

**Sonra:** 6 (Python tarafı — kapsam kararı bekliyor), 7 (deploy).

**Sona bırakılan (kullanıcı kararı, 22 Eylül 2026):** "Ufak tefek
aksamalar" — somut liste henüz çıkarılmadı; 3b-2d/4 bittikten sonra
kullanıcıya "hangi ufak aksamalar" diye sorulacak, ayrı cilalama turu.

**Açık kapsam kararı bekliyor:** Adım 6 (Python tarafı metinler —
istatistik hata mesajları, PDF rapor içerikleri, SEO_GUIDES,
training_catalog, TOOL_CATEGORIES, quiz bankası).

**Her makemessages sonrası hatırlatma:** fuzzy girişleri temizle
(compilemessages fuzzy'leri sessizce atlar); aynı msgid'in hem tekil hem
çoğul kullanımı xgettext uyarısı verir — farklı değişken adı
(`counter`) ile ayrıştır.

---

## Kapsam Kararı

**Dahil (EN + DE çevrilecek):**
- Ana sayfa, navbar, footer, kayıt/giriş akışı
- Makale Analiz (`makaleanaliz/`), OpenAlex (`openalex/`), Semantic
  Scholar (`semanticscholar/`) — uluslararası kaynaklar, Türkiye'ye özgü değil
- 18 istatistik aracının açıklama/giriş sayfaları (evrensel yöntemler):
  ttesti, anova, mann_whitney, kruskal_wallis, ki_kare, korelasyon,
  cronbach, normallik, betimsel, orneklem, lineer_regresyon,
  lojistik_regresyon, friedman, tekrarli_anova, karar_agaci, svm, afa,
  wilcoxon

**Kapsam dışı (Türkiye'ye özgü / UGC / karar bekliyor):**
- YÖK Tez (`yoktez/`), TR Dizin (`trdizin/`), Tez Analiz (`tezanaliz/`)
  — YÖK Tez tabanlı, Türkiye'ye özgü
- OAI-PMH (`oaipmh/`) — 17 aktif arşivin hepsi Türk üniversitesi
- Forum — UGC, Türkçe topluluk
- ~~Market/iş ilanları~~ → **YALNIZCA ARAYÜZ DAHİL edildi** (23 Eylül 2026
  kullanıcı kararı): `market/*` URL'leri `forum/urls_i18n.py`'ye taşındı;
  şablonlar + pazar view'larındaki flash mesajları + ilan/teklif form
  etiketleri çevrildi. Çevrilmeyen (kasıtlı): ilan/teklif içerikleri (UGC),
  ₺ fiyatlar, `promote_job_iban.html` (TL/IBAN ödeme akışı), otomatik
  DM/bildirim metinleri (alıcının dil tercihi bilinmiyor). Ayrıca çevrildi:
  `forum/models.py` → `FreelanceJob`/`JobProposal` durum etiketleri
  (`gettext_lazy`, migration gerekmedi — `makemigrations --check` temiz) ve
  `Profile.can_post_job*/can_propose()` sebep metinleri. Rütbe adları
  (`get_rank_display`, ör. "Çaylak") ve rozet adları (DB) Türkçe kalıyor.
- Blog — mevcut içerik Türkiye SEO'suna göre üretilmiş
- ~~Proje talebi / Danışmanlık / Eğitim landing sayfaları~~ → **DAHİL edildi**
  (22 Eylül 2026 kullanıcı kararı), aşağıdaki dosya listesine eklendi

## Uygulama Adımları (sırayla, her adım sonrası onay bekle)

- [x] **1. Ayarlar:** `analizdestek/settings.py` → `LANGUAGES` listesine
  `('de', _('German'))` eklendi (22 Eylül 2026)
- [x] **2. URL yapısı:** TAMAMLANDI (22 Eylül 2026). `analizdestek/urls.py`
  → `i18n_patterns(..., prefix_default_language=False)` ile sarıldı:
  `forum.urls_i18n` (yeni dosya — home/register/proje-talebi/ai-cozumler/
  egitim*), `makaleanaliz.urls`, `openalex.urls`, `semanticscholar.urls`,
  `istatistik.urls_analiz`. Kapsam dışı app'ler (yoktez, trdizin, tezanaliz,
  oaipmh, bibliometrics, transcript, istatistik.urls legacy polling, tarama,
  forum.urls geri kalanı, admin, sitemap, robots.txt) prefix dışında kaldı.
  - `forum/urls.py` → 7 path (`home`, `register`, `proje_talebi`,
    `ai_cozumler`, `egitim`, `egitim_talebi`, `egitim_detay`) yeni
    `forum/urls_i18n.py`'ye taşındı.
  - **Bulunup düzeltilen regresyon:** `login` adı hem `django.contrib.auth.urls`
    (dahili) hem `custom_login`'de (rate-limited) kullanılıyor —
    `reverse()` aynı isimde son kayıt edileni döndürüyor. `login`'i
    i18n_patterns'e alınca dahili view kazanmaya başladı. Düzeltme: `login`
    orijinal konumunda (accounts/ include'undan SONRA), prefix'siz bırakıldı
    — çeviri için soruna yol açmaz, `LocaleMiddleware` prefix'siz sayfalarda
    da dil çerezine bakar.
  - **Bulunup düzeltilen 3 sabit-kodlanmış link** (i18n_patterns'e alınan
    URL'lere `{% url %}` yerine `/analiz/` veya `/register/` hardcode
    edilmişti — EN/DE sayfalarda tıklanınca kullanıcıyı sessizce Türkçe'ye
    geri atıyordu): `templates/base.html` (2× navbar `/analiz/` linki + 1×
    quiz "Üye ol" linki), `istatistik/templates/istatistik/
    analiz_console_base.html` ("İlgili Araçlar" linki).
  - **Ertelenen (düşük risk, AJAX/JSON, görünür metin değil):**
    `fetch('/analiz/clear-session/')`, `makaleanaliz/results.html`
    `STATUS_URL`, `openalex`/`semanticscholar` landing'lerindeki
    `/status/` polling fetch'leri — hardcoded kalsa da sadece job durumu
    döndürüyor, dil karışıklığı görünür değil. İstenirse adım 6'da ele alınır.
  - **Doğrulama:** `manage.py check` temiz; `reverse()` ile tr/en/de için
    `home`/`login`/`analiz_home`/`register`/`proje_talebi` test edildi;
    local runserver ile `/`, `/en/`, `/de/`, `/analiz/`, `/en/analiz/ttesti/`,
    `/de/openalex/`, `/de/semantic-scholar/`, `/login/`, `/forum/`,
    `/yoktez/`, `/istatistik/ttesti/` (301→/analiz/ttesti/, değişmedi)
    curl ile 200/301 olarak doğrulandı; ana sayfa HTML çıktısında `/en/`
    için navbar linklerinin doğru prefix aldığı görüldü.
- [x] **3a. `templates/base.html` + `templates/partials/footer.html`:**
  TAMAMLANDI (22 Eylül 2026). Navbar (desktop dropdown'lar, mobil drawer,
  auth butonları, hamburger/close/arama/dil-seç aria-label'ları), `<title>`/
  meta description varsayılanları, footer (marka tagline, Araçlar/Topluluk/
  Kurumsal kolonları, alt satır copyright+link) `{% trans %}` ile işaretlendi.
  **Kasıtlı olarak İŞARETLENMEDİ:** "Forum"/"Blog" (dilller arası aynı
  kelime), footer "Akademik Kaynaklar" kolonu (Google Scholar/DergiPark/
  Semantic Scholar/YÖK Tez Merkezi — marka isimleri), footer "Bize Destek
  Ol" + bağış modalı (TL/IBAN havale bazlı ödeme — kapsam dışı, proje
  kuralı: ödeme sistemi belirsiz, sormadan genişletme), fiziksel adres,
  ana sayfadaki quiz limit-aşımı JS metni (İstatistik Arena/quiz soru
  içeriği zaten Türkçe kalacak, forum-bitişik özellik).
  Doğrulama: `manage.py check` temiz, local Docker'da restart+curl ile
  sayfa 200 dönüyor, `{% trans %}` sarılan metinler `.po` derlenmediği için
  (beklendiği gibi) hâlâ Türkçe kaynak metin olarak görünüyor.
- [x] **3b-1. `templates/forum/register.html` + `forum/templates/registration/login.html`:**
  TAMAMLANDI (22 Eylül 2026). İkisi de `base.html`'i extend ETMEYEN bağımsız
  sayfalar (özel split-screen tasarım) — `{% load i18n %}` eklendi,
  `<html lang="tr">` → `<html lang="{{ LANGUAGE_CODE }}">`, form label/hint/
  buton metinleri `{% trans %}` ile işaretlendi. **Kasıtlı işaretlenmedi:**
  register.html'deki "Akademik Etik Protokolü" modalının 7 paragraflık
  metni — KVKK ve Türk Ceza Kanunu'na doğrudan atıf yapıyor, EN/DE
  kullanıcılar için hukuken anlamsız/yanıltıcı olur; ayrı bir hukuki karar
  gerektirir (GDPR'a uyarlanmış ayrı metin mi, yoksa sadece Türkçe mi
  kalacak — henüz karar yok).
  Doğrulama: `manage.py check` temiz, `/login/` ve `/register/` 200,
  `/en/login/` 404 (beklenen — login kasıtlı olarak i18n_patterns dışında,
  bkz. yukarıdaki bug notu).
- [x] **3b-2a. `forum/templates/forum/home.html`:** TAMAMLANDI (23 Eylül
  2026). **Karar değişikliği (kullanıcı):** ana sayfanın büyük kısmının
  Pazaryeri/Uzman/Quiz içeriği olduğu keşfedildi (kapsam dışı diye
  kararlaştırılan Market özelliği doğrudan ana sayfaya gömülü) — kullanıcı
  "tüm sayfayı çevir" dedi, tutarlılık için TÜMÜ işaretlendi (navbar'da
  uygulanan aynı mantık: hedef sayfa çevrili olmasa bile UI metni çevrilir).
  İşaretlenen bölümler: title/meta, hero, pazar yeri yönlendirme (2 kart),
  nasıl çalışıyoruz (4 adım), istatistik şeridi, güven unsurları, uzman
  vitrini + iş ilanı kartları (statik chrome; `job.title`/`job.description`
  DB içeriği olduğu için dokunulmadı), araştırma konsolu, AI Asistan+Arena
  (statik chrome; quiz soru bankası DB içeriği hâlâ Türkçe), AI çağı bandı,
  SSS (5 soru-cevap), haberler bölümü (statik chrome; blog post içeriği
  dokunulmadı), hero dropzone + quiz JS'teki statik metinler.
  **Kasıtlı atlanan:** JSON-LD structured data (4 `<script type="application/
  ld+json">` bloğu — SEO metadata, ayrı küçük bir iş olarak bırakıldı),
  "Gündemdeki Tartışmalar" include'u (`_gundem_tartismalar.html` — forum
  konuları, dinamik DB içeriği), `q.difficulty` JS karşılaştırma mantığı
  ('Kolay'/'Zor' — CSS class routing için backend-bağımlı, çevrilirse mantık
  bozulur).
  Doğrulama: `manage.py check` temiz, sayfa 200 dönüyor, kalan düz Türkçe
  metin taraması yalnızca marka isimleri (TR Dizin, Cronbach, OpenAlex)
  buldu.
- [x] **3b-2b. `makaleanaliz/results.html` + `openalex/landing.html` +
  `semanticscholar/landing.html`:** TAMAMLANDI (23 Eylül 2026).
  **`order.html` (her iki app'te) KASITLI ATLANDI** — TL fiyatlı sipariş/
  ödeme akışı (IBAN havale benzeri), footer bağış modalıyla aynı kapsam
  dışı kategori (proje kuralı: ödeme sistemi belirsiz, sormadan genişletme).
  Doğrulama: `manage.py check` temiz, `/openalex/` ve `/semantic-scholar/`
  200, kalan Türkçe metin taraması yalnızca CSS `font-family` değeri buldu.
- [x] **3b-2c. `proje_talebi.html` + `ai_cozumler.html` + `egitim.html` +
  `egitim_detay.html` + `egitim_talebi.html`:** TAMAMLANDI (23 Eylül 2026).
  Title/meta blokları, form alanları (label/placeholder/option), SSS
  akordeonları, zaman çizelgeleri, kart metinleri işaretlendi.
  **Kasıtlı atlanan:** `item.title`/`item.summary`/`item.audience`/
  `item.syllabus`/`item.faq` gibi `training_catalog.py`'den (Python) gelen
  DİNAMİK kurs verileri — bunlar adım 6'nın (Python tarafı metinler)
  kapsamına giriyor, şablon seviyesinde çevrilemez. JSON-LD blokları da
  (home.html'deki gibi) kasıtlı atlandı.
  **Bulunup düzeltilen 2. tür hata:** `{% blocktrans %}` içine `{% url %}`/
  `{% if %}` gibi iç içe template tag koymak `TemplateSyntaxError` verir
  (Django blocktrans yalnızca basit `{{ değişken }}` enterpolasyonuna izin
  verir). İki yerde bu hata yapılmıştı (egitim.html, egitim_talebi.html) —
  fark edilip URL'yi `{% url ... as x %}` ile önceden hesaplayıp
  `{{ x }}` olarak geçirme veya cümleyi ayrı `{% trans %}` parçalarına
  bölme yöntemiyle düzeltildi. Tüm dosyalar bu kalıp için ayrıca tarandı,
  başka örnek çıkmadı.
  Doğrulama: `manage.py check` temiz; flag'ler geçici açılıp (sonra
  kapatılıp) `/egitim/`, `/ai-cozumler/`, `/egitim-talebi/`,
  `/egitim/spss-uygulamali/` gerçek render ile 200 test edildi; kalan
  Türkçe metin taraması temiz.
- [ ] **3b-2d. Kalan dosyalar** (18 istatistik şablonu):
  - `istatistik/templates/istatistik/{afa,anova,betimsel,cronbach,
    friedman,karar_agaci,ki_kare,korelasyon,kruskal_wallis,
    lineer_regresyon,lojistik_regresyon,mann_whitney,normallik,
    orneklem,svm,tekrarli_anova,ttesti,wilcoxon}.html`
    (+ ortak `analiz_console_base.html`/`tool_base.html` iskelet metinleri)
- [ ] **4. Çeviri dosyaları:** `django-admin makemessages -l en -l de`
  (mevcut `locale/en/` var, `locale/de/` yeni oluşacak) → `.po` doldur →
  `compilemessages`
- [x] **5a. Navbar dil seçici + dinamik `<html lang>`:** TAMAMLANDI
  (22 Eylül 2026, kullanıcı isteğiyle sıra dışı erken yapıldı — adım 3'ten
  önce test kolaylığı için). `templates/base.html`: desktop navbar'da globe
  ikonlu dropdown + mobil drawer'da TR/EN/DE buton satırı, ikisi de
  `{% get_language_info_list %}` ile `django.conf.urls.i18n`'in `set_language`
  view'ına POST eden mini formlar (`next` = `request.get_full_path`, Django
  `translate_url()` otomatik doğru dil prefix'ine çeviriyor — ayrıca kod
  yazmaya gerek yok). `<html lang="tr">` → `<html lang="{{ LANGUAGE_CODE }}">`.
  - **Kritik tuzak bulundu:** `static/css/navbar.css` **ölü dosya** —
    `base.html` yalnızca `static/css/bundle.css`'i yüklüyor (temmuz 2026'da
    5 kaynak dosya birleştirilip minify edildi, bkz. analizus.md §26).
    CSS eklerken doğru akış izlendi: `navbar.css`'e yeni kurallar eklendi →
    `rcssmin` ile `bundle.css` container içinde yeniden üretildi → `?v=0004`
    → `?v=0005`.
  - **Doğrulama (lokal Docker):** `manage.py check` temiz, `collectstatic`
    ile `staticfiles_data` volume güncellendi, `web`+`nginx` restart edildi,
    curl ile `/`, `/en/`, `/de/` üzerinde dropdown markup + `<html lang>`
    doğru görüldü, `/i18n/setlang/`'e gerçek POST ile `next=/analiz/ttesti/`
    + `language=de` gönderildi → `Location: /de/analiz/ttesti/` +
    `Set-Cookie: django_language=de` doğrulandı (Django'nun `translate_url()`
    mekanizması sorunsuz çalışıyor).
  - **5a-devam (aynı gün, kullanıcı isteğiyle):** (1) dil butonuna seçili
    dili gösteren rozet eklendi (`{{ LANGUAGE_CODE|upper }}`, `.site-nav__
    lang-trigger`/`.site-nav__lang-code` CSS). (2) `forum/middleware.py` →
    yeni `ForceDefaultLanguageMiddleware` (settings.py'de
    `AuthenticationMiddleware`'den sonra, `LocaleMiddleware`'den ÖNCE) —
    çerez yoksa `Accept-Language` header'ını temizler, tarayıcı dili ne
    olursa olsun prefix'siz sayfa hep `tr` açılır. **Araştırılıp Django'nun
    kendi tasarımı olduğu doğrulanan (bug değil) davranış:** `prefix_default
    _language=False` ile çıplak `/` URL'si, `django_language` çerezi ne
    olursa olsun HER ZAMAN varsayılan dili (`tr`) gösterir — Django'nun
    `LocaleMiddleware.process_request`'i bunu kasıtlı yapıyor (bkz. Django
    kaynağı: `language_from_path` yoksa + `i18n_patterns` kullanılıyorsa +
    `prefixed_default_language=False`'sa → `language = settings.LANGUAGE_CODE`
    ile override eder). Kullanıcı dil değiştirince (`/i18n/setlang/` POST)
    `translate_url()` doğru prefix'li URL'ye (`/de/`) yönlendiriyor, oradan
    itibaren tüm `{% url %}` linkleri prefix'i koruyor — sorun yalnızca
    "çerez set edilmişken çıplak `/`'i elle tekrar ziyaret etme" senaryosunda
    ve bu, tek-URL=tek-dil SEO ilkesiyle örtüştüğü için kasıtlı bırakıldı.
    Doğrulama: curl ile Accept-Language:en-US + çerezsiz → tr; `/en/` hâlâ
    çalışıyor; gerçek POST ile `next=/` + `language=de` → `Location: /de/`.
- [x] **5b. Kalan SEO işleri:** TAMAMLANDI (23 Eylül 2026).
  `forum.context_processors.hreflang_alternates` → base.html'de tr/en/de +
  x-default `<link rel="alternate">` (yalnızca i18n_patterns sayfaları:
  translate_url her dilde farklı yol üretirse) + dile göre `og:locale` /
  `og:locale:alternate`. Sitemap: `MultilingualSitemapMixin` (Django
  `i18n`/`alternates`/`x_default`) — static-i18n, istatistik, training,
  tools-i18n; tek dilliler (forum, blog, uzman dizini, yoktez…, ilanlar)
  değişmedi. Hepsi `feature_multilingual`'a bağlı (kapalıyken /en/ 404).
  18 araç şablonundaki sabit TR canonical → `{% url 'analiz_console' %}`.
  robots.txt'ye özel sayfaların /en/ /de/ karşılıkları eklendi.
  Kasıtlı: ilan detayları sitemap'te tek dilli (içerik Türkçe UGC — ince
  kopya içerik riski); sayfa başlığındaki hreflang yine üretilir.
- [ ] **6. Python tarafı metinler:** kapsamdaki app'lerin (istatistik
  servisleri, makaleanaliz, openalex, semanticscholar) view/form hata
  mesajları ve PDF çıktı metinleri — ayrı görev olarak scope'u netleştir
  (PDF font/layout Türkçe karaktere göre ayarlı, `pdf_fonts.py` etkilenir mi
  kontrol edilmeli)
- [ ] **7. Deploy:** dev → Render'da doğrula, sonra kullanıcı onayıyla
  main → Hetzner'de `docker compose exec web python manage.py
  compilemessages` + `restart web` + `restart nginx`

## Bulunup Düzeltilen Kritik Bug (22 Eylül 2026, kullanıcı raporu)

**Belirti:** "de ve tr seçilmiyor, en seçilebiliyor" — `/en/` veya `/de/`
sayfasındayken dil dropdown'undan başka bir dile geçiş çoğunlukla
çalışmıyordu (sessizce aynı sayfada kalıyordu).

**Kök neden:** `path('i18n/', include('django.conf.urls.i18n'))`
`i18n_patterns` dışında (prefix'siz) tanımlıydı. Django'nun
`LocaleMiddleware`'i, prefix'siz HER isteğin aktif dilini zorla varsayılana
(`tr`) çeviriyor (`prefix_default_language=False` tasarımının bir parçası —
bkz. yukarıdaki "5a-devam" notu). `/i18n/setlang/`'in KENDİSİ prefix'siz
olduğu için, bu POST isteği işlenirken aktif dil hep `tr`'ye zorlanıyordu.
Django'nun `set_language` view'ı içindeki `translate_url(next, lang_code)`,
`next` değerini (`/en/...` gibi) çözerken bu yanlış ('tr') aktif dil
bağlamını kullanıyor — `i18n_patterns`'in prefix regex'i dinamik olarak
aktif dile göre kurulduğu için (`LocalePrefixPattern.language_prefix`),
`/en/...` yolu 'tr' bağlamında hiçbir pattern'e uymuyor (`Resolver404`),
`translate_url` `next`'i DEĞİŞTİRMEDEN döndürüyor.

**Düzeltme:** `analizdestek/urls.py` → `i18n/` path'i `i18n_patterns(...)`
bloğunun İÇİNE taşındı. Artık `{% url 'set_language' %}` her sayfada kendi
dil prefix'ini taşıyor (`/en/i18n/setlang/`, `/de/i18n/setlang/`), bu
isteğin aktif dili artık her zaman doğru (`en`/`de`) oluyor, `translate_url`
`next`'i doğru çözüyor.

**Doğrulama:** 3 kaynak sayfa (`/`, `/en/`, `/de/`) × 3 hedef dil = 9
kombinasyonun hepsi gerçek POST ile test edildi, hepsi doğru `Location`
başlığı döndürdü. `/en/analiz/ttesti/` → `de` seçimi de ayrıca doğrulandı
(`/de/analiz/ttesti/`).

## Bulunup Düzeltilen 2. Kritik Bug + Admin Flag (22 Eylül 2026)

**Belirti:** "dil seçiminden sonra sayfa değiştiğinde otomatik olarak tr'ye
geçiliyor" — `/en/`/`/de/` sayfasındayken "Giriş" linkine tıklayınca dil
bağlamı kayboluyordu.

**Kök neden:** `login`/`logout` bilinçli olarak `i18n_patterns` dışında
(prefix'siz) tutulmuştu — `django.contrib.auth.urls`'ün kendi `login`/
`logout` adlarıyla çakıştığı için (`reverse()` belirsizliği). Prefix'siz
kalınca aynı "5a-devam"/"i18n/ path'i" bug'larıyla aynı kök sorun: bu
sayfaya giden isteğin KENDİSİ prefix'siz olduğu için `LocaleMiddleware`
aktif dili zorla `tr`'ye çekiyordu.

**Düzeltme:** `django.contrib.auth.urls` include'u KALDIRILDI (sadece
kullanılmayan `password_change`/`password_change_done` elle tanımlandı —
kod tabanında `password_change` hiç kullanılmıyor, grep ile doğrulandı),
`login`/`logout` artık `i18n_patterns` içinde. Artık isim çakışması yok,
`{% url 'login' %}` her sayfada kendi dil prefix'ini koruyor
(`/en/login/`, `/de/login/`).

**Ek — Admin'den açılır/kapanır flag (kullanıcı isteği):**
- `SiteSettings.feature_multilingual` (BooleanField, `default=False` —
  diğer "hazır ama henüz yayında değil" flag'leriyle tutarlı:
  `feature_agentic_landing`/`feature_training` gibi)
- `forum/context_processors.py` → `feature_flags()`'e eklendi
- `forum/admin.py` → `SiteSettingsAdmin.fieldsets`'e eklendi (KRİTİK adım —
  unutulursa flag DB'de var ama admin'den hiç değiştirilemez, bkz.
  analizus.md §26 "Yeni SiteSettings feature flag" dersi)
- `forum/middleware.py` → yeni `MultilingualFeatureMiddleware`: flag
  kapalıyken `/en/`, `/de/` prefix'li TÜM istekleri 404 ile keser
  (`settings.MIDDLEWARE`'de `ForceDefaultLanguageMiddleware`'den sonra,
  `LocaleMiddleware`'den önce)
- `templates/base.html` → navbar'daki dil seçici (desktop + mobil)
  `{% if features.multilingual and is_multilingual_page %}` ile sarıldı

**Ek — kapsam dışı sayfalarda dil seçici gizleme (kullanıcı kararı: "Gizle"):**
- `forum/context_processors.py` → yeni `multilingual_page_context()`:
  Django'nun `set_language` view'ının kullandığı AYNI `translate_url()`
  mekanizmasıyla, `'en'` ve `'de'` hedeflerine çeviri farklı URL üretiyorsa
  sayfa kapsamda demektir (`is_multilingual_page=True`); kapsam dışı
  sayfalarda (tarama, forum, yoktez, trdizin, oaipmh) ikisi de değişmeden
  aynı path'e eşit döner → seçici hiç gösterilmez. Öncesinde seçici orada
  da görünüyordu ama tıklayınca "görünürde hiçbir şey değişmiyordu" (çerez
  set ediliyordu ama gidecek prefix'li adres yoktu) — kafa karıştırıcıydı.

**Doğrulama:** `manage.py check` temiz; migration uygulandı; flag kapalıyken
`/en/`→404 + navbar'da seçici yok, flag açıkken `/en/`→200 + seçici var;
`reverse('login')`/`reverse('logout')` tr/en/de için doğru prefix'li;
`/en/login/` 200 + `<html lang="en">` + sayfadaki tüm linkler `/en/`
prefix'ini koruyor; kapsam içi sayfalarda (`/`, `/analiz/ttesti/`) seçici
görünüyor, kapsam dışında (`/tarama/`, `/forum/`) gizli.

## Bulunup Düzeltilen 3. Bug + Karar Değişikliği (22 Eylül 2026)

**Belirti 1 (Render):** Navbar'da "EN" rozetinin yanında boş/kırık bir
kutu görünüyordu (giriş yapmış kullanıcıda).
**Kök neden:** `Gelen kutusu` (`inbox`) linkine `{% trans %}` eklerken
`<a ...>` etiketinin kapanış `>` işareti yanlışlıkla silinmişti — `<svg>`
bir sonraki satırda geldiği için tarayıcı etiketi bozuk parse ediyor,
ikon hiç render olmuyordu. `templates/base.html` düzeltildi, aynı hata
için diğer tüm `aria-label="{% trans ... %}"` satırları taranıp
doğrulandı (başka bozuk yer yok).

**Belirti 2 (Render):** Sayfa değiştikçe dil seçici görünüp kayboluyordu.
**Karar değişikliği:** Kapsam dışı sayfalarda (tarama, forum, yoktez...)
dil seçiciyi gizleme kararı ("Gizle") kullanıcıyı şaşırttı — geri alındı.
Artık **her sayfada her zaman görünür** (kapsam dışı sayfada tıklarsa
çerez set edilir ama görünür bir değişiklik olmaz — kabul edilebilir).
`multilingual_page_context()` context processor'ü ve `is_multilingual_page`
kontrolü kaldırıldı (kullanılmıyordu, sadelik için silindi).

**Ortam notu:** Yerel makinede İKİ ayrı sunucu çalışıyor — Docker
(nginx/443, postgres) ve bağımsız `manage.py runserver` (port 8000,
`db.sqlite3`, .env'de `DATABASE_URL` kapalı olduğu için fallback).
İkisi FARKLI veritabanı kullanıyor — birinde yapılan flag/veri değişikliği
diğerinde görünmez. Test ederken hangi sunucuda olduğunuza dikkat edin.

## Adım 4 — İlk Çeviri Turu Tamamlandı (23 Eylül 2026, kullanıcı isteğiyle öne alındı)

**Neden öne alındı:** 3b-2 grubu (proje talebi/eğitim/AI çözümler) bitince
kullanıcı "hâlâ çeviriler sayfalarında gözükmüyor" dedi — haklı olarak,
o ana kadarki iş sadece `{% trans %}` işaretlemesiydi, gerçek çeviri
metni yoktu. Sırayı değiştirip o ana kadar işaretlenen HER ŞEYİN gerçek
İngilizce+Almanca çevirisini yazdım.

**Yapılanlar:**
- `gettext` container'a geçici kuruldu (kalıcı `requirements.txt`
  bağımlılığı DEĞİL, tek seferlik)
- `makemessages -l en -l de` → 601 msgid çıkarıldı
- `polib` ile Python script (`translate_po.py`, scratchpad'te) yazılıp
  601 metnin TAMAMI için EN+DE çevirisi elle yazıldı (plural + python-format
  placeholder'lar korunarak: `%(daily_limit)s`, `%(job_id)s`,
  `%(tool_title)s`/`%(promo_title)s` vb.)
- `compilemessages` ile derlendi

**Bulunup düzeltilen 2 ek sorun:**
1. **Fuzzy işaretler:** `makemessages` benzer eski msgid'lere göre bazı
   yeni string'leri otomatik "fuzzy" işaretliyor (ör. "Ücretsiz" →
   "Ücretsiz Dene" benzerliği) — `compilemessages` fuzzy girişleri
   VARSAYILAN OLARAK derlemeye dahil etmiyor, msgstr dolu olsa bile
   sessizce atlanıyor. `msgattrib --clear-fuzzy` ile temizlendi (6 kayıt
   etkilenmişti). **Bu adımı gelecekte her `makemessages` sonrası
   unutma.**
2. **`service_promo.html` keşfi:** Anonim kullanıcılar (yeni ziyaretçilerin
   çoğu) istatistik/openalex/semanticscholar araçlarında asıl çevirdiğim
   şablonu değil, `service_promo.html` adında paylaşılan bir "kayıt ol"
   davet şablonunu görüyor (`if not request.user.is_authenticated`).
   Bu dosya orijinal 26 dosyalık listede yoktu — küçük (211 satır) ve
   doğrudan kapsamdaki araçların giriş kapısı olduğu için ek onay
   almadan işaretlendi ve çevrildi.

**Doğrulama:** Giriş yapmış VE anonim oturumla `/en/`, `/de/` üzerinde
home, footer, navbar, openalex, semanticscholar, analiz/anova,
proje-talebi, login/register sayfaları curl ile test edildi — gerçek
İngilizce/Almanca metin görünüyor (`manage.py check` temiz).

**Kasıtlı hâlâ çevrilmemiş (adım 6 kapsamı, Python tarafı):**
`training_catalog.py` kurs verileri, `TOOL_CATEGORIES` sidebar etiketleri,
`seo_guide`/SEO_GUIDES sözlüğü (intro/faq/apa_example vb.), quiz soru
bankası, `analyses_list` (makaleanaliz), tablo satırları (`{{ label }}` /
`{{ m.title }}` gibi DB/servis çıktısı alanlar).

## Açık Sorular (kullanıcıya soruldu, netleşince ilerlenir)
- Proje talebi / Danışmanlık / Eğitim sayfaları kapsama girecek mi?
- İstatistik araçlarının analiz sonuç metinleri (PDF rapor içerikleri) de
  çevrilecek mi, yoksa sadece giriş/açıklama sayfaları mı?

---

# [ÖNCELİKLİ] Local Docker Ortamı — nginx crash-loop + yanlış DB fallback

**Durum:** TAMAMLANDI (23 Temmuz 2026) — nginx crash-loop çözüldü, DB fallback
çözüldü. Aşağıdaki "Önerilen düzeltme" bölümü artık geçmiş kayıt.

## Bulgular

**1. nginx sürekli restart oluyor (`docker compose ps` → `Restarting (1)`)**
Log (`docker compose logs nginx`): her ~60 saniyede bir
`cannot load certificate "/etc/letsencrypt/live/analizus.com/fullchain.pem"`
hatasıyla çöküyor. Kök neden: `docker-compose.yml:41` production nginx config'ini
(`./nginx/conf.d` — Let's Encrypt sertifika yolu bekliyor) mount ediyor, ama bu
sertifika yerel makinede yok (yalnızca Hetzner'de var).

Zaten 13 Temmuz'da (10 gün önce) bunun için bir local override hazırlanmış ama
hiç bağlanmamış: `nginx/conf.d.local/local.conf` (untracked dosya, git'e hiç
eklenmemiş) self-signed sertifika (`/etc/nginx/local-ssl/selfsigned.crt`)
kullanacak şekilde yazılmış — ama:
  - `docker-compose.yml` hâlâ `./nginx/conf.d`'yi mount ediyor, `conf.d.local`'ı değil
  - Self-signed sertifika dosyaları (`selfsigned.crt`/`.key`) henüz üretilmemiş,
    docker-compose.yml'de mount edilecek bir volume de tanımlı değil

**2. Web container Postgres yerine SQLite'a düşüyor**
`.env:9` içinde `DATABASE_URL` satırı yorumlu (`# DATABASE_URL=postgres://...`).
`analizdestek/settings.py:124-129`'daki `dj_database_url.config(default='sqlite:///...')`
bu yüzden sessizce `db.sqlite3`'e fallback yapıyor — halbuki `analizdestek-db-1`
(Postgres) container'ı zaten ayakta ve çalışıyor, web ona hiç bağlanmıyor.
Bu yüzden shell'den sorgulanan sayılar (ör. `FreelanceJob` tamamlanan iş sayısı)
yanlış/boş çıktı verdi — gerçek veri kaybı DEĞİL, yanlış DB'ye bağlanma sorunu.

## Önerilen düzeltme — TÜMÜ TAMAMLANDI (bkz. aşağıdaki "nginx düzeltmesi +
KRİTİK git-güvenlik düzeltmesi" ve "Madde 3 sonucu" bölümleri için uygulama
detayları). Bu blok artık geçmiş kayıt.

## nginx düzeltmesi + KRİTİK git-güvenlik düzeltmesi (23 Temmuz 2026, TAMAMLANDI)

Self-signed sertifika üretildi (`openssl req -x509 ...` → `nginx/local-ssl/
selfsigned.crt`+`.key`, 825 gün geçerli, `.gitignore`'a eklendi — makineye
özel, commit edilmeyecek).

**⚠️ ÖNEMLİ BULGU — `docker-compose.yml` Hetzner ile PAYLAŞILAN tek dosya:**
`analizus.md` §3 doğruladı: Hetzner production da `git pull origin main` ile
aynı `docker-compose.yml`'i çekip `docker compose` ile çalıştırıyor (container
adları `app-web-1`/`app-db-1`/`app-nginx-1`, aynı `web`/`db`/`nginx` servis
isimleri). İlk denemede nginx volume mount'unu VE `web` servisine bir
`environment: DATABASE_URL: ...` override'ını doğrudan bu paylaşılan dosyaya
yazmıştım — bu, Hetzner'in `main`'e merge sonrası `git pull` yapmasıyla
**production nginx'ini (Let's Encrypt yerine self-signed/local config) ve
olası DB bağlantısını kırma riski** taşıyordu (Docker Compose'da `environment:`
her zaman `env_file`'dan önceliklidir — Hetzner'in gerçek `.env`'indeki
`DATABASE_URL`'i sessizce ezebilirdi).

**Düzeltme:** `docker-compose.yml` **main ile birebir aynı** hale geri
döndürüldü (`diff <(git show main:docker-compose.yml) docker-compose.yml` →
fark yok, doğrulandı). Tüm local-only override'lar (`web.environment.
DATABASE_URL`, `nginx.volumes` → `conf.d.local`+`local-ssl`) yeni bir
**`docker-compose.override.yml`** dosyasına taşındı — Docker Compose bunu
`docker compose up`'ta otomatik yükler (ekstra `-f` bayrağı gerekmez) ama
dosya `.gitignore`'a eklendiği için **hiçbir zaman commit'lenmez, Hetzner'e
asla ulaşmaz**. Doğrulama: `docker compose config` ile birleşmiş ayarlar
kontrol edildi (DATABASE_URL doğru, nginx conf.d.local+local-ssl doğru),
`docker compose up -d` sonrası hem Postgres bağlantısı (`ENGINE: postgresql`)
hem nginx (`https://localhost/` → 200, restart döngüsü yok) çalışır durumda.

**Ders (gelecek oturumlar için kritik):** `docker-compose.yml` Hetzner
production'da da kullanılan paylaşılan bir dosya — local-only ayarlar asla
doğrudan bu dosyaya yazılmamalı, her zaman gitignore'lu bir
`docker-compose.override.yml`'e (veya benzeri) izole edilmeli. `nginx/conf.d.
local/local.conf` (sertifika/secret içermiyor) git'e eklenip commit'lendi —
gelecekte tekrar kurulum gerekmesin diye.

**Sonuç:** `docker compose ps` → 4 container da stabil (`db` healthy, `redis`/
`web`/`nginx` Up, hiçbiri restart döngüsünde değil).

## Madde 3 sonucu — TAMAMLANDI (23 Temmuz 2026)
"Tamamlanan pazar talebi istatistikleri" (FreelanceJob completed count)
sorunu çözüldü, 3 katmanlı kök neden bulundu ve düzeltildi:

1. `.env`'de `DATABASE_URL=postgres://bunyamin:analizus@db:5432/analizus`
   eklendi (satır yorumdan çıkarıldı) — web artık SQLite'a değil Postgres'e
   bağlanıyor.
2. **Yeni bulgu:** Bağlantı denenince şifre hatası çıktı — `app_postgres_data`
   volume'ü daha önce farklı bir şifreyle init edilmiş olduğundan `bunyamin`
   rolünün gerçek şifresi `.env`'deki değerle uyuşmuyordu. Yerel unix socket
   üzerinden (`docker exec -u postgres analizdestek-db-1 psql -U bunyamin -d
   analizus`) bağlanılıp `ALTER ROLE bunyamin WITH PASSWORD 'analizus';` ile
   düzeltildi.
3. **Yeni bulgu:** Şifre düzelince DB'nin 107 migration geride olduğu ortaya
   çıktı (forum uygulaması `0068`'de kalmıştı — `seed_initial_users`,
   `freelancejob` alan eklemeleri gibi kritik migration'lar uygulanmamıştı).
   Local/dev DB olduğu için (production etkilenmiyor)
   `docker compose exec web python manage.py migrate` çalıştırıldı, hepsi
   başarıyla uygulandı (`showmigrations` artık 0 bekleyen gösteriyor).

**Yan etki — istenmeyen e-posta patlaması (23 Temmuz 2026, aynı gün çözüldü):**
`docker compose restart web` iki kez çalıştırıldı (madde 1 ve madde 3 sonrası
doğrulama için). `Dockerfile` CMD'si her başlangıçta `deploy.sh`'i çalıştırıyor;
`deploy.sh` "DB boşsa seed yükle" idempotency kontrolü (`Topic.objects.count()`)
kullanıyor. İkinci restart'ta Postgres'e ilk kez gerçekten bağlanıldığı ve forum
tabloları taze/boş olduğu için bu kontrol "boş" algıladı, `load_seed_content`
gerçek `User.objects.create_user()` ile ~78 sahte kullanıcı oluşturdu →
`forum/signals.py:578` `post_save` sinyali → `notify_admin_new_user` →
**gerçek SMTP** (`.env`'deki `mail.analizus.com`) üzerinden admin'in gerçek
Gmail'ine (`ADMIN_NOTIFICATION_EMAIL`) ~78 ayrı e-posta gitti (her biri ayrı
async thread, birkaç dakikaya yayılarak ulaştı). Kaynak süreç kendi kendine
bitti, kalıcı bir hata değildi — bir daha aynı restart'ta tekrar tetiklenmez
çünkü DB artık boş değil (idempotency guard tutar).

**Kök neden düzeltmesi — host/Docker DB ayrışması (23 Temmuz 2026, TAMAMLANDI):**
Yukarıdaki 1. maddede `.env`'e yazılan `DATABASE_URL=postgres://...@db:...`
host'ta (`.venv`/conda ile) normal `python manage.py runserver` çalıştıran
günlük local iş akışını kırdı — `db` hostname'i yalnızca docker-compose
network'ünde çözülüyor (`could not translate host name "db"`).
`analizus.md` §24 ("DATABASE_URL boş bırak, SQLite kullanılır" — host için
dokümante edilmiş varsayılan) ile §26 ("host Docker servis adı olmalı" — bu
kural Docker/prod bağlamı için) referans alınarak iki ortam ayrıştırıldı:
- `.env`'deki `DATABASE_URL` tekrar yorum satırına döndürüldü (host →
  SQLite, eski/dokümante davranış).
- `docker-compose.yml`'de `web` servisine `environment: DATABASE_URL:
  postgres://${POSTGRES_USER:-bunyamin}:${POSTGRES_PASSWORD:-analizus}@db:
  5432/${POSTGRES_DB:-analizus}` override'ı eklendi (yalnızca container için
  Postgres, `env_file`'daki boş değeri ezer).
Doğrulandı: `docker compose up -d web` sonrası container hâlâ Postgres'e
bağlı (`ENGINE: postgresql`, `NAME: analizus`); bu recreate'te `deploy.sh`
seed adımı tekrar denedi ama kaynak `.md` dosyaları bulunamadığından
(`AnalizDestek_Forum_Seed_Content.md` yok) hiç yeni kullanıcı oluşturmadı,
kullanıcı sayısı 97'de sabit kaldı — **yeni e-posta gitmedi**.

**/market/ istatistik bandının local'de görünmemesi — bug DEĞİL, kasıtlı
sıfır kuralı (23 Temmuz 2026, doğrulandı):** Kullanıcı local'de `/market/`
sayfasındaki "Tamamlanan İş / Aktif Uzman / Son 90 Gün" üçlü sayaç bandının
hiç görünmediğini bildirdi. İnceleme: `forum/views.py:450-456`'daki
`market_stats` (`total_completed`, `recent_completed`, `total_experts`) ve
`forum/templates/forum/market/job_list.html:65` `{% if market_stats.
total_completed or market_stats.total_experts or market_stats.
recent_completed %}` — template yorumu bunu zaten "sıfır kuralı: üçü de 0
ise şerit gizli" diye adlandırıyor. Local Postgres DB'de `FreelanceJob` ve
`JobProposal` tabloları tamamen boş (0 kayıt, yukarıdaki DB fallback
sorunundan bağımsız — local ortamda hiç gerçek pazar verisi girilmemiş)
olduğu için üçü de 0 çıkıyor, şerit kasıtlı olarak gizleniyor. Kod tarafında
hata/cache bayatlığı/isim uyuşmazlığı yok. Ana sayfadaki `showcase_jobs`
(views.py:284-299) de aynı sebeple boş. **İş gerekmiyor** — local'de gerçek
iş ilanı/teklif verisi oluşturulursa bant otomatik görünür.

**Sonuç:** `FreelanceJob.objects.count()` artık hatasız çalışıyor, sonuç **0**.
Repo kökündeki `yedek_2026-07-13.sql` yedeği de kontrol edildi — orada da
yalnızca 1 kullanıcı (admin) ve 0 iş var. Yani local ortamda hiçbir zaman
gerçek pazar verisi olmamış; "0 tamamlanan iş" artık **doğru** sonuç,
önceki yanlış/boş çıktı tamamen yanlış DB bağlantısından kaynaklanıyordu.

## Sıradaki adım
Yok — sertifika üretimi de (bkz. yukarı "nginx düzeltmesi" bölümü, 23 Temmuz
2026) dahil tüm maddeler tamamlandı, doğrulandı: 31 Temmuz 2026 itibarıyla
`docker compose ps` 4 container da stabil, nginx restart döngüsünde değil.

---

# Bootstrap Kaldırma — Kademeli Migration Planı

**Durum:** Envanter çıkarıldı, uygulama henüz başlamadı. (Temmuz 2026)

## Neden gerekli
CLAUDE.md kuralı "Bootstrap yalnızca grid için" diyor ama gerçek kod bunu ihlal
ediyor — Lighthouse'un "kullanılmayan CSS 111 KiB / kullanılmayan JS 164 KiB"
bulgusunun kaynağı bu. Ayrıca Google Fonts/Bootstrap CDN cache-control süresi
bizim kontrolümüzde değil (Lighthouse "verimli önbellek" bulgusu, 177 KiB).

## Envanter (temmuz 2026 taraması)
- **102 template dosyası** Bootstrap component class kullanıyor (`btn`, `card`,
  `badge`, `alert`, `modal`, `dropdown`, `form-control`, `form-select`)
- **13 dosya** `data-bs-toggle`/`data-bs-target`/`data-bs-dismiss` kullanıyor
  (Bootstrap JS bundle'a bağımlı — modal/dropdown açma-kapama)
- **96 dosya** grid class'ı (`container`/`row`/`col-*`) kullanıyor
- **3 dosya** JS'te doğrudan `new bootstrap.Modal(...)` / `bootstrap.Dropdown`
  API'sini çağırıyor: `forum/templates/forum/success_stories.html`,
  `static/js/notifications.js`, `templates/base.html`
- En ağır kullanan dosyalar: `hangi_test.html` (144), `base.html` (127),
  `studyroom_detail.html` (117), `tezanaliz/landing.html` (97),
  `istatistik/korelasyon.html` (93), `market/job_detail.html` (93)

## Mevcut ax- sistem durumu (static/css/)
Var olan: `.ax-btn` (base.css), `.ax-card` (cards.css), `.ax-badge` (8 tanım,
cards.css/profiles.css/home_sections.css'e dağılmış)

Eksik — inşa edilmesi gereken: `.ax-alert`, `.ax-modal`, `.ax-dropdown`,
`.ax-form-control`/`.ax-form-select`/`.ax-form-check`, `.ax-tooltip`,
`.ax-toast`, `.ax-collapse`/`.ax-tab`

## Fazlar

### Faz 1 — Eksik ax- CSS bileşenlerini inşa et (sıfır görsel etki) — TAMAMLANDI
`static/css/base.css`'e 4 yeni bölüm eklendi (7. Alert, 8. Modal, 9. Dropdown,
10. Form Controls — dosya sonu Responsive Utilities artık 11), mevcut
numaralandırma/token/isimlendirme deseni takip edildi. Hiçbir template
değiştirilmedi.
- `.ax-alert` (+ success/danger/warning/info varyantları)
- `.ax-modal` (backdrop + dialog + header/body/footer, `.is-open` toggle)
- `.ax-dropdown` (site-nav'daki `.site-nav__dropdown*` ile aynı görsel dil,
  genel kullanım için ayrı isimlendirildi — `.ax-dropdown-wrap`/`.ax-dropdown`)
- `.ax-form-control` / `.ax-form-select` / `.ax-form-check` (+ `.ax-form-group`,
  `.ax-form-label`, `.ax-form-hint`)

**Not — "sıfır görsel etki" tam sağlanamadı, bilinçli olarak kabul edildi:**
Uygulamadan önce tarama yapıldı, 2 sayfa zaten bu class isimlerini
kullanıyor ama hiçbir CSS tanımı yoktu (çıplak/stilsiz kullanım):
- `yoktez/templates/yoktez/results.html` (54, 192. satır) —
  `ax-alert ax-alert--danger` artık gerçekten stillenecek
- `istatistik/templates/istatistik/anova.html` (61, 66. satır) —
  `ax-form-control` artık gerçekten stillenecek

Kullanıcı onayıyla bug-fix niteliğinde kabul edildi. **TODO: bu 2 sayfa
tarayıcıda görsel doğrulanmalı** (deploy sonrası).

Çakışma olmayan (kontrol edildi, dokunulmadı): `ttesti.html`/`hangi_test.html`
kendi `.ax-form-control` tanımına sahip (body içindeki `<style>` bloğu,
cascade'de kazanıyor); `normallik.html` vb. istatistik sayfaları tek tireli
`ax-alert-danger`/`ax-alert-info` kullanıyor (farklı isim, çakışmıyor);
`hangi_test.html`'in `.ax-modal-overlay/-dialog` yapısı tamamen ayrı
isimlendirme.

### Faz 2 — Vanilla JS modal/dropdown controller — TAMAMLANDI (modal+dropdown)
**Kapsam kullanıcı onayıyla daraltıldı:** `notifications.js`'teki
`bootstrap.Toast` kapsam dışı bırakıldı — gerçekte Modal/Dropdown değil Toast
kullanıyordu, `.ax-toast` CSS'i Faz 1'de yok, ayrı görev olarak aşağıda not
edildi.

**Yapılanlar:**
- `static/js/ax-modal.js` (yeni) — `data-ax-toggle="modal"` / `data-ax-target`
  / `data-ax-dismiss="modal"` deseni + backdrop tıklama + Escape ile kapatma +
  `.ax-no-scroll` scroll kilidi + `window.AxModal.open/close` programatik API.
- `static/js/ax-dropdown.js` (yeni) — `.ax-dropdown-wrap`/`[data-ax-dropdown]`
  için genel controller, `navbar.js`'e dokunmadan ayrı çalışır. **Henüz hiçbir
  template kullanmıyor** — Faz 3 migration'larında kullanılacak, şimdilik no-op.
- `templates/base.html` — 4 modal (`searchModal`, `quizModal`, `profileModal`,
  `storyModal`) markup'ı `.ax-modal-backdrop`/`.ax-modal`/`.ax-modal__*`'e
  taşındı; 3 `new bootstrap.Modal()` çağrısı `AxModal.open(el)` ile değiştirildi;
  arama tetikleyicisi `data-ax-toggle`'a geçti. Modal içeriği (quiz butonları,
  badge'ler, spinner-border) kasıtlı olarak Bootstrap class'larıyla bırakıldı
  — o Faz 3'ün kapsamı (component migration), Bootstrap CSS/JS Faz 4'e kadar
  zaten yüklü kalacak.
- `forum/templates/forum/success_stories.html` — `shareStoryModal` aynı şekilde
  taşındı, `bootstrap.Modal(...).show()` → `AxModal.open(...)`.

**Bilinçli küçük görsel sapmalar (doğrulama listesine eklendi):**
- `profileModal`/`storyModal`'ın özel inline arka plan renkleri
  (`rgba(15,23,42,.95)`, gradient) kaldırıldı, `.ax-modal`'ın standart koyu
  arka planı kullanılıyor — görsel olarak çok yakın ama birebir aynı değil.
- `base.html`:511'deki mesaj `alert`/`data-bs-dismiss="alert"` kasıtlı
  dokunulmadı — bu Bootstrap'ın Alert bileşeni (Modal/Dropdown değil),
  kapsam dışı.

**Görsel doğrulama — TAMAMLANDI.** İlk testte modallar gizlenmedi, sayfa
akışının içinde çıplak görünüyorlardı — sebep `base.css`'in cache-busting
versiyonunun (`?v=0100`) Faz 1/2 içerik değişikliklerine rağmen artırılmamış
olmasıydı (bkz. `tasks/lessons.md`). `templates/base.html`'de `?v=0101`'e
yükseltilip tarayıcı yenilendikten sonra kullanıcı doğruladı: sorun düzeldi.

### Faz 3 — Template migration (dosya dosya, düşük riskliden başla) — BAŞLADI
Öncelik sırası: az Bootstrap class'ı olan → çok olan. Her dosya değişikliği
ayrı görev olarak onaya sunulmalı (CLAUDE.md kırmızı çizgi). Her dosyadan
sonra tarayıcıda görsel doğrulama yapılmalı.
- Grid-only sayfalar önce (sadece container/row/col — risk düşük)
- Sonra btn/card/badge kullanan sayfalar (ax- karşılığı zaten var)
- En son modal/dropdown/form kullanan ağır sayfalar (job_detail.html,
  hangi_test.html, studyroom_detail.html, istatistik araçları)

**ÖNEMLİ BULGU (kullanıcı onayıyla kapsam dışı bırakıldı, ayrıca not):**
`profile_private.html` incelenirken görüldü — "grid-only" kategorisinde
gerçek proje dosyası yok (tek eşleşme `aws/dist/awscli/...` idi, 3. parti
kütüphane, proje template'i değil). Ayrıca component class'ı (btn/card/badge)
migrate edilmiş dosyalarda bile Bootstrap **utility** class'ları (`d-flex`,
`text-white`/`text-muted`, `fw-bold`, `mb-*`/`py-*`/`px-*`, `gap-*`,
`rounded-*`, `shadow-*`, `bg-*`, `border-*`) hâlâ yaygın — bunlar CLAUDE.md'nin
"Bootstrap yalnızca grid için" kuralına göre onaylı değil ve **Faz 4'te
CDN kaldırılınca bunlar da kırılır**, sadece modal/dropdown/form değil.
Karar: Faz 3 şimdilik dar tutuldu (sadece component class migration).
Utility class migration'ı **Faz 4'ten önce ayrı bir alt görev olarak**
ele alınmalı — envanteri henüz çıkarılmadı.

**AYRI BULGU — float buton z-index/konum çakışması (Bootstrap kaldırma
kapsamı dışı):** Kullanıcı bildirdi — sayfa dar ekranda (yarım pencere)
görüntülenince sağ alttaki float butonlar (Destekçi/donate, "AI Asistan",
WhatsApp "Proje hakkında konuşalım") üst üste biniyor, biri diğerini
kapatıyor. Mobil öncelikli ([[feedback_mobile_first]] memory) gözden
geçirilmeli — muhtemelen aynı `position: fixed; bottom/right` offset'i
paylaşıyorlar, responsive stacking/offset eksik. Henüz araştırılmadı,
kök neden dosyası bulunmadı. Ayrı bir görev olarak ele alınacak.

**İlk migrate edilen component-density sıralaması (en düşükten):**
`story_modal_content.html` (1, ama 2 farklı kopyası var — `templates/` ve
`templates/forum/partials/`, senkron değiller), `account_delete.html` (2),
`donation_success.html` (3), `job_list.html` (3), `profile_detail.html` (3).

**Dosya bazlı ilerleme:**
- [x] `forum/templates/forum/account_delete.html` — tek değişiklik:
  `btn btn-danger` → `ax-btn ax-btn--danger` (40. satır). Yeni CSS gerekmedi,
  `.ax-btn--danger` zaten vardı. **Görsel doğrulama TAMAMLANDI** —
  `/account/delete/` sayfasında kullanıcı ekran görüntüsüyle onayladı.
- [x] `forum/templates/forum/donation_success.html` — 3 değişiklik:
  `card`→`ax-card` (9. satır), `card-body` kaldırıldı (10. satır, `p-5`
  zaten padding sağlıyordu), `btn`→`ax-btn` (60. satır, inline gradient
  stili korundu). Utility class'lara dokunulmadı. **Görsel doğrulama
  TAMAMLANDI** — `/donation/success/` sayfasında kullanıcı ekran
  görüntüsüyle onayladı, kart/padding/buton hiç bozulmamış.
- [ ] Sıradaki aday: `job_list.html` (3 component)

**Not (temmuz 2026) — yeni sayfalar envanteri büyütmedi:** Bu oturumda
oluşturulan `forum/templates/forum/contact.html` (İletişim landing page) ve
`forum/templates/forum/gizlilik_politikasi.html` (KVKK sayfası) sıfırdan
`ax-*` sistemiyle yazıldı — migrasyon kapsamına eklenecek yeni Bootstrap
component borcu yok. Tek istisna: KVKK sayfasındaki tablo ilk halde
`table table-dark table-borderless` ile yazılmıştı, aynı oturumda fark edilip
(`table-dark`'ın `--bs-table-bg`/`--bs-table-color` değişkenleri inline
satır renkleriyle çakışıp okunaksız görünüyordu) `.ax-kvkk-table`'a
taşındı — yani net etki: envantere yeni satır eklenmedi.

**Not (temmuz 2026) — cache-busting dersi tekrar uygulandı:** Navbar logosuna
eklenen "Analizus" yazısının puntosu `navbar.css`'te iki kez büyütüldü, ama
`templates/base.html:93`'teki `?v=0103` versiyon string'i ilk seferinde
artırılmayı unutuldu — kullanıcı production'da değişikliği göremeyince fark
edildi, `?v=0104`'e çekilip düzeltildi. Bu, §26'daki "CSS değişikliği
production'da görünmüyor" hatasının canlı bir tekrarı; her `static/css/*.css`
değişikliğinde ilgili `<link>` versiyon string'inin de artırılması gerektiği
bir kez daha teyit edildi.

### Faz 4 — Bootstrap CDN'i kaldır
`base.html`'den `bootstrap.min.css` + `bootstrap.bundle.min.js` linklerini
sil. Tüm sayfalarda regresyon taraması (özellikle modal/dropdown/form
davranışları).

### Faz 5 — Temizlik
Kullanılmayan geçiş dönemi shim'leri varsa kaldır.

## Riskler
- Modal/dropdown JS davranışı görsel olarak sessiz kırılabilir (constructor
  hatası fırlatmaz, sadece tıklama işe yaramaz) — her migration adımından
  sonra manuel tıklama testi şart
- Form control stilleri (`form-control`, `form-select`) hem stat hem
  survey/analiz formlarında yoğun kullanılıyor — ax- karşılığı görsel olarak
  input/select native davranışını (autofill, focus ring, disabled state)
  bozmamalı
- 100+ dosyalık migration tek PR'da değil, birden fazla oturuma yayılmalı

## Sıradaki adım
Faz 1'i başlatmak için onay bekleniyor — hiçbir mevcut template değişmeyeceği
için düşük riskli, istenildiğinde başlanabilir.

**Deploy notu:** Bu migration'ın tüm adımları yalnızca `dev` branch'ine push
edilecek. `main`'e (Hetzner/prod) kullanıcı açıkça "merge et" demeden
geçilmeyecek — bkz. genel proje kuralı (memory: `git_workflow`, `dev_first`).

---

# Homepage'e 3. Hero Seçeneği: "Bir Projem Var" (fikir aşaması)

**Durum:** Sadece fikir — henüz uygulanmadı, kullanıcı "todo'ya yaz ve bırak"
dedi. (Temmuz 2026)

## Fikir
Homepage'deki iki taraflı pazar yeri yönlendirmesine ("Analiz Yaptırmak
İstiyorum" / "Uzman Olarak Katılmak İstiyorum") üçüncü bir seçenek eklemek:
"Bir Projem Var..." → mevcut `/proje-talebi/` sayfasına (kurumsal danışmanlık
talep formu) yönlendiren bir kart/şerit.

## Teknik bulgular
- İki mevcut kart `forum/templates/forum/home.html:257-341` içinde, `row g-4`
  içinde iki `col-lg-6` — her biri özel SVG illüstrasyon, özellik listesi,
  kategori etiketleri, çoklu CTA içeriyor (zengin/karmaşık içerik).
- Kart shell'i `static/css/home_sections.css:71` — `.ax-market-card` (ortak
  gövde) + `.ax-market-card--demand`/`--supply` (üst renkli çizgi varyantları,
  indigo/amber). Üçüncü `.ax-market-card--project` varyantı (`--ax-accent-secondary`
  yeşili ile) düşük riskli, küçük bir CSS eklemesi olur.
- `/proje-talebi/` zaten var (`forum/views.py: proje_talebi`, "Projenizi
  Anlatın, Size Uygun Uzmanı Bulalım" başlığı) — kurumsal/şirket odaklı.
  **Dikkat:** "Analiz Yaptırmak İstiyorum" kartıyla hedef kitle örtüşmesi
  olabilir (ikisi de "biri benim için analiz yapsın" diyor) — uygulamaya
  geçilirken bu ayrım netleştirilmeli (örn. proje_talebi = kurumsal/resmi
  teklif süreci, mevcut kart = bireysel/hızlı eşleşme).

## Önerilen yaklaşım (kullanıcıya sunuldu, karar bekliyor)
İki mevcut kart hiç değişmeden kalsın (zaten dönüşüm sağlıyorlar, riske
atılmamalı). Altına tam genişlikte, sade/yatay bir üçüncü şerit eklensin —
büyük SVG yok, kısa açıklama + tek CTA (`/proje-talebi/`), yeşil
(`--ax-accent-secondary`) vurgusuyla diğer ikisinden ayrışır. **Reddedilen
alternatif:** 3 eşit kolon (`col-lg-4`) — mevcut zengin kartların
küçültülmesini gerektirir, çalışan/dönüşüm sağlayan elemanlara dokunma
riski taşır.

## Sıradaki adım
Kullanıcı ne zaman uygulamaya geçmek isterse haber verecek; o zaman hedef
kitle ayrımı netleştirilip yukarıdaki yaklaşımla (veya kullanıcının o an
tercih edeceği alternatifle) uygulanacak.

---

# Claude API ile Akademik Tarama Entegrasyonu (fikir aşaması)

**Durum:** Sadece fikir/araştırma notu — henüz plan/onay yok. (Temmuz 2026)

## Kaynak
LinkedIn'de görülen "Claude Science" paylaşımı aslında Claude'un agentic
tool use ile yaptığı bir sistematik literatür taraması: PubMed E-utilities'den
veri çekme, LLM+kural tabanlı hibrit tarama, kod yürütme ile PRISMA diyagramı/
bibliyometrik grafik üretimi, Crossref'ten DOI doğrulama.

## Fikir
Bu yeteneği platformun mevcut "akademik tarama" ve "bibliyometri"
modüllerine (analizus.md §13-15) eklemek.

## Önerilen mimari (taslak)
- **Managed Agents değil, Claude API + tool use** — mevcut Django job/polling
  altyapısına (Celery, S3, `result_data` JSON kaydı) entegre olması ve tam
  backend kontrolü için
- Custom tool: `pubmed_search` (E-utilities çağrısı), `crossref_verify_doi`
- Server-side `code_execution` tool: PRISMA diyagramı + bibliyometrik
  grafikler (matplotlib, mevcut istatistik pipeline'ıyla aynı mantık)
- Hibrit tarama: önce ucuz kural tabanlı filtre, belirsiz kalanlar Claude'a
  (maliyet kontrolü)
- Sonuç: CSV + figür + referans listesi, mevcut polling/job desenine (§12)
  uyacak şekilde

## Tradeoff notu
Managed Agents kullanılırsa ajan döngüsü/konteyner Anthropic tarafında
barınır (daha az backend kodu) ama mevcut Celery/polling mimarisiyle
entegrasyonu daha zor ve ekstra maliyet/karmaşıklık getirir.

## Sıradaki adım
Hangi modüle ekleneceği netleşmedi (mevcut akademik tarama mı, yeni özellik
mi). Karar verilmeden somut plana (dosyalar, endpoint, migration gerekip
gerekmediği) geçilmeyecek.

---

# Site Geneli "Sıfır Kuralı" (Zero-State Sigortası)

**Durum:** TAMAMLANDI (12 Temmuz 2026, commit `b39307c`). Kaynak prompt
`~/Desktop/analizus_sifir_kurali_prompt.md`. Faz 1 envanteri çıkarıldı+onaylandı,
Faz 2 uygulandı (ana sayfa 5 sayaç + `has_any_stats` grup kontrolü, uzman kartı
"0 tamamlanan proje" satırı, "Akademik Haberler" placeholder kaldırıldı,
Gündemdeki Tartışmalar+Akademik Haberler layout bütünlüğü, /hakkimizda/ "Ekip ve
Güven" bölümü), Faz 3'te 9 smoke test eklendi (`forum/tests.py`). /market/ ve
/proje-talebi/ zaten kurala uygun çıktı (yeni iş gerekmedi). Aşağıdaki eski not
artık geçmiş kayıt olarak kalıyor:

## Amaç
Değeri 0 olan hiçbir güven metriği ("0 tamamlanan analiz", "0 aktif uzman" vb.)
ve içi boş hiçbir vitrin bölümü ziyaretçiye gösterilmeyecek. Gerekçe: dev DB
boşluğu değil, canlının doğal dalgalanması (gece 03:00 çevrimiçi uzman
gerçekten 0 olabilir) — "boş dükkân" izlenimini önlemek.

## Protokol (kullanıcının vurguladığı 3 kritik nokta)
1. **Kuralı tanımla, yerleri saydırma.** Talimat sabit bir liste değil: Faz 1
   `grep` ile TÜM template'leri tarayıp tam bir envanter tablosu çıkarır
   (Template · Bölüm · Metrik/Koleksiyon · Mevcut davranış · Önerilen işlem ·
   Kategori), onay alınmadan tek satır değiştirilmez. Bilinen 8-9 aday
   (ana sayfa `ax-stats-section`, uzman vitrini kart içi satırlar, "Akademik
   haberler yakında" şeridi, /proje-talebi/ stats bar, /market/ sayaç üçlüsü,
   /hakkimizda/ "Henüz uzman kadro eklenmedi.") başlangıç noktası, liste
   bunlarla SINIRLI değil — asıl risk modelin kapsamı kendiliğinden
   genişletmesi; envanter+onay kapısı bunu keser.
2. **İstisnayı ilkeyle tanımla, örnekle sabitle — "davet vs itiraf" ayrımı.**
   Davet (bilinçli tasarlanmış CTA içeren boş-durum metni, ör. market'teki
   "İlk analiz işini sen tamamla…") KORUNUR; itiraf ("Henüz uzman kadro
   eklenmedi." gibi) GİZLENİR. Gri kalan her örnek envanterde "karar gerekli"
   işaretlenip kullanıcıya sorulacak.
3. **Yan etkileri kurala bağla.** Bir öğe gizlenince grid/flex kırılmamalı
   (7 sayaçtan 3'ü gizlenince kalan 4'ün doğal dağılması); bir sayaç
   grubundaki TÜMÜ 0 ise kapsayıcı (şerit/başlık dahil) da gizlenir; yeni DB
   sorgusu YASAK — "hepsi sıfır mı" kontrolü mevcut cache'li değerlerden
   türetilen tek bir boolean ile yapılır; parantezli `{% if %}` yasağı
   (analizus.md §26) geçerli.

## Fazlar (kaynak promptta tanımlı)
- Faz 1 — Envanter (uygulama yok, sadece rapor + onay)
- Faz 2 — Uygulama (template `{% if %}`, gerekirse tek boolean context değişkeni)
- Faz 3 — Test + Teslim (0/>0 smoke testleri, migration beklenmiyor)

## Sıradaki adım
Kullanıcı başlamamı istediğinde `analizus_sifir_kurali_prompt.md` içeriğiyle
Faz 1'i (envanter) çalıştırıp tabloyu onaya sunacağım.

---

# Merge Öncesi Son Süpürme (analizus_son_supurme_prompt.md)

**Durum:** TAMAMLANDI — Madde 1-11'in tümü bitti (13 Temmuz 2026). `dev`→`main`
merge de yapıldı (31 Temmuz 2026 itibarıyla iki branch aynı commit'te,
`9b6f58d`). Merge sonrası hatırlatmalardan `feature_agentic_landing` flag'inin
prod'da elle açılıp açılmadığı DOĞRULANMADI — sıradaki oturumda kontrol
edilmeli (bkz. Madde 10 deploy notu).
Kaynak: `~/Desktop/analizus_son_supurme_prompt.md`. Yeni oturumda önce bu dosya
+ bu bölüm okunmalı; `analizus_son_supurme_prompt.md`'nin ORİJİNAL Madde 1
metni artık güncel değil (aşağıdaki kararlarla değişti), bu yüzden bu bölüm
esas alınmalı.

## Tamamlananlar (commit sırasıyla)

- **Madde 1 (huni parametreleri)** — `cd84461`. Tableau CTA metni "Proje Talebi
  Oluştur"a çevrildi; bibliometrik ön-seçim için `ANALYSIS_CHOICES`'a
  `('bibliometric', 'Bibliyometrik Analiz')` eklendi (migration `0147`, no-op
  AlterField). `proje_talebi` view artık `?type=` GET param'ını da okuyor.
  **Karar (kullanıcı onaylı):** bibliometri istatistiksel analiz sayılmadı,
  `statistics` seçeneği yeniden kullanılmadı — ayrı seçenek açıldı.
- **Madde 2 (Sıfır Kuralı)** — `b39307c`. Yukarıdaki bölüme taşındı.
- **Madde 3 (footer tutarsızlığı)** — iş YOK, zaten çözülmüştü (footer tek
  partial, `{% url 'analiz_home' %}` kullanıyor, hardcode `/istatistik/` yok).
- **Madde 4 (forum boş-durum sızıntısı)** — iş YOK, zaten çözülmüştü (`#noResults`
  zaten `d-none` ile başlıyor, JS mantığı zaten doğruydu).
- **Madde 5 (OG override + meta)** — `d73ab72`. 8 hedef sayfaya
  og_title/og_description/twitter_title/twitter_description eklendi.
  **Önemli bulgu:** `/bibliometrics/` misafir kullanıcı için `landing.html`
  değil, PAYLAŞILAN `templates/service_promo.html` render ediyor (6+ istatistik
  araç sayfası da aynı şablonu kullanıyor). Asıl düzeltme oraya, `promo_description`
  context değişkeninden yapıldı — bonus: diğer araç sayfaları da özgün
  og:description kazandı.
- **Madde 6 (dev noindex middleware)** — iş YOK, zaten vardı
  (`forum/middleware.py::NoIndexMiddleware` + `settings.IS_PRODUCTION`).
- **Madde 7a (bibliometri örnek çıktılar + OpenAlex köprüsü)** — `2029ce9`.
  Galeri ve OpenAlex ters köprüsü zaten
  vardı; eklenen tek şey hero altı "OpenAlex'te tarama mı yaptın?" bandı
  (`promo_openalex_bridge` context bayrağı, yalnızca bibliometride true).
  **Karar (kullanıcı onaylı):** galeri kartları spec'in istediği 5 başlıkla
  (Anahtar Kelime Eş-Oluşum Ağı, Anahtar Kelime Zaman Trendi vb.) DEĞİL,
  `static/img/`'de gerçekten var olan 6 görselin gerçek içeriğine uygun
  başlıklarla kuruldu (Yayın Trendi, Anahtar Kelime Bulutu, Yazar İşbirliği
  Ağı, Atıf Analizi & H-index, Araştırma Boşluğu Haritası, Lotka Kanunu) —
  bu zaten `bibliometrics/views.py`'de mevcuttu, değiştirilmedi.
- **Madde 7b (Tableau facade)** — `4ebaa7e`. Poster+buton facade UI önceki
  turda zaten kuruluydu, ama `tableau.embedding.3.latest.min.js` script'i
  `extra_js` block'unda koşulsuz (sayfa yüklenir yüklenmez) çekiliyordu —
  bu da "ilk yüklemede public.tableau.com'a sıfır istek" kabul kriterini
  fiilen bozuyordu. Script artık yalnızca "İnteraktif Dashboard'u Yükle"
  tıklamasında dinamik `<script>` enjeksiyonuyla yükleniyor. Playwright ile
  doğrulandı: yüklemede 0 istek, tıklamada gerçek dashboard (5 istek) açılıyor.
- **Madde 7c (Blog OG/kapak/pagination)** — `8b82242`. og:type=article ve
  pagination linkleri önceki turda zaten doğruydu. Eksik olan tek parça —
  kapaksız yazılarda kategoriye göre varsayılan görsel — `BlogPost.
  cover_image_url` property'siyle eklendi (35/35 yayındaki yazının hiçbirinde
  kapak yoktu, bu yüzden kartlar ve og:image/JSON-LD boş görünüyordu).
  Migration gerekmedi. Playwright ile liste+detay sayfası görsel doğrulandı.
- **Madde 8 (Hero sadeleştirme)** — `c338a7b`. `ax-hero__actions` bloğu
  ("Ücretsiz Başla"/"Analiz Yap" / "Uzman Bul" / "Foruma Katıl", giriş
  yapmış/yapmamış iki varyantıyla) tamamen kaldırıldı. Dropzone, "uzmana
  bırak" linki, veri kazıma bandı, alt CTA kartları değişmedi — Playwright
  ile masaüstü+mobil görsel doğrulandı, orphan spacing/CSS sorunu yok.
- **Madde 10 (Testler + Deploy Notu)** — bu tur. `forum/tests.py`'e 8 yeni smoke
  test eklendi: Madde 1'in 4 ön-seçimi (`?source=verification/agentic/tableau/
  bibliometrics` → `proje_talebi` formunda doğru `<option selected>`), Madde 4
  (forum arama sonucu boş-durumu varsayılan görünümde `d-none` ile gizli),
  Madde 6 (`NoIndexMiddleware` — `IS_PRODUCTION=False`'da header var,
  `True`'da yok, 2 test), Madde 7b (tableau `<tableau-viz>` yalnızca
  `<template>` içinde, ilk yüklemede canlı DOM'da yok). Madde 2 ve 9'un
  testleri zaten mevcuttu (bkz. yukarı Sıfır Kuralı bölümü ve
  `test_register_get_returns_200`/`test_login_get_returns_200`).
  **Sonuç:** 31 test, 30 geçti; tek hata `test_yoktez_job_daily_limit_normal_user`
  — bu turla ilgisiz, önceden bilinen, dokunulmadı (bkz. "Genel notlar").

  **DEPLOY NOTU (main'e merge öncesi — dev, main'den 28 commit ileride):**
  - **Migration:** main→dev arası tam 4 migration — `0144_projectrequest_
    source_choices`, `0145_sitesettings_feature_agentic_landing_and_more`,
    `0146_projectrequest_source_tableau_bibliometrics`,
    `0147_projectrequest_analysis_bibliometric`. Hepsi `AlterField` (choices
    genişletme) + tek `AddField` (boolean flag) — veri kaybı riski yok,
    `--fake` gerekmiyor.
  - **collectstatic:** GEREKLİ. Yeni statik dosyalar: 6 yeni CSS
    (`agentic_landing.css`, `bibliometrics.css`, `brand_visuals.css`,
    `expert_card.css`, `market.css`, `trend_topics.css`) + görseller
    (`agentic-hero(-mobile).webp`, `auth-login(-mobile)/auth-register
    (-mobile).webp`, `biblio-ornek-*.webp` ×6, `tableau-poster-*.webp` ×4).
  - **`?v=` denetimi:** main'de zaten var olup dev'de içeriği değişen yalnızca
    2 CSS dosyası var — ikisi de doğru bump edilmiş: `hero.css` 0103→0105,
    `home_sections.css` 0106→0112. Diğer 6 CSS dosyası main'de hiç yok
    (prod'da eski cache'lenmiş kopya yok), versiyon numaraları (v=0001/0002)
    bu yüzden önemsiz.
  - **Hetzner sırası:** `git pull` (main) → `docker compose exec web python
    manage.py migrate` → `docker compose exec web python manage.py
    collectstatic --noinput` → `docker compose restart web` → `docker compose
    restart nginx` (IP cache sorunu, CLAUDE.md kuralı).
  - **Merge sonrası hatırlatmalar:**
    1. **Feature flag açılmalı:** `feature_agentic_landing` migration'da
       `default=False` geliyor — admin'den `SiteSettings`'te AÇILMAZSA
       `/ai-cozumler/` ne navbar'da (`context_processors.py:75`) ne sitemap'te
       (`sitemaps.py:14`) görünür. Bu adım atlanırsa Madde 1b/7a'nın tüm
       huni işi görünmez kalır.
    2. `robots.txt` içeriği değişti (`Disallow: /istatistik/` satırı
       kaldırıldı, artık 301 üzerinden /analiz/'e akıyor) — GSC "robots.txt
       Test Aracı"ndan yeniden okutulmalı.
    3. Sitemap resubmit (GSC → Sitemaps).
    4. `/ai-cozumler/` + Madde 7'deki araç sayfaları (bibliometrics,
       tableau-analiz vb.) için GSC URL denetimi → elle dizine ekleme iste.
    5. `/istatistik/` → `/analiz/` 301'i GSC URL denetim aracıyla doğrula
       (robots.txt artık bunu engellemiyor, redirect aktif görünmeli).
    6. **Premium fiyat kaynağı kontrol edildi — DÜZELTME GEREKMEDİ.** Kaynak
       tamamen DB: `DonationTier.min_amount` (migration'ları 0031/0032/0045/
       0076, zaten prod'da uygulanmış, bu merge'e dahil değil).
       `footer.html:154-167` yalnızca `{{ tier.min_amount }}` render ediyor,
       hardcode TL değeri yok — prod (250/500/750/1000) ve dev (50/100/250/
       500) farkı tamamen DB seed farkı, template/kod fark yaratmıyor.

- **Madde 9 (Auth panelleri)** — `7837700`. `login.html`/`register.html`
  base.css yüklemiyor (tamamen izole, hardcode renkli sayfalar) — bu yüzden
  `var(--ax-bg)` yerine dosyanın kendi `#0a1628` rengiyle iç vinyet
  (`box-shadow: inset 0 0 90px 70px #0a1628`) eklendi, kullanıcı onaylı.
  Turuncu dikey ayraç çizgisi (`::after`+`@keyframes fall`) kaldırıldı.
  Form `<label>` etiketleri nötr griye (#94a3b8) döndü — sadece etiketler,
  form-subtitle rengi DEĞİŞMEDİ (kullanıcı onaylı kapsam). register.html
  alt başlığı "Ücretsiz hesap — 30 saniye sürer."a çevrildi. <991px
  gizleme davranışı değişmedi, Playwright ile masaüstü+mobil doğrulandı.

## Genel notlar (yeni oturum için önemli)

- **Deploy notu — migration sayısı:** Bu tur `0147`'ye kadar geldi (0144-0147,
  toplam 4 migration). Madde 10'daki deploy notunda bu sayı kullanılmalı.
- **Pre-existing test hatası (bu turla ilgisi yok, dokunma):**
  `forum/tests.py::test_yoktez_job_daily_limit_normal_user` son commit'te de
  başarısız (`assert 3 == 1`) — bu turun DIŞINDA bir konu, `python -m pytest`
  çalıştırınca "1 failed" görürsen şaşırma.
- **service_promo.html gotcha:** Bibliometri, cronbach, normallik, betimsel,
  korelasyon, t-testi, anova, mann-whitney, kruskal-wallis, ki-kare, lineer/
  lojistik regresyon guest (misafir) görünümlerinin HEPSİ bu tek şablonu
  paylaşıyor. Bu sayfalardan birine özel bir düzenleme istenirse, view'daki
  context dict'e yeni bir bayrak eklenip template'te `{% if %}` ile o bayrağa
  göre gösterilmesi gerekir — aksi halde değişiklik ya hiçbir sayfada
  görünmez ya da yanlışlıkla hepsinde birden görünür.

- **Madde 11 (Ana sayfa "AI çağında iki yol" sağ kartı)** — TAMAMLANDI.
  `forum/templates/forum/home.html` FAZ 4 bölümündeki `.ax-agentic-band-card`
  (836-853. satır) sol karttaki (`.ax-brand-visual`) desenle birebir aynı
  yapıya geçti: `<picture>` (agentic-hero.webp masaüstü / agentic-hero-
  mobile.webp mobil, `source media="(min-width:768px)"`) + `.ax-agentic-
  band-card__overlay` gradient + mevcut başlık/metin/CTA içeriği değişmeden
  overlay içine taşındı. `static/css/home_sections.css`'te eski flat-renk
  flex kutusu CSS'i (`.ax-agentic-band-card { display:flex; background:...}`)
  kaldırılıp `__img`/`__overlay` kuralları eklendi (brand_visuals.css'teki
  `.ax-brand-visual__img`/`__overlay` ile aynı desen); `?v=0112`→`0113`.
  **Kritik gözlem:** agentic-hero görselleri sol karttaki ai-dogrulama
  görselleriyle piksel-piksel AYNI boyutta (1600×893 masaüstü, 800×446
  mobil) — bu yüzden iki kart hiçbir grid-stretch hilesine gerek kalmadan
  doğal olarak eşit yükseklikte oluştu, eski `@media(min-width:768px)
  { .ax-agentic-band-card{height:100%} }` kuralı gereksiz hale gelip
  kaldırıldı. `object-fit:cover;object-position:center` yine de güvenlik
  amaçlı bırakıldı (boyutlar eşit olduğu için normal akışta devreye
  girmiyor). Render'a push edilip (`analizus-dev.onrender.com`) Playwright
  ile doğrulandı: masaüstünde iki kart TAM eşit yükseklik (306.7px),
  380px mobilde neredeyse eşit (189.5 vs 190.4px, <1px fark), yatay taşma
  yok, görsel/overlay/metin doğru render ediyor.

## Kalan işler

Yok — "Merge Öncesi Son Süpürme" turunun 11 maddesi tamamlandı ve `dev`→`main`
merge'i de yapıldı (31 Temmuz 2026). Tek açık nokta: `feature_agentic_landing`
flag'inin prod'da elle açıldığı doğrulanmadı (bkz. Madde 10 deploy notu,
"Merge sonrası hatırlatmalar" #1) — sıradaki oturumda admin panelinden
kontrol edilmeli.

## Yeni oturumda nasıl devam edilir

1. Bu dosyayı (`tasks/todo.md`) ve `CLAUDE.md`'yi oku (CLAUDE.md zaten proje
   kökünde, otomatik yükleniyor).
2. Bu tur tamamlandı — yeni oturumda kullanıcı ya merge onayı verecek ya da
   yeni bir görev başlatacak (`/market/` pazaryeri zenginleştirme veya
   aşağıdaki fikir-aşaması maddelerinden biri gibi).

---

# /market/ Pazaryeri Zenginleştirme

**Durum:** Bekliyor — henüz başlanmadı. Kaynak prompt kullanıcı tarafından
hazırlandı (`analizus_pazaryeri_prompt.md`, bu konuşmada paylaşıldı, repo'da
dosya olarak yok). (Temmuz 2026)

## Amaç
`/market/` işlevsel ama çıplak (stats + ilan listesi + 3 adım) — hedef, sayfayı
gerçek bir pazaryeri vitrinine çevirmek: iki tarafı da (ilan açan / uzman)
karşılayan çift kapı, güven işaretleri, gezilebilir kategoriler, akan sosyal
kanıt.

## Protokol (kullanıcının vurguladığı 3 kritik nokta — sıfır kuralıyla aynı disiplin)
1. **Kuralı tanımla, yerleri saydırma.** İlk iş envanter: `/market/` view +
   template, ana sayfa uzman vitrini sorgusu (`home()`), trust bandı, skill
   chip yapısı incelenip YENİDEN KULLANILACAKLAR belirlenir; plan onaya
   sunulmadan uygulamaya geçilmez.
2. **İstisnayı ilkeyle tanımla, örnekle sabitle.** Bu görev "sıfır kuralı"
   görevinin somut uygulama alanlarından biri: market'teki "İlk analiz işini
   sen tamamla…" boş-durum metni bilinçli bir DAVETTİR, korunur — /hakkimizda/
   "Henüz uzman kadro eklenmedi." gibi bir İTİRAF değildir. Faz 4'teki sayaç
   üçlüsü (Tamamlanan İş / Aktif Uzman / Son 90 Günde) sıfır kuralına bağlanır:
   0 olan sayaç gizlenir, üçü de 0 ise şerit tamamen gizlenir.
3. **Yan etkileri kurala bağla.** Fiyat gizliliği kesin (uzman kartlarında
   fiyat/teklif bilgisi ASLA gösterilmez); sayaç/uzman sorguları ana
   sayfadaki `home_stats`/`home_experts` cache pattern'i yeniden kullanılır,
   çift hesaplama yapılmaz; kategori chip'leri ilan modelinde gerçek bir
   skill/kategori alanı yoksa "görsel chip + hepsi aynı listeye" şeklinde
   sessizce degrade EDİLMEZ — durum kullanıcıya bildirilip birlikte karar
   verilir; OG meta override mekanizması `base.html`'e dokunuyorsa ayrı onaya
   sunulur.

## Fazlar (kaynak promptta tanımlı)
- Faz 1 — Hero Bandı + Çift Kapı (İlan Aç / Uzman Olarak Katıl, market-hero
  görseli yoksa CSS-only placeholder)
- Faz 2 — Kategori Gezinmesi (`?skill=` GET filtresi — ilan modelinde kategori
  alanı yoksa DUR ve sor)
- Faz 3 — Sosyal Kanıt Katmanı (uzman vitrini şeridi, başarı hikayeleri varsa,
  oyunlaştırma/puan bandı)
- Faz 4 — Sıfır Temizliği + SEO (sayaç üçlüsü sıfır kuralı, OG override, SEO
  paragrafı)
- Faz 5 — Deploy Notu

## Sıradaki adım
Kullanıcı başlamamı istediğinde `analizus_pazaryeri_prompt.md` içeriğiyle
Faz 1'i çalıştırıp planı onaya sunacağım. Not: /market/ görevi, sıfır kuralı
görevinden ÖNCE veya SONRA yapılabilir — market'in Faz 4'ü sıfır kuralına
bağlı olduğundan, sıfır kuralı önce bitmişse market Faz 4 onun sonucunu
doğrudan kullanabilir (tekrar iş çıkarmaz), ama bu bir ön koşul değil.

---

# Çalışma Odaları Dönüşümü — Ertelenmiş İşler

**Kaynak:** `analizus_odalar_prompt.md` (repoda dosya olarak yok — yalnızca
sohbet eki olarak verildi, karakter kodlaması bozuk geldiği için repoya
olduğu gibi yazılmadı). Faz 1/2/3/4/5/6 tamamlandı (temmuz 2026, `dev`
branch'inde commit'lendi: faz-1, faz-1 ek, faz-2, faz-4, faz-3, faz-5+6).

## Ertelenen: Faz 3 milestone (proje odası ilerleme çekliste)
Proje tipi (`room_type='project'`) odalar için kurucunun işaretleyebildiği
3–7 maddelik ilerleme kontrol listesi özelliği **şimdilik eklenmedi**.
Karar: yalnızca `room_type` etiketi + görsel ayrım yeterli kabul edildi;
milestone checklist'i (JSONField `milestones = models.JSONField(default=list)`
+ kurucunun inline ekleyip işaretlediği küçük bir POST endpoint'i, üyeler
tam listeyi görür, misafir yalnızca "%40 tamamlandı" bar'ını görür) ayrı
bir görev olarak ele alınacak.

**Ne zaman gündeme gelir:** Kullanıcı proje odaları için ilerleme takibi
isteğini tekrar gündeme getirdiğinde, veya `room_type='project'` kullanımı
yaygınlaştığında.

## Henüz yapılmayan fazlar
- **Faz 7 — Görsel yükseltme:** `static/img/odalar-hero.webp` ve
  `odalar-hero-mobile.webp` artık mevcut (kullanıcı sağladı, henüz repoya
  commit'lenmedi/kullanılmadı). Hero + kart dilini market/agentic sayfalarıyla
  hizala.
- **Faz 8 — SEO + teknik temizlik:** Slug Türkçe karakter düzeltmesi
  (mevcut oda slug'larına dokunma), JSON-LD Event schema, sitemap,
  test hesap temizliği (kullanıcı kararı gerekiyor).

---

# Ana Sayfa & Navbar İyileştirme Turu — Faz 12 + Faz 13 (bekleyen)

**Kaynak:** `analizus_anasayfa_prompt.md` (proje kökünde dosya olarak mevcut).
Faz 0,1,2,3,4,5,6,7,8,9,10,11 tamamlandı ve
`main`'e merge edildi (bkz. memory `project_anasayfa_iyilestirme`). Faz 12 ve
13 o turdan kalan, henüz başlanmamış iki faz.

## Faz 12 — Forum vitrini dönüşümü — TAMAMLANDI (kısmi yayın), Temmuz 2026, dev branch
Ana sayfadaki "Gündemdeki Tartışmalar" 6 jenerik AI konusu (Fine-tuning vs RAG,
Prompt Engineering, Açık kaynak LLM'ler, LLM Halüsinasyonu, GPU olmadan Deep
Learning, LLM etik sınırları — hepsi `seed_forum.py`'den sabit views=3456-5678
ile) `forum/management/commands/remove_generic_seed_topics.py` ile silindi.
Konuyla alakalı ama sahte-seed 4 konuya (SPSS normallik, anket örneklem,
Google Forms, Türkçe NLP model) kullanıcı kararıyla dokunulmadı.

`forum/management/commands/reseed_forum_topics.py` (yeni, idempotent,
`--count N` ile kademeli yayın) 12 yeni konu+uzman cevabını (SEO'ya dikkat
edilerek yazıldı) ve 3 yeni Category'yi (`akademik-surec`, `veri-analizi-bi`,
`ai-ml-agentic`) içeriyor — kaynak: `analizus_forum_seed_konular.md`. Bu turda
`--count 3` ile yalnızca ilk 3 konu (Hakem 2/SEM, Etik kurul onam muafiyeti,
YÖK Tez benzerlik) canlıya alındı; kalan 9 konu dosyada hazır, sonraki
haftalarda `docker compose exec web python manage.py reseed_forum_topics
--count N` ile devreye alınır (kademeli yayın kuralı — hepsi bir günde
açılmaz).

`forum/views.py` — yeni `_trending_topics()` yardımcı fonksiyonu (`home()` ve
`forum_index()` ortak kullanıyor, N+1 yok): sıralama artık `-views` değil,
`Exists()` ile uzman (`account_type='Expert'`) cevaplı konular önce, dolmazsa
son aktif konular. `views` alanı DEĞİŞMEDİ (gerçek sayaç, `topic_detail()`'da
artıyor), sadece sıralama kriteri değişti.

`_gundem_tartismalar.html` — "Uzman cevapladı" rozeti (`ax-badge
ax-badge--primary`) + cevap sayısı eklendi. `trend_topics.css`'te forum
varyantı meta satırına `flex-wrap`/`max-width` eklendi (rozet mobilde
taşmasın diye), `?v=0001`→`0002` bump edildi (forum_index.html + home.html×2).

Doğrulama: `python -m pytest forum/tests.py` → 52/53 geçti (tek hata
`test_yoktez_job_daily_limit_normal_user`, bu turla ilgisiz, önceden bilinen).
Django shell üzerinden `/` ve `/forum/` render edildi, "Uzman cevapladı" 5
kez görünüyor, "Fine-tuning" metni artık hiç yok. Playwright ile görsel
(mobil taşma) doğrulaması henüz yapılmadı — sıradaki oturumda önerilir.

**Kalan iş:** 9 konunun kademeli yayını (haftada 2-3, `--count` artırılarak)
+ her yayından sonra ilgili uzman hesabın cevabının gerçekten "vitrin
kalitesinde" durduğunu gözden geçirmek.

## Faz 13 — Dropzone akışı: vaat + triyaj şeridi
Hero dropzone'a dosya bırakan kullanıcı `/analiz/?from=hero` araç listesine
düşüyor ama analiz bilmeyen kullanıcı 18 araç arasında yol göstericisiz
kalıyor — H1 "yapamıyorsan yapan burada" vaadiyle çelişki.

- **Keşif (metinden önce zorunlu):** dosya hero'da sunucuya mı yükleniyor,
  tarayıcıda mı tutuluyor; misafir kullanabiliyor mu; `/analiz/`de dosya
  durumu nasıl taşınıyor.
- **Triyaj şeridi:** `/analiz/`de yalnızca `from=hero` + dosya seçili durumda,
  rozetin altına üç link: Hangi Test? sihirbazı · AI Asistan'a sor
  (`axOpenAiWidget`) · Bu işi uzmana bırak (`?source=analiz_triyaj`). Yeni
  motor yok, mevcut hedefler kullanılır.
- **Hero mikrometni (keşif sonrası):** vaat gerçeğe göre yazılır, yalnızca
  teknik olarak doğrulanan ifadeler kullanılır; uygulamadan önce kullanıcıya
  sunulur.
- ERTELENEN (bu fazın kapsamı dışı): kolon-tipine dayalı gerçek öneri motoru.

## Sıradaki adım
Kullanıcı başlamamı istediğinde önce Faz 12 için karar noktasını (komut mu
elle mi) sorup uygulayacağım; Faz 13 keşif adımıyla başlayacak. İkisi
birbirinden bağımsız, istenen sırada yapılabilir.

## Faz 13 — DURUM: mikrometin + triyaj şeridi tamamlandı (temmuz 2026)
Keşif + uygulama bitti: hero dropzone altına "Kayıt gerekmez — hemen dene"
mikrometni (`forum/templates/forum/home.html` + `static/css/hero.css`,
`.ax-hero-dropzone__trust`, `?v=0107`), `/analiz/` sayfasına `from_hero`
rozetinin altına triyaj şeridi (Hangi Test? · AI Asistan'a sor · Bu işi
uzmana bırak `?source=analiz_triyaj`) eklendi
(`istatistik/templates/istatistik/analiz_hub.html`).

**Doğrulanan mimari bulgular (Faz 13 keşfinden):**
- Hero'dan yüklenen dosya gerçekten sunucuya gidiyor, session'da RAM'de
  tutuluyor (`istatistik/services/job_runner.py` — `_session_datasets`,
  `_pending_file_contents`); disk/DB'ye yazılmıyor.
- Login zorunlu değil — misafir hem yükleyip hem analiz çalıştırabiliyor
  (`is_demo=not request.user.is_authenticated` deseni).
- Production tek process/tek container (Hetzner: `docker-compose.yml` tek
  `web` servisi, `Dockerfile` CMD'si tek `daphne` process, nginx tek
  `web:8000` upstream'ine proxy; Render/`Procfile` de aynı). **Modül seviyesi
  dict için multi-worker veri kaybı riski şu an gerçek değil** — yalnızca
  ileride yatay ölçeklendirilirse (birden fazla container/process) mimari
  kırılır, dikkat edilecek kısıt olarak not düşülüyor.
- Dosya boyutu limiti zaten var: `MAX_UPLOAD_SIZE = 5MB`
  (`analizdestek/settings.py:529`), `hero_upload` kontrol ediyor — ek iş yok.

## `_session_datasets` TTL temizliği — TAMAMLANDI (31 Temmuz 2026)
Faz 13 keşfinde bulunan bellek sızıntısı riski (terkedilmiş veri setleri
süresiz RAM'de birikiyor) çözüldü ve canlıda doğrulandı:
- `istatistik/services/job_runner.py` — `_session_datasets` artık
  `(content, filename, saved_at)` tutuyor, `SESSION_DATASET_TTL_SECONDS = 2 saat`
  (kullanıcı kararı — `SESSION_COOKIE_AGE` ile hizalı, 24 saat önerisi session
  zaten 2 saatte geçersiz olduğu için gereksiz bulundu), yeni
  `cleanup_expired_session_datasets()` fonksiyonu eklendi.
- `forum/api_views.py` + `forum/urls.py` — mevcut `/api/cron/*` desenine uygun
  yeni `cron_cleanup_session_datasets` endpoint'i (`X-Cron-Secret` doğrulamalı).
  DB değil RAM temizlediği için (ayrı process bu dict'e erişemez) yalnızca bu
  HTTP-tetiklemeli desen çalışır — management command seçeneği mimari olarak
  elenmiş oldu.
- `dev`'den `main`'e fast-forward merge edildi, Hetzner'e deploy edildi
  (`git pull` + `restart web`/`nginx`, migration yok), crontab'a saatlik satır
  eklendi (`0 * * * * curl ... cleanup-session-datasets/?secret=...`).
- Canlı doğrulama: doğru secret → `{"success": true, "deleted": 0}`, yanlış
  secret → `403`; `crontab -l` ile satır teyit edildi.

Aynı turda ayrıca bulunup düzeltilen ilgisiz bug: `cleanup-pageviews` cron
satırı www'suz domain kullandığından 301'e takılıp hiç çalışmıyordu (canonical
domain `www.analizus.com`'a dönmüş, crontab güncellenmemişti); `cleanup-s3`
ve `cleanup-attachments` dokümantasyonda "Aktif" görünüp crontab'da hiç
yoktu. Üçü de düzeltildi/eklendi — detay: `analizus.md` §23.

## PageSpeed Insights — Kalan Optimizasyon Fırsatları (ertelendi, temmuz 2026)

MathJax/Prism/Font Awesome kaldırma, footer kontrast (WCAG AA) ve
bootstrap-icons preload (CLS 0.102→0.009) düzeltmeleri uygulandı ve
`main`'e merge edildi (masaüstü 86→96, mobil 70→80, erişilebilirlik
96→100). Kullanıcı kararıyla burada duruldu — kalanlar ayrı, daha büyük
işler:

- [ ] **Kullanılmayan CSS (Bootstrap, 43 KiB)** — ayrı görev olarak zaten
  planlı, bkz. bu dosyanın başındaki "Bootstrap Kaldırma — Kademeli
  Migration Planı"
- [ ] **Render-blocking `bundle.css`** (188-190ms) + **Ağ bağımlılık ağacı**
  (kritik yol ~588ms) — aynı kök neden: `bundle.css` above-the-fold
  navbar/layout stilini içeriyor, deferred yapmak FOUC riski taşır; kritik
  CSS ayıklama (inline critical CSS + async geri kalan) gerektirir
- [ ] **Yandex Metrica** — verimli önbellek (71 KiB) + kullanılmayan JS
  (43 KiB) + olası uzun görevler; üçüncü parti, init'i `requestIdleCallback`
  ile ertelemek TBT'yi düşürür ama webvisor/bounce-tracking doğruluğunu
  etkileyebilir — iş kararı, kullanıcıya sorulmadan yapılmayacak
- [ ] **Zorunlu yeniden düzenleme** (~103ms ilişkilendirilmemiş) — kesin
  kaynağı Chrome DevTools Performance profiliyle tespit edilmeli, first-party
  JS'te (navbar.js/ax-dropdown.js/widget_collapse.js/main.js) layout-thrashing
  deseni yok (grep ile doğrulandı)
- [ ] **28 birleştirilmemiş (uncomposited) animasyon** — `border-color`/
  `background-color`/`box-shadow` geçişleri ax- tasarım sisteminde ~20 CSS
  dosyasına yaygın, düzeltmek geniş kapsamlı bir tasarım sistemi revizyonu
  gerektirir
- [x] **Görsel boyutu** (`ai-dogrulama.webp`/`agentic-hero.webp`) —
  1600×893 → 1100×614 küçültüldü, kullanıcı kararıyla burada bırakıldı
  (retina netliği öncelikli, 30 KiB'lik kalan Lighthouse uyarısı kabul edildi)
