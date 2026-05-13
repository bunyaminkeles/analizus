from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Ücretsiz SPSS Alternatifi Var mı? Tez İçin En İyi Seçenekler</h2>
<p>SPSS lisansı her öğrenci için erişilebilir değildir. Üniversitenizin lisansı yoksa veya lisans süresi dolduysa paniğe kapılmayın. Tez analizleriniz için kullanabileceğiniz, ücretsiz ve güvenilir birçok alternatif mevcuttur. Bu yazıda en yaygın seçenekleri ve hangisinin hangi analiz için uygun olduğunu bulacaksınız.</p>

<h2>Ücretsiz İstatistik Programları Karşılaştırması</h2>
<table>
  <thead><tr><th>Program</th><th>Güçlü Yönleri</th><th>Zayıf Yönleri</th><th>Kullanım Zorluğu</th></tr></thead>
  <tbody>
    <tr><td><strong>R + RStudio</strong></td><td>Her türlü analiz, yayın kalitesi grafik</td><td>Programlama bilgisi gerektirir</td><td>Orta-Yüksek</td></tr>
    <tr><td><strong>JASP</strong></td><td>SPSS'e benzer menü, Bayesyen analiz</td><td>Bazı ileri analizler yok</td><td>Düşük</td></tr>
    <tr><td><strong>jamovi</strong></td><td>Gerçek zamanlı çıktı, R modülleri</td><td>Veri manipülasyonu sınırlı</td><td>Düşük</td></tr>
    <tr><td><strong>PSPP</strong></td><td>SPSS sözdizimi uyumlu</td><td>Grafikler zayıf, güncel değil</td><td>Düşük-Orta</td></tr>
    <tr><td><strong>Analizus</strong></td><td>Türkçe, tarayıcıda çalışır, teze hazır çıktı</td><td>Temel analizlere odaklı</td><td>Çok Düşük</td></tr>
  </tbody>
</table>

<h2>Hangi Analiz İçin Hangi Program?</h2>
<table>
  <thead><tr><th>Analiz</th><th>Önerilen Ücretsiz Araç</th></tr></thead>
  <tbody>
    <tr><td>t-Testi, ANOVA, Korelasyon</td><td>jamovi, JASP veya Analizus</td></tr>
    <tr><td>Cronbach Alpha, Faktör Analizi</td><td>jamovi veya Analizus</td></tr>
    <tr><td>Çoklu Regresyon</td><td>jamovi, R veya Analizus</td></tr>
    <tr><td>Yapısal Eşitlik Modellemesi (SEM)</td><td>R (lavaan paketi) veya JASP</td></tr>
    <tr><td>Çok Düzeyli Modelleme</td><td>R (lme4 paketi)</td></tr>
    <tr><td>Meta-analiz</td><td>R (meta, metafor paketleri)</td></tr>
  </tbody>
</table>

<h2>Hızlı Başlangıç İçin jamovi</h2>
<p>jamovi, SPSS'i kullananların en hızlı adapte olabileceği ücretsiz programdır. Menü yapısı SPSS'e benzer, her analizin altında R kodu otomatik oluşturulur ve çıktılar APA formatına yakındır. Windows, Mac ve Linux'ta çalışır; ayrıca tarayıcı tabanlı cloud versiyonu mevcuttur.</p>

<p><strong>Hemen analize başlamak için → <a href="/istatistik/ttesti/">Analizus t-Testi aracını tarayıcınızda ücretsiz kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>The jamovi project. (2023). jamovi (Version 2.4) [Computer software]. jamovi.org<br>JASP Team. (2023). JASP (Version 0.18) [Computer software]. jasp-stats.org</small>"""

    BlogPost.objects.get_or_create(
        slug='ucretsiz-spss-alternatifi-var-mi-tez-icin-en-iyi-secenekler',
        defaults={'title': 'Ücretsiz SPSS Alternatifi Var mı? Tez İçin En İyi Seçenekler', 'excerpt': 'SPSS lisansınız yoksa tez analizleriniz için R, JASP, jamovi veya Analizus gibi ücretsiz alternatifleri kullanabilirsiniz. Karşılaştırma tablosu ve analiz türüne göre öneri.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0111_blog_spss_mi_r_mi')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
