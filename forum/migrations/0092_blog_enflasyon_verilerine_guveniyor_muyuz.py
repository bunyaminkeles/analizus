# Dosya Adı: forum/migrations/0092_blog_enflasyon_verilerine_guveniyor_muyuz.py

from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='ekonometri-veri-politikasi',
        defaults={'name': 'Ekonometri & Veri Politikası'}
    )

    content = """<h2>Enflasyonun Ekonometrisi: Veri Tartışmalarının Kökeni</h2>
<p>Türkiye'de makroekonomik istatistikler üzerine yapılan tartışmaların merkezinde enflasyon verileri (TÜFE - Tüketici Fiyat Endeksi) yer alıyor. Türkiye İstatistik Kurumu (TÜİK) tarafından yayımlanan resmi veriler ile Bağımsız Enflasyon Araştırma Grubu (ENAG) gibi sivil inisiyatiflerin hesaplamaları arasındaki makasın giderek açılması, sadece politik bir sorun değil, aynı zamanda ciddi bir <strong>ekonometrik ve metodolojik analiz</strong> konusudur.</p>

<h2>TÜFE Nasıl Hesaplanır? Sepet ve Ağırlıklandırma Sorunu</h2>
<p>Enflasyon, teoride temsili bir tüketicinin tükettiği mal ve hizmetlerden oluşan bir "sepetin" belirli bir dönemdeki maliyet değişimidir. Metodolojik ayrışmaların başladığı temel noktalar şunlardır:</p>
<ul>
  <li><strong>Madde Sepeti ve Ağırlıklar:</strong> Her toplumun tüketim alışkanlığı farklıdır. Gıdanın veya kiranın sepetteki ağırlığı (yüzdesi) ne olmalıdır? TÜİK, ağırlıkları Hanehalkı Bütçe Anketi sonuçlarına göre güncellerken, bağımsız grupların farklı anket verileri kullanması, özellikle gıda enflasyonu yüksek olduğunda manşet enflasyonda devasa farklara yol açar.</li>
  <li><strong>Fiyat Derleme Yöntemi:</strong> Geleneksel anketör bazlı fiyat toplama yönteminden, barkod (scanner) verileri ve web kazıma (web scraping) yöntemlerine geçiş. ENAG, saatlik web kazıma yöntemlerini yoğun olarak kullanırken, TÜİK hem web kazıma hem de saha verilerini entegre etmektedir.</li>
</ul>

<h2>Hedonik Fiyat Endeksi: Kalite mi, İllüzyon mu?</h2>
<p>Ekonometride enflasyon ölçümünün en tartışmalı alanlarından biri kalite düzeltmeleridir. Örneğin, geçen yıl 10.000 TL olan bir bilgisayar bu yıl 15.000 TL olduysa, enflasyon %50 midir? Eğer yeni bilgisayarın belleği, işlemcisi veya ekranı eskisinden daha iyiyse, fiyat artışının bir kısmı enflasyon değil, kalite artışıdır.</p>
<p>TÜİK gibi resmi kurumlar, bu kalite değişimini fiyattan arındırmak için <strong>Hedonik Regresyon</strong> modelleri kullanırlar. Ancak kamuoyunun enflasyonu hissetme şekli ile hedonik modellerin çıktıları çoğu zaman uyuşmaz, bu da kurumsal veri güvenilirliği konusunda şüpheleri körükler.</p>

<h2>Veri Şeffaflığı ve Beklenti Enflasyonu</h2>
<p>Ekonometrik modeller (örneğin Phillips Eğrisi tahminleri) ekonomik ajanların (halkın ve yatırımcıların) beklentilerine göre şekillenir. Merkez bankalarının en büyük korkusu enflasyon beklentilerinin bozulmasıdır.</p>
<p>Eğer resmi kuruma duyulan güven azalırsa ve halk kendi enflasyonunu farklı kurumlara (ENAG, İTO vb.) veya kendi gözlemine (hissedilen enflasyon) göre şekillendirirse, ücret/fiyat sarmalı (wage-price spiral) kontrolden çıkar. Bu yüzden resmi veri üreticilerinin metodolojilerini (özellikle sepet madde fiyatlarını) en ince ayrıntısına kadar şeffaf bir şekilde araştırmacılara açması, spekülasyonları bitirmenin tek bilimsel yoludur.</p>
<hr>
<small>
<strong>Kaynakça:</strong><br>
Diewert, W. E. (2001). The consumer price index and index number purpose. Journal of Economic and Social Measurement, 27(3-4), 167-248.<br>
Triplett, J. E. (2006). Handbook on hedonics and quality adjustments in price indexes: Special application to information technology products. OECD.<br>
TÜİK. (2023). Tüketici Fiyat Endeksi Metadokümanı.
</small>"""

    BlogPost.objects.get_or_create(
        slug='enflasyon-verilerine-guveniyor-muyuz-tuik-enag-resmi-veri-tartismasi',
        defaults={
            'title': 'Enflasyon Verilerine Güveniyor muyuz? TÜİK, ENAG ve Resmi Veri Tartışmasının Ekonometrik Anatomisi',
            'excerpt': 'TÜFE hesaplamalarındaki metodolojik farklar, hedonik regresyon uygulamaları ve TÜİK ile bağımsız ölçümler arasındaki enflasyon makasının ekonometrik nedenlerini inceliyoruz.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0091_blog_survival_analizi_101'),
    ]

    operations = [
        migrations.RunPython(ekle, migrations.RunPython.noop),
    ]