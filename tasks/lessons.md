# Dersler

## CSS dosyası düzenlenince cache-busting versiyonunu artır
**Ne oldu:** Faz 1'de `static/css/base.css`'e ~330 satır yeni CSS eklendi
(alert/modal/dropdown/form bileşenleri), ama `templates/base.html`'deki
`<link href="...base.css?v=0100">` versiyon numarası değiştirilmedi. Faz 2'de
bu yeni CSS'e bağımlı modal markup'ı devreye alınınca, tarayıcı eski
`base.css?v=0100`'ü önbellekten sunduğu için modallar gizlenmedi — sayfa
akışının içinde çıplak `<div>` gibi göründüler (kullanıcı ekran görüntüsüyle
bildirdi).

**Kural:** `static/css/*.css` veya `static/js/*.js` dosyasının **içeriğini**
değiştiren her görevde, o dosyayı referans eden template'teki `?v=XXXX` sürüm
parametresini de artır. Yeni dosya oluşturmak (ilk kez link/script eklemek)
bu kuralın dışında — sadece **var olan** dosyayı düzenlerken geçerli.

**Nasıl uygulanır:** Bir CSS/JS dosyasını Edit ile değiştirdikten hemen sonra,
o dosyayı `{% static %}` ile çağıran tüm template'lerde `?v=` değerini kontrol
et ve bir artır (örn. `0100` → `0101`). Değişikliği "tamamlandı" olarak
raporlamadan önce bu adımı unutma.

## i18n: "kalan Türkçe" taramasını özel harfe (ç/ğ/ı/ş) göre yapma (23 Eylül 2026)

İstatistik araçlarını çevirirken hem işaretleyici hem doğrulama taraması
yalnızca Türkçe özel harf içeren metinleri Türkçe saydı. "Metodoloji",
"Normallik Testi Nedir?", "Normal kabul edilir", "Karar:", "Hesapla" gibi
özel harfsiz metinler iki aşamada da görünmez kaldı; kullanıcı ekran
görüntüsüyle bildirdi. Ayrıca Python regex'inde `re.I` ile `[İ]` karakter
sınıfı düz `i` ile eşleşir — dedektör her İngilizce metni yakaladı.

**Kural:** Şablon işaretlemede "Türkçe mi?" sezgisine güvenme. Önce
trans'sız TÜM metin düğümlerini (harf içeriğinden bağımsız) listele, elle
ayıkla (kaynakça/formül/evrensel terim hariç), sonra sar. Doğrulamada da
render edilen sayfada özel harfsiz Türkçe kelime listesiyle tara; karakter
sınıfını `re.I` olmadan, kelime listesini ayrı regex'le kontrol et.
Kısa ve yeniden kullanılan msgid'lerin (ör. "Orta") mevcut çevirisini
bağlama uygunluk için kontrol et; farklı anlamdaysa `context` ekle.

## Django `{# #}` yorumu tek satırlıktır (24 Eylül 2026)
**Hata:** Gizlilik şablonuna çok satırlı `{# … #}` yorum yazıldı → Django bunu
yorum saymadı, metin sayfada göründü (render testinde yakalandı).
**Kural:** Çok satırlı şablon yorumu için her zaman `{% comment %}…{% endcomment %}`.
Şablona yorum ekledikten sonra render edilmiş HTML'de `{#` / `#}` ara.

## grep -v ile dosya adı filtrelerken alt dizgi tuzağı (25 Eylül 2026)
**Hata:** "Silme işlemini yapan kod var mı?" aranırken `grep ... | grep -v
"views.py\|models.py"` kullanıldı — `views.py` alt dizgisi `api_views.py`'yi de
eledi; var olan cron (`cron_process_account_deletions`) görülmedi ve kullanıcıya
"silen kod yok" diye YANLIŞ bulgu raporlandı, gizlilik metninden gereksiz yere
bir ifade çıkarıldı. Ayrıca önceki aramada `head -10` sonuçları kesmişti.
**Kural:** "X yok" demeden önce filtresiz tam arama yap (`grep -rn` + `head`
yok); dosya elerken tam yol/`--exclude` kullan (`grep -v "/views.py:"` değil
`--exclude=views.py`). Olumsuz bulguyu raporlamadan önce analizus.md'de de ara
(orada dokümante edilmişti). Yokluk iddiası = en yüksek doğrulama çıtası.

## polib ile fuzzy temizlerken tüm "previous" alanlarını sil (25 Eylül 2026)
**Hata:** Çeviri betiği fuzzy girişte yalnızca `e.previous_msgid=None` yaptı;
girişte `#| msgid_plural` (previous_msgid_plural) kalınca msgfmt "syntax error"
verdi ve compilemessages TÜM çevirileri derlemedi (sessiz değil ama kolay kaçar).
**Kural:** fuzzy temizlerken `previous_msgid`, `previous_msgid_plural`,
`previous_msgctxt` üçünü birden None yap; compilemessages çıktısında "error"
kontrolünü her seferinde yap.

