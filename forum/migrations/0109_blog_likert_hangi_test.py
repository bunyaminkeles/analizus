from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Likert Ölçeğine Hangi İstatistik Testi Uygulanır?</h2>
<p>Anketinizde "1-Kesinlikle Katılmıyorum … 5-Kesinlikle Katılıyorum" şeklinde bir Likert ölçeği kullandınız. Şimdi hangi testi uygulayacaksınız? Bu soru onlarca yıldır metodoloji tartışmalarının merkezinde yer almaktadır. Doğru cevap, ölçeğin nasıl ele alındığına bağlıdır; bu yazıda iki yaklaşımı ve pratik karar rehberini bulacaksınız.</p>

<h2>İki Temel Yaklaşım</h2>
<p><strong>Yaklaşım 1 — Ordinal (sıralı) veriymiş gibi davranmak:</strong> Her madde ayrı ayrı analiz edilir, parametrik olmayan testler tercih edilir. Tek maddelik sorularda önerilir.</p>
<p><strong>Yaklaşım 2 — Sürekli (interval) veriymiş gibi davranmak:</strong> Birden fazla madde toplanarak alt boyut skoru elde edilir ve parametrik testler kullanılır. Güvenilirliği (α ≥ .70) kanıtlanmış çok maddelik ölçeklerde yaygın kabul görür.</p>

<h2>Karar Tablosu</h2>
<table>
  <thead><tr><th>Durum</th><th>Önerilen Test</th><th>Gerekçe</th></tr></thead>
  <tbody>
    <tr><td>Tek madde, 2 grup karşılaştırma</td><td>Mann-Whitney U</td><td>Ordinal + küçük örneklem</td></tr>
    <tr><td>Tek madde, 3+ grup karşılaştırma</td><td>Kruskal-Wallis</td><td>Ordinal + çok grup</td></tr>
    <tr><td>Çok madde (ölçek), 2 grup, normal dağılım var</td><td>Bağımsız t-Testi</td><td>Interval + parametrik</td></tr>
    <tr><td>Çok madde (ölçek), 3+ grup, normal dağılım var</td><td>ANOVA</td><td>Interval + parametrik</td></tr>
    <tr><td>Çok madde (ölçek), normal dağılım yok</td><td>Mann-Whitney U / Kruskal-Wallis</td><td>Normallik sağlanmıyor</td></tr>
    <tr><td>İki ölçek arasındaki ilişki</td><td>Pearson / Spearman Korelasyon</td><td>Ölçek türüne göre seçin</td></tr>
  </tbody>
</table>

<h2>Normallik Kontrolü Zorunlu mu?</h2>
<p>Ölçek toplam puanı için normallik kontrolü yapılmalıdır. Shapiro-Wilk (N &lt; 50) veya Kolmogorov-Smirnov (N ≥ 50) testleri kullanılabilir. p &gt; 0.05 ise parametrik teste geçebilirsiniz; p ≤ 0.05 ise veya histogram çarpık görünüyorsa parametrik olmayan testi tercih edin.</p>

<h2>Tezde Nasıl Yazılır?</h2>
<p><em>"Veriler Likert tipi (1–5) ölçekle toplanmış olup her alt boyut için madde ortalamaları hesaplanmıştır. Shapiro-Wilk normallik testi sonucunda alt boyut puanlarının normal dağılım gösterdiği belirlenmiş (p &gt; .05) ve gruplar arası karşılaştırmalarda bağımsız örneklem t-testi uygulanmıştır."</em></p>

<p><strong>Normallik testinizi yapmak için → <a href="/istatistik/normallik/">Analizus Normallik Testi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Norman, G. (2010). Likert scales, levels of measurement and the "laws" of statistics. Advances in Health Sciences Education, 15(5), 625–632.<br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.</small>"""

    BlogPost.objects.get_or_create(
        slug='likert-olcegine-hangi-istatistik-testi-uygulanir',
        defaults={'title': 'Likert Ölçeğine Hangi İstatistik Testi Uygulanır?', 'excerpt': 'Likert ölçeğiyle toplanan veriye t-testi mi, Mann-Whitney mi uygulamalısınız? Tek madde ve çok maddelik ölçekler için karar tablosu ve tezde raporlama rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0108_blog_orneklem_buyuklugu')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
