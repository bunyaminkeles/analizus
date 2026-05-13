from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Korelasyon Yüksek Ama Anlamsız — Bu Nasıl Olur?</h2>
<p>Korelasyon matrisini incelediyseniz ve r = 0.45 gibi görece yüksek bir korelasyon katsayısının yanında p = 0.182 gibi anlamsız bir p değeri gördüyseniz, bu sizi şaşırtmış olabilir. "İlişki bu kadar güçlüyse neden anlamlı değil?" sorusu, istatistik dünyasının en sık sorulan sorularından biridir ve cevabı örneklem büyüklüğüdür.</p>

<h2>İstatistiksel Anlamlılık ile Pratik Anlamlılık Farkı</h2>
<p>İki kavramı birbirinden kesinlikle ayırt etmeniz gerekir:</p>
<p><strong>İstatistiksel Anlamlılık (p &lt; 0.05):</strong> Gözlemlenen ilişkinin şansa bağlı olmadığını, örneklemdeki bulgunun genel popülasyona genellenebileceğini gösterir. Küçük örneklemde büyük korelasyon bile anlamsız çıkabilir.</p>
<p><strong>Pratik Anlamlılık (Etki Boyutu):</strong> İlişkinin gerçek dünyada ne kadar önemli olduğunu gösterir. Büyük örneklemde r = 0.05 bile istatistiksel olarak anlamlı çıkabilir — ama pratikte hiçbir önemi yoktur.</p>

<h2>Örneklem Büyüklüğü Korelasyon Anlamlılığını Nasıl Etkiler?</h2>
<table>
  <thead><tr><th>r (Korelasyon)</th><th>N = 20 için p</th><th>N = 100 için p</th><th>N = 500 için p</th></tr></thead>
  <tbody>
    <tr><td>0.10</td><td>p = .674 (anlamsız)</td><td>p = .318 (anlamsız)</td><td>p = .024 (anlamlı!)</td></tr>
    <tr><td>0.30</td><td>p = .196 (anlamsız)</td><td>p = .002 (anlamlı)</td><td>p &lt; .001 (anlamlı)</td></tr>
    <tr><td>0.50</td><td>p = .025 (anlamlı)</td><td>p &lt; .001 (anlamlı)</td><td>p &lt; .001 (anlamlı)</td></tr>
  </tbody>
</table>
<p>Tabloda açıkça görüldüğü üzere, aynı korelasyon katsayısı farklı örneklem büyüklüklerinde tamamen farklı anlamlılık sonuçları verir.</p>

<h2>Cohen'in Korelasyon Etki Büyüklüğü Sınıflandırması</h2>
<p>Korelasyon katsayısını yorumlarken mutlaka etki büyüklüğü sınıflandırmasını kullanın: r = 0.10 küçük etki, r = 0.30 orta etki, r = 0.50 büyük etki olarak kabul edilir (Cohen, 1988). Anlamsız ama büyük etki boyutlu bir korelasyon, daha büyük örneklemde anlamlı çıkacağını gösterir.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Çalışma motivasyonu ile iş performansı arasındaki ilişkiyi incelemek amacıyla Pearson korelasyon analizi uygulanmıştır. Analiz sonucunda iki değişken arasında pozitif yönde orta düzeyde bir ilişki gözlemlenmiş (r = .38), ancak mevcut örneklem büyüklüğü göz önüne alındığında (N = 25) bu ilişki istatistiksel anlamlılık sınırına ulaşamamıştır, p = .062. Etki büyüklüğünün orta düzeyde olduğu (r = .38; Cohen, 1988) ve daha büyük örneklemlerle yürütülecek çalışmalarda anlamlı sonuçlara ulaşılabileceği değerlendirilmektedir."</em></p>

<p><strong>Korelasyon matrisinizi hesaplamak için → <a href="/istatistik/korelasyon/">Analizus Korelasyon Analizi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.). Erlbaum.<br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.</small>"""

    BlogPost.objects.get_or_create(
        slug='korelasyon-yuksek-ama-anlamsiz-bu-nasil-olur',
        defaults={'title': 'Korelasyon Yüksek Ama Anlamsız — Bu Nasıl Olur?', 'excerpt': 'Korelasyon katsayısı yüksek çıkmasına rağmen p değeri 0.05\'ten büyük olabilir mi? İstatistiksel anlamlılık ile pratik anlamlılık farkı ve örneklem büyüklüğünün etkisi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0102_blog_shapiro_wilk_sinir_deger')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
