FAZ 1: Dashboard Layout ve Grid Optimizasyonu
Amacı: Sayfadaki o "kopuk" ve "boş" duruşu düzeltmek, sidebar'ları ve ana içeriği orantılı hale getirmek.

# FAZ 1: Layout Dengesi ve Grid Optimizasyonu

## Görev
Ana sayfadaki sidebar'lar ve orta içerik alanı arasındaki orantısız boşlukları gider. Siteyi bir "yönetim paneli / dashboard" estetiğine kavuştur.

## Teknik Kurallar
1. **Grid Dengeleme:** Bootstrap grid'ini kullanarak `row` içerisinde `col-lg-3` (sidebarlar için) ve `col-lg-6` (ana içerik) şeklinde yeniden düzenle. Ana içeriği ekranın ortasında daha baskın hale getir.
2. **Derinlik (Dark Mode):** Tüm `.ax-` kartlarına `border: 1px solid rgba(255, 255, 255, 0.05)` ve `box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3)` ekle. Bu, kartları arka plandan hafifçe kaldırarak o ruhsuz flat görüntüyü kıracak.
3. **Spacing:** Kartların dış boşluklarını (margin) `var(--space-6)` ile standardize et. Sayfanın en üstünden en altına kadar her bölümün arasında nefes alacak alan olsun.

FAZ 2: Quiz Modülü (Modernizasyon)
Amacı: Hata veren ve sönük kalan Quiz modülünü modern bir interaktif bileşene dönüştürmek.

# FAZ 2: Quiz Modülü Modernizasyonu

## Görev
Hata veren quiz modülünü tamamen yeniden yaz.

## Teknik Kurallar
1. **Görsel:** Quiz kartına `background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary))` ver. 
2. **Şıklar:** Bootstrap'in `btn` class'larını kullanma. Bunun yerine `ax-option` class'ı oluştur. `border: 1px solid var(--border-default)`, `padding: 12px`, `border-radius: var(--radius-md)`.
3. **Etkileşim:** Şıkkın üzerine gelindiğinde `border-color: var(--accent-primary)` olsun. 
4. **Hata Giderme:** Quiz verilerini bir JS objesi olarak koda göm (hardcode). `fetch` veya `async` hata risklerini minimize et. Kullanıcı şıkka bastığında butonlar anında `disabled` olsun, doğru/yanlış animasyonu CSS sınıfı ile (`.is-correct` / `.is-wrong`) yönetilsin.

FAZ 3: Görsel Hiyerarşi (Tipografi ve İkonlar)
Amacı: Küçük ve okunaksız duran sidebar metinlerini ve boş doküman ikonlarını düzeltmek.

# FAZ 3: Tipografi ve İkonografi

## Görev
Sitenin görsel hiyerarşisini güçlendir.

## Teknik Kurallar
1. **Tipografi:** Sidebar'daki (Popüler Tartışmalar vb.) tüm metinlerin `line-height` değerini `1.6` yap. Başlıkları `font-weight: 600` yap ve `font-size` değerlerini mevcut hallerine göre %10 artır.
2. **İkonografi:** "Güncel Akademik İçerikler" kısmındaki boş doküman ikonlarını kaldır. Yerine `Lucide-icons` (veya benzeri bir setten) her dosya türüne göre (PDF, Makale, Veri, AI) özel SVG ikonlar koy.
3. **Vurgu:** Sidebar başlıklarına (Popüler Tartışmalar gibi) `border-left: 3px solid var(--accent-primary)` ekle. Bu, gözü sidebar'a daha hızlı çeker.

FAZ 4: Navbar ve Hero "Bütünleşme"
Amacı: Navbar ile Hero arasındaki kopukluğu gidermek.

# FAZ 4: Navbar ve Hero Entegrasyonu

## Görev
Sayfanın en üstündeki kopukluğu gidererek sayfayı profesyonel bir "giriş" haline getir.

## Teknik Kurallar
1. **Gradient Blur:** `navbar` altına hemen, `ax-hero`'nun en üst kısmına `background: linear-gradient(180deg, var(--bg-primary) 0%, rgba(99, 102, 241, 0.05) 100%)` gibi çok ince, sayfaya derinlik veren bir geçiş ekle.
2. **Hero:** `ax-hero` içeriğini `padding-top: 100px` (desktop) olacak şekilde aşağı çek. Başlık (`h1`) ile alt açıklama (`p`) arasındaki boşluğu `margin-bottom: var(--space-6)` ile artır.
3. **CTA:** Hemen Başla butonuna `box-shadow: 0 0 20px rgba(99, 102, 241, 0.3)` ekle. Butonun "tıklanabilir" olduğunu hissettir.

Bu prompt, sidebar'daki widget'ları "yıkıp" onları ana gövdeye "modern kartlar" olarak geri inşa etmeni sağlar.

# FAZ 8: Sidebar'ları Yık, Widget'ları Modernize Et

## Görev
Sidebar'lardaki (Popüler Konular, Bilim Haberleri, İstatistikler, Değerlendirmeler) widget'ları sidebar'dan çıkar. Bunları orta alanda, Bootstrap `row/col` yapısını kullanan, modern, geniş ve okunaklı "Bölüm Kartlarına" dönüştür.

## Teknik Kurallar
1. **Sidebar'ı İptal Et:** Sitedeki tüm `col-lg-3` veya `col-lg-4` sidebar yapılarını kaldır. İçeriği tek bir `container` içinde topla.
2. **Widget Dönüşümü:**
   - **Popüler Konular + Bilim Haberleri:** Sayfanın orta kısmına bir `row` aç. `col-md-6` olarak yan yana iki büyük kart (widget) yap. İsimlerini "Gündemdeki Tartışmalar" ve "Akademik Haberler" olarak değiştir.
   - **İstatistikler + Değerlendirmeler:** Bunları da "Platform Verileri" başlığı altında, 4 sütunlu bir `row` içinde, ikonlu ve büyük fontlu dashboard kutucuklarına dönüştür.
3. **Görsel Kurallar:**
   - Sidebar'daki o sıkışık listeleri, geniş `card` içine al. `padding: 24px` ver.
   - İkon kullanımını artır (örn: Popüler Tartışmalar için alev, haberler için gazete ikonu).
   - Sidebar'da dikey akıp giden o dar listeleri, 2 sütunlu modern bir "grid list"e çevir.

## Beklenen
- Sayfa artık "sidebar bataklığı" gibi değil, "dergi/platform" gibi görünecek.
- İçerik alanı genişlediği için "boşluk" hissi kaybolacak.
- Sayfa aşağı doğru akarken her bölüm bir "bölüm" gibi duracak, yan kolonlar yüzünden bölünmeyecek.