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