## "Bir sonraki maddeye kadar" ile blok değiştirme sessizce içerik siler (26 Eylül 2026)
**Hata:** todo'da bir maddeyi güncellerken bloğun sonunu `s.index("- [ ]", a+5)`
(bir sonraki AÇIK madde) ile belirledim; aradaki 5 tamamlanmış [x] madde ve
"**B.**" başlığı da silindi, bir gün sonra fark edildi (69e8947).
**Kural:** Blok sonunu "bir sonraki madde başlangıcı" (`\n- [` — açık VEYA kapalı)
ya da açık bir bitiş işaretiyle belirle; değişiklikten sonra `git diff` ile
silinen satır sayısını kontrol et — beklenenden fazlaysa commit etme.


## 26 Eylül 2026 — Bağlantı envanteri: sabit href ≠ TR-only sayfa
**Hata:** EN/DE bağlantı envanterinde `href="/openalex/"` (sabit yazılmış, `{% url %}` değil)
öneksiz göründüğü için "TR-only / i18n dışı" sayıldı; oysa `openalex/` ve `semantic-scholar/`
i18n_patterns içindeydi. Kullanıcıya "arayüzü çevrilmemiş" diye sunuldu, C grubunda gizlendi;
Semantic Scholar tabloda adıyla hiç geçmedi (hub linki gizlenince dolaylı gizlendi).
**Kural:** Bir hedefin dil durumunu href'in önekine bakarak değil, (1) URL'in i18n_patterns
içinde olup olmadığı (`/en/<yol>` 200 mü) ve (2) EN render'ında görünür Türkçe metin oranı
ölçülerek belirle. Gizleme/kaldırma tablosunda dolaylı etkilenen her aracı ADIYLA yaz.

## 27 Eylül 2026 — Test sonucu commit zincirinde durdurucu olmalı
**Hata:** `pytest ...; ... && git commit` zincirinde pytest `;` ile ayrıldığı için 1 başarısız
testle commit+push yapıldı (dev'e; main'e gitmedi, hemen düzeltildi).
**Kural:** Commit'ten önce testi `&&` ile bağla ya da çıktıyı okuduktan SONRA ayrı adımda commit et.
Ayrıca: STORAGES/statik değişikliği testleri DEBUG=False nedeniyle manifest'e bağlar →
test_settings'te düz StaticFilesStorage.

## 27 Eylül 2026 — Metin tarayıcılarında `\w` Türkçe harfleri de kapsar
**Hata:** "Teknik sabit mi?" filtresi `re.fullmatch(r'[#\w\-\.:/]*', s)` tek kelimelik Türkçe
metinleri ("Yıl", "Diğer", "Düzeltme") de teknik sabit sayıp atladı (Python `\w` Unicode harfleri
kapsar). Sonradan "sarılmamış Türkçe sabit" taramasıyla yakalandı.
**Kural:** Toplu sarmadan SONRA her zaman ters kontrol yap: gettext'e sarılmamış ve ç/ğ/ı/ö/ş/ü
içeren sabitleri listele; ASCII Türkçe kelimeler için ayrıca elle göz at.

## 28 Eylül 2026 — polib `save()` tüm .po dosyasını yeniden sarar
**Hata:** İki msgid eklemek için `polib.pofile(...).save()` kullandım; dosyanın tamamı yeniden sarıldı, EN/DE
po'larda ~5800 satırlık gereksiz diff oluştu (commit'ten önce `git diff --stat` ile fark edilip geri alındı).
**Kural:** Birkaç yeni giriş için po dosyasına düz metin olarak ekle (append) + `compilemessages`; polib yalnız
toplu düzenlemede ve orijinal wrapwidth ile. Her çeviri değişikliğinden sonra `git diff --stat` — beklenenden
büyükse commit etme.

## 28 Eylül 2026 — Doğrulamadan "zaten çevrili" deme
**Hata:** F adımını anlatırken "üretilemeyen analiz nedenleri (B adımı) zaten çevrili" dedim; msgid taraması 16'sının
çevrilmemiş olduğunu gösterdi (düzeltip kullanıcıya bildirdim).
**Kural:** Bir metnin çevrili/var/yok olduğunu söylemeden önce po'da ara (polib ile `(msgctxt, msgid)` kümesi). Kapsam
listesi verirken sayıyı taramadan çıkar, tahminden değil.

