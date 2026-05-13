from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>ANOVA mı Mann-Whitney mi? Hangisini Seçmeliyim?</h2>
<p>Gruplar arasındaki farkı incelerken bir araştırmacının aklına genellikle en popüler iki test olan ANOVA ve Mann-Whitney U testleri gelir. Ancak bu iki test aslında <strong>aynı amaca hizmet etmez</strong> ve birbirinin doğrudan alternatifi değildir. Değişkenlerinizin yapısı ve grup sayınız, bu iki testten hangisini seçeceğinizi kesin çizgilerle belirler.</p>

<h2>Kısa Tanım: Testlerin Temel Özellikleri</h2>
<p><strong>ANOVA (Varyans Analizi):</strong> Üç veya daha fazla bağımsız grubun ortalamaları arasında anlamlı fark olup olmadığını test eden <em>parametrik</em> bir yöntemdir. Normal dağılım gerektirir.</p>
<p><strong>Mann-Whitney U Testi:</strong> Sadece iki bağımsız grubun sıralamalarını karşılaştıran <em>non-parametrik</em> bir testtir. Veriler normal dağılmadığında bağımsız örneklem t-testinin yedeği olarak kullanılır.</p>

<h2>Seçimi Belirleyen 2 Altın Kural</h2>
<ol>
  <li><strong>Bağımsız Değişkeninizde Kaç Grup Var?</strong> Grup sayısı tam olarak 2 ise ANOVA kullanamazsınız. Grup sayısı 3 veya daha fazla ise Mann-Whitney U testi kullanamazsınız.</li>
  <li><strong>Veriler Normal Dağılıyor mu?</strong> 3+ grup varsa ve normal dağılıyorsa → ANOVA. 3+ grup varsa ve normal dağılmıyorsa → <a href="/istatistik/kruskal-wallis/">Kruskal-Wallis H Testi</a> (Mann-Whitney U değil!).</li>
</ol>

<h2>Örnek Senaryo ile Karşılaştırma</h2>
<table>
  <thead><tr><th>Araştırma Sorusu</th><th>Grup</th><th>Normallik</th><th>Doğru Test</th></tr></thead>
  <tbody>
    <tr><td>Kadın ve erkeklerin (2 grup) gelir düzeyleri arasında fark var mıdır?</td><td>2</td><td>Sağlanmamış</td><td><strong>Mann-Whitney U</strong></td></tr>
    <tr><td>İlkokul, lise ve üniversite mezunlarının (3 grup) yaşam tatminleri arasında fark var mıdır?</td><td>3</td><td>Sağlanmış</td><td><strong>Tek Yönlü ANOVA</strong></td></tr>
    <tr><td>İlkokul, lise ve üniversite mezunlarının (3 grup) yaşam tatminleri arasında fark var mıdır?</td><td>3</td><td>Sağlanmamış</td><td><strong>Kruskal-Wallis H</strong></td></tr>
  </tbody>
</table>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Eğitim durumu değişkeninin 3 alt gruptan oluşması ve bağımlı değişken olan tükenmişlik puanlarının normal dağılım varsayımını (Shapiro-Wilk p &gt; .05) karşılaması nedeniyle gruplar arası farklılıkların incelenmesinde Tek Yönlü Varyans Analizi (ANOVA) kullanılmıştır."</em></p>

<p><strong>Grup karşılaştırmalarınızı saniyeler içinde yapmak için → <a href="/istatistik/anova/">Analizus ANOVA aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Tabachnick, B. G., &amp; Fidell, L. S. (2013). Using multivariate statistics (6th ed.). Pearson.<br>Pallant, J. (2020). SPSS survival manual. Routledge.</small>"""

    BlogPost.objects.get_or_create(
        slug='anova-mi-mann-whitney-mi-hangisini-secmeliyim',
        defaults={'title': 'ANOVA mı Mann-Whitney mi? Hangisini Seçmeliyim?', 'excerpt': 'ANOVA parametrik 3+ gruplar için, Mann-Whitney U ise non-parametrik 2 grup içindir. Veri setinize ve grup sayınıza göre doğru istatistiksel testi seçme rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0096_blog_bagimsiz_mi_bagimli_mi_t_testi')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
