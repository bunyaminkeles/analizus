from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>p Değeri 0.05'ten Büyük Çıktı, Tezime Ne Yazarım?</h2>
<p>Analizinizi tamamladınız ve SPSS'ten "Sig. = 0.231" gibi 0.05'in üzerinde bir p değeri çıktı. İlk tepki genellikle şok ve hayal kırıklığı olur: "Hipotezim reddedildi, şimdi ne olacak?" Ancak istatistik dünyasında anlamlı olmayan bir sonuç, başarısız bir tez anlamına gelmez. Aksine, dürüstçe raporlanmış anlamsız bulgular bilime değerli katkı sağlar.</p>

<h2>p Değeri Ne Anlama Gelir?</h2>
<p>p değeri, "eğer H₀ (sıfır hipotezi) doğruysa, bu verileri veya daha aşırısını gözlemleme olasılığını" gösterir. p &gt; 0.05 çıkması; gruplar arasında gerçekten fark olmadığı anlamına gelmez. Yalnızca "bu veri seti ile, bu örneklem büyüklüğünde, istatistiksel olarak yeterli kanıt bulunamadı" demektir. İki şeyin aynı olduğunu kanıtlamaz; sadece farkın kanıtlanabilir olmadığını gösterir.</p>

<h2>p &gt; 0.05 Çıkınca Yapılabilecekler</h2>
<p><strong>1. Örneklem büyüklüğünü sorgulayın:</strong> Küçük N ile büyük efekt boyutu bile anlamsız çıkabilir. Güç analizi (Power Analysis) yaparak örnekleminizin yeterli olup olmadığını kontrol edin.</p>
<p><strong>2. Etki büyüklüğünü (Effect Size) raporlayın:</strong> Cohen's d, η², veya r gibi etki büyüklüğü ölçüleri, pratik önemi gösterir. Küçük örneklemde p &gt; 0.05 çıksa bile büyük etki boyutu olabilir.</p>
<p><strong>3. Sıfır hipotezini tartışın:</strong> "Anlamlı fark bulunamadı" bulgusu da bir bulgudur. Literatürde fark bekleniyordu ama siz bulmadınız — bu neden olabilir? Tartışma bölümünde bunu ele alın.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p>Anlamsız sonuçları "başarısız" gibi sunmak yerine objektif ve akademik bir dille raporlayın:</p>
<p><em>"Deney ve kontrol grupları arasında akademik başarı puanları açısından istatistiksel olarak anlamlı bir fark bulunamamıştır, t(58) = 1.24, p = .220, d = 0.32. Bu bulgu, uygulanan programın bu örneklemde ölçülebilir bir etki yaratmadığını göstermektedir. Etki büyüklüğünün küçük-orta düzeyde (d = 0.32) olması, daha büyük örneklemlerle yürütülecek çalışmalarda anlamlı sonuçlara ulaşılabileceğine işaret etmektedir."</em></p>

<h2>Hangi Analizler Anlamsız Sonuç Verse de Tezde Kullanılabilir?</h2>
<table>
  <thead><tr><th>Analiz</th><th>p &gt; 0.05 Durumunda</th></tr></thead>
  <tbody>
    <tr><td>t-Testi</td><td>Gruplar arası fark kanıtlanamadı — etki boyutunu raporla</td></tr>
    <tr><td>ANOVA</td><td>Grupların ortalamaları arasında anlamlı fark yok — post-hoc yapmana gerek yok</td></tr>
    <tr><td>Korelasyon</td><td>İki değişken arasında doğrusal ilişki kanıtlanamadı</td></tr>
    <tr><td>Regresyon</td><td>Model anlamsız — bağımsız değişkenler bağımlıyı yordamıyor</td></tr>
  </tbody>
</table>

<p><strong>Analizlerinizi yapmak için → <a href="/istatistik/ttesti/">t-Testi</a>, <a href="/istatistik/anova/">ANOVA</a> ve <a href="/istatistik/korelasyon/">Korelasyon</a> araçlarımızı kullanın.</strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.). Erlbaum.<br>Cumming, G. (2014). The new statistics: Why and how. Psychological Science, 25(1), 7–29.</small>"""

    BlogPost.objects.get_or_create(
        slug='p-degeri-0-05-ten-buyuk-cikti-tezime-ne-yazarim',
        defaults={'title': 'p Değeri 0.05\'ten Büyük Çıktı, Tezime Ne Yazarım?', 'excerpt': 'İstatistiksel analiz sonucunda p > 0.05 çıktığında tez başarısız mı oldu? Anlamsız bulguların nasıl yorumlanacağını, etki boyutunu ve APA raporlama örneklerini öğrenin.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0098_blog_ki_kare_mi_lojistik_regresyon_mu')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
