from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Normallik Testi Sağlanmazsa Hangi Test Kullanılır?</h2>
<p>Bağımsız örneklem t-testi veya ANOVA yapmadan önce SPSS'te Shapiro-Wilk veya Kolmogorov-Smirnov testlerini çalıştırdınız. Ekranda "Sig. (p)" sütununun altında 0.05'ten küçük bir değer (örneğin p=0.01) gördünüz. Bu, verilerinizin normal dağılıma uymadığı anlamına gelir. Panik yapmanıza gerek yok; parametrik testlerin her zaman "kurtarıcı" bir karşılığı olan non-parametrik (parametrik olmayan) testler mevcuttur.</p>

<h2>Kısa Tanım: Parametrik Olmayan Testler Nedir?</h2>
<p>Parametrik olmayan (Non-parametric) testler, verinin çan eğrisi şeklinde (normal) dağılmasını gerektirmeyen, ortalamalar yerine verilerin sıralama (rank) değerlerini kullanan daha esnek istatistiksel analiz yöntemleridir. Aykırı değerlerin fazla olduğu, örneklem büyüklüğünün çok küçük olduğu (genellikle N &lt; 30) veya anketlerin ordinal (sıralı) ölçekle elde edildiği durumlarda veri setinin kurtarıcısı olurlar.</p>

<h2>Nasıl Karar Verilir ve Ne Zaman Kullanılır?</h2>
<p>Normallik testi sağlanmadığında hemen non-parametrik testlere kaçmak her zaman ilk çözüm olmamalıdır. Eğer örnekleminiz yeterince büyükse (N &gt; 30 veya N &gt; 50), Merkezi Limit Teoremi'ne göre çarpıklık (skewness) ve basıklık (kurtosis) değerlerine bakılmalıdır. Eğer bu değerler -1.5 ile +1.5 arasındaysa normallik testi p &lt; 0.05 çıksa bile parametrik teste devam edebilirsiniz.</p>
<p>Ancak, hem normallik p değeri 0.05'ten küçük, hem çarpıklık-basıklık değerleri sınırların dışında, hem de örnekleminiz küçükse kesinlikle non-parametrik alternatiflere geçiş yapmalısınız.</p>

<h2>Parametrik ve Non-Parametrik Test Dönüşüm Tablosu</h2>
<table>
  <thead><tr><th>Parametrik Test</th><th>Karşılaştırma Türü</th><th>Non-Parametrik Alternatif</th></tr></thead>
  <tbody>
    <tr><td>Bağımsız Örneklem T-Testi</td><td>İki bağımsız grup</td><td><strong>Mann-Whitney U Testi</strong></td></tr>
    <tr><td>Bağımlı Örneklem T-Testi</td><td>Aynı grubun iki ölçümü</td><td><strong>Wilcoxon İşaretli Sıralar Testi</strong></td></tr>
    <tr><td>Tek Yönlü ANOVA</td><td>3+ bağımsız grup</td><td><strong>Kruskal-Wallis H Testi</strong></td></tr>
    <tr><td>Pearson Korelasyonu</td><td>İki sürekli değişken</td><td><strong>Spearman's Rho</strong></td></tr>
  </tbody>
</table>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Araştırmada veri setinin normal dağılıma sahip olup olmadığı Shapiro-Wilk testi ile incelenmiştir. Yapılan analiz sonucunda verilerin normal dağılım göstermediği tespit edilmiştir (p &lt; .05). Ek olarak çarpıklık ve basıklık değerlerinin de -1.5 ve +1.5 sınırları dışında olduğu görülmüştür. Bu nedenle, iki bağımsız grup arasındaki farkın incelenmesinde parametrik olmayan Mann-Whitney U testi tercih edilmiştir."</em></p>

<p><strong>Değişkenlerinizin normal dağılıp dağılmadığını hesaplamak için → <a href="/istatistik/normallik/">Analizus Normallik Testi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>Pallant, J. (2020). SPSS survival manual. Routledge.</small>"""

    BlogPost.objects.get_or_create(
        slug='normallik-testi-saglanmazsa-hangi-test-kullanilir',
        defaults={'title': 'Normallik Testi Sağlanmazsa Hangi Test Kullanılır?', 'excerpt': 'Shapiro-Wilk normallik testi p değeri 0.05\'ten küçük çıktığında parametrik testler yerine hangi non-parametrik testlere geçmeniz gerektiğini öğrenin.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0094_blog_cronbach_alpha_0_6_cikti')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
