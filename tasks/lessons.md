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