## 28 Eylül 2026 — Türkçe kesme işareti tek tırnaklı Python string'ini kırar
**Hata:** `gettext('... 17'ye kadar ...')` — kaçırılmamış `'` SyntaxError → `urls` import edilemedi, dev'de tüm sayfalar
500 (render testinde yakalandı). Toplu metin değişikliğini Python replace betiğiyle yaparken oldu.
**Kural:** Türkçe metin içeren .py düzenlemesinden sonra `python3 -c "import ast; ast.parse(open(f).read())"` çalıştır;
tek tırnaklı string'e "'ye/'de/'nin" yazarken `\'`.

## 28 Eylül 2026 — İmaj yeniden build edilince elle kurulan araçlar gider
**Olay:** `bibtexparser` sabitlemesi için `--build` sonrası container'da `msgfmt` (gettext) ve `polib` yoktu — daha önce
elle kurulmuşlardı. Ayrıca sürümsüz `bibtexparser` build'de 2.x gelip BibTeX'i kırmıştı.
**Kural:** API'sine bağlı paketlere sürüm sabitle; build sonrası etkilenen akışı uçtan uca dene. Çeviri derlemesi
host'ta `msgfmt -c` (analizus.md §26/§28.5).

## 29 Eylül 2026 — Container'da `makemigrations` yeni app klasörünü root sahipli yaratır
**Olay:** Yeni `pubmed` app'inde `migrations/` klasörü container içinde (root) oluştu. main'e geçişte git bu
root sahipli dosyaları silemedi → `merge --ff-only dev` ve `checkout dev` "untracked files would be overwritten"
ile durdu. Diğer app'lerde klasör kullanıcıya ait olduğu için sorun çıkmadı.
**Kural:** Yeni app'in `migrations/` klasörünü host'ta oluştur (`mkdir -p app/migrations && touch .../__init__.py`)
ya da container'da oluşturduktan sonra `docker compose exec -T web chown -R 1000:1000 /app/<app>` yap. Commit
öncesi `stat -c '%U' <yeni dosyalar>` ile sahibi kontrol et.

## 29 Eylül 2026 — Şablon değişikliği restart olmadan görünmez (cached loader)
**Olay:** XSS testinde düzeltme öncesi şablonu geri koyup testi çalıştırdım; sonuç "güvenli" çıktı — sunucu önceki
şablonu önbellekten veriyordu. Restart sonrası eski sürümde yük 7 kez çalıştı.
**Kural:** Şablon değiştirip tarayıcı/test client ile doğrulamadan önce `docker compose restart web` (+ nginx). Bir
testin açığı gerçekten yakaladığını, düzeltme öncesi sürümde BAŞARISIZ olduğunu görerek kanıtla.

## 29 Eylül 2026 — Doğrulama betiği sağlam veriyi "bozuk" saydı (varsayılan dosya formatı)
**Hata:** Yedek betiğinde "dump complete" satırını son 3 satırda aradım; yeni pg_dump sonuna `\unrestrict` ekliyor →
sağlam yedek "eksik" diye reddedildi. Formatı görmeden varsaydım.
**Kural:** Bir dosya formatına dayanan doğrulama yazmadan önce gerçek örneğin sonunu/başını oku (`tail -c 300`); asıl
kanıt olarak yedeği geçici container'a geri yükle.

## 29 Eylül 2026 — API anahtarı hata metninden sızar
**Olay:** OpenAlex anahtarı URL parametresi → `requests` hata metni → `mark_failed(str(e))` ile kullanıcıya gösteriliyordu;
PubMed/OpenAlex traceback'leri log'a yazıyordu.
**Kural:** Dış API hatasını kullanıcıya asla `str(e)` ile gösterme; anahtar URL'deyse istisnayı kaynağında temizleyip
yeniden fırlat. Testte eski kodda sızıntının GÖRÜLDÜĞÜNÜ de kanıtla.

## 30 Eylül 2026 — Google'ın gördüğü şablon, düzenlenen şablon değildi
**Olay:** SEO başlık/açıklama değişikliğini tarama sayfalarının `landing.html`'ine yaptım; anonim ziyaretçi (Googlebot
dahil) `service_promo.html` görüyor ve başlığı view'daki `promo_title`/`promo_description`'dan alıyor. Haziran'daki
"landing keyword" turu da aynı dosyaları düzenlemişti — büyük olasılıkla Google'a hiç ulaşmadı.
**Kural:** SEO değişikliğinden önce sayfayı **oturumsuz** `curl` ile çek, `<title>`/description'ın hangi şablon/context'ten
geldiğini bul; doğrulamayı da oturumsuz yap. Çeviri dosyasında toplu polib `save()` tüm dosyayı yeniden sarar (yüzlerce
satır fark) — tek girdi değişikliğini metin olarak yap, `git diff --stat` ile kontrol et.
