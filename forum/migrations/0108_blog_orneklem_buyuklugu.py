from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Tez İçin Kaç Anket Doldurulmalı? Örneklem Büyüklüğü Nasıl Hesaplanır?</h2>
<p>"Kaç kişiye anket uygulamalıyım?" sorusu, tez danışmanlarının en çok duyduğu ve öğrencilerin en çok kafasının karıştığı sorulardan biridir. "100 yeterli mi?", "200 mi olmalı?" gibi muğlak cevaplar yerine, örneklem büyüklüğünü istatistiksel bir temele oturtmanız hem akademik güvenilirliğinizi artırır hem de savunmada sizi rahatlatır.</p>

<h2>Örneklem Büyüklüğünü Belirleyen 3 Temel Faktör</h2>
<p><strong>1. Güven Aralığı (%95 veya %99):</strong> Ne kadar yüksekse o kadar fazla katılımcı gerekir. Sosyal bilimlerde standart %95'tir.</p>
<p><strong>2. Hata Payı (%5 veya %3):</strong> Ne kadar düşükse o kadar fazla katılımcı gerekir. %5 hata payı genellikle yeterli kabul edilir.</p>
<p><strong>3. Evren Büyüklüğü:</strong> Ulaşmak istediğiniz hedef kitlenin büyüklüğü. Evren büyüdükçe gereken örneklem de büyür; ancak belirli bir noktadan sonra artış yavaşlar.</p>

<h2>Cochran Formülü ile Örneklem Hesaplama</h2>
<p>Eğer evren büyüklüğünü bilmiyorsanız veya çok büyükse (N &gt; 10.000) Cochran formülü kullanılır:</p>
<p><strong>n₀ = (Z² × p × q) / e²</strong></p>
<p>Burada: Z = 1.96 (%95 güven için), p = 0.5 (maksimum örneklem için), q = 1-p = 0.5, e = 0.05 (hata payı). Hesaplama: n₀ = (1.96² × 0.5 × 0.5) / 0.05² = <strong>384 kişi</strong>.</p>

<h2>Analiz Türüne Göre Minimum Örneklem Büyüklüğü</h2>
<table>
  <thead><tr><th>Analiz Türü</th><th>Minimum Örneklem</th><th>Gerekçe</th></tr></thead>
  <tbody>
    <tr><td>t-Testi (2 grup)</td><td>Grup başına 30+</td><td>Merkezi Limit Teoremi</td></tr>
    <tr><td>ANOVA (3+ grup)</td><td>Grup başına 20-30+</td><td>Her hücrede yeterli gözlem</td></tr>
    <tr><td>Korelasyon</td><td>50+</td><td>Güvenilir r tahmin</td></tr>
    <tr><td>Çoklu Regresyon</td><td>Değişken başına 10-20</td><td>5 değişken → min 50-100 kişi</td></tr>
    <tr><td>Faktör Analizi</td><td>Madde başına 5-10</td><td>20 madde → min 100-200 kişi</td></tr>
  </tbody>
</table>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Araştırmanın örneklem büyüklüğü Cochran (1977) formülü esas alınarak hesaplanmıştır. %95 güven aralığı ve %5 hata payı ile evrenin 5.000 kişiden oluşması durumunda gereken minimum örneklem büyüklüğü 357 olarak belirlenmiştir. Ölçek kayıpları ve eksik veriler göz önüne alınarak örnekleme 400 kişi dahil edilmiş, bunların 386 tanesinden kullanılabilir veri elde edilmiştir."</em></p>

<p><strong>Örneklem büyüklüğünü hesaplamak için → <a href="/istatistik/orneklem/">Analizus Örneklem Büyüklüğü Hesaplayıcısını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Cochran, W. G. (1977). Sampling techniques (3rd ed.). Wiley.<br>Krejcie, R. V., &amp; Morgan, D. W. (1970). Determining sample size for research activities. Educational and Psychological Measurement, 30(3), 607–610.</small>"""

    BlogPost.objects.get_or_create(
        slug='tez-icin-kac-anket-doldurulmali-orneklem-buyuklugu-nasil-hesaplanir',
        defaults={'title': 'Tez İçin Kaç Anket Doldurulmalı? Örneklem Büyüklüğü Nasıl Hesaplanır?', 'excerpt': 'Teziniz için gereken minimum örneklem büyüklüğünü nasıl hesaplarsınız? Cochran formülü, analiz türüne göre minimum örneklem tablosu ve APA raporlama rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0107_blog_regresyon_bulgular_bolumu')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
