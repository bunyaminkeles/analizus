from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>SPSS mi R mi? Tez İçin Hangisi Daha Kolay?</h2>
<p>Tez analizlerine başlamadan önce çoğu öğrencinin aklına ilk gelen soru şudur: "SPSS mi kullansam, R mi?" Her ikisi de güçlü araçlardır; ancak hangi programın size uygun olduğu, analizlerinizin karmaşıklığına, programlama deneyiminize ve tez danışmanınızın beklentisine göre değişir. Bu yazıda her iki programı aynı ölçütlerle karşılaştırdık.</p>

<h2>SPSS vs R Karşılaştırma Tablosu</h2>
<table>
  <thead><tr><th>Ölçüt</th><th>SPSS</th><th>R</th></tr></thead>
  <tbody>
    <tr><td>Öğrenme eğrisi</td><td>Düşük — menü tabanlı</td><td>Yüksek — kod yazılması gerekir</td></tr>
    <tr><td>Maliyet</td><td>Ücretli (~300$/yıl) veya üniversite lisansı</td><td>Ücretsiz ve açık kaynak</td></tr>
    <tr><td>Çıktı formatı</td><td>Otomatik tablo ve görsel</td><td>Özelleştirilebilir, yayın kalitesi</td></tr>
    <tr><td>Temel istatistikler (t-testi, ANOVA, regresyon)</td><td>Çok kolay</td><td>Kolay (birkaç satır kod)</td></tr>
    <tr><td>İleri analizler (SEM, çok düzeyli model)</td><td>Sınırlı</td><td>Kapsamlı paket desteği</td></tr>
    <tr><td>Tekrar üretilebilirlik</td><td>Zayıf (tıklama kayıt edilmez)</td><td>Güçlü (kod = tam kayıt)</td></tr>
    <tr><td>Sosyal bilimler tezlerinde yaygınlık</td><td>Çok yaygın</td><td>Giderek artan</td></tr>
  </tbody>
</table>

<h2>Hangi Durumda Hangisi?</h2>
<p><strong>SPSS'i seçin eğer:</strong> İstatistik derslerinde SPSS ile çalıştıysanız, teziniz yüksek lisans düzeyinde temel analizler içeriyorsa (t-testi, ANOVA, regresyon, faktör analizi), danışmanınız SPSS çıktısına alışkınsa.</p>
<p><strong>R'ı seçin eğer:</strong> Doktora veya yayın odaklı çalışıyorsanız, SEM, çok düzeyli modelleme veya meta-analiz yapacaksanız, tekrar üretilebilir araştırma ilkeleri sizin için önemliyse ya da programlamaya ilginiz varsa.</p>

<h2>Üçüncü Seçenek: Analizus</h2>
<p>Temel istatistik analizlerinizi kurulum gerektirmeden, Türkçe arayüzle ve teze hazır çıktılarla yapmak istiyorsanız Analizus'u deneyebilirsiniz. t-Testi, ANOVA, korelasyon, regresyon, Cronbach Alpha ve normallik testleri desteklenmektedir.</p>

<p><strong>Kurulum gerektirmeden analiz yapmak için → <a href="/istatistik/normallik/">Analizus İstatistik Araçlarını ücretsiz kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>Wickham, H., &amp; Grolemund, G. (2017). R for data science. O'Reilly. Ücretsiz erişim: r4ds.had.co.nz</small>"""

    BlogPost.objects.get_or_create(
        slug='spss-mi-r-mi-tez-icin-hangisi-daha-kolay',
        defaults={'title': 'SPSS mi R mi? Tez İçin Hangisi Daha Kolay?', 'excerpt': 'Tez analizleriniz için SPSS mi yoksa R mı kullanmalısınız? Öğrenme eğrisi, maliyet, çıktı kalitesi ve sosyal bilimler tezlerinde yaygınlık açısından karşılaştırma.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0110_blog_eksik_veri_missing_data')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
