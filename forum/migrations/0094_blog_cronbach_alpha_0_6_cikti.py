from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Cronbach Alpha 0.6 Çıktı, Ne Yapmalıyım?</h2>
<p>SPSS'te güvenilirlik analizi sonuçlarınızı beklerken ekranda 0.60 (veya 0.60-0.69 arası) bir Cronbach Alpha değeri görmek, birçok tez öğrencisinde anında paniğe neden olur. Tez sürecinde anket topladınız, analiz aşamasına geçtiniz ve literatürde sürekli tekrarlanan "0.70" eşiğinin altında kaldınız. Peki, bu durumda ölçek iptal mi olmalı? Tüm veriler çöpe mi gidecek? Hayır. Doğru gerekçeler ve düzeltme adımları ile 0.60 değeri de akademik dünyada kabul edilebilir bir sınır olabilir.</p>

<h2>Kısa Tanım: Cronbach Alpha Nedir?</h2>
<p>Cronbach Alpha, bir anket veya ölçekteki soruların (maddelerin) birbiriyle ne kadar uyumlu olduğunu, yani iç tutarlılığını ölçen istatistiksel bir katsayıdır. Bir konsepti (örneğin kaygı düzeyini) ölçmek için tasarladığınız 10 sorunun hepsi gerçekten aynı yapıyı mı ölçüyor, yoksa bazı sorular katılımcıların aklını mı karıştırıyor? Alfa değeri 0 ile 1 arasında değişir; 1'e ne kadar yakınsa sorular o kadar birbiriyle uyumlu ve güvenilirdir.</p>

<h2>Nasıl Yorumlanır ve 0.60 Ne Zaman Kabul Edilir?</h2>
<p>Genel kabul, sosyal bilimlerde Cronbach Alpha katsayısının <strong>0.70 ve üzeri</strong> olması gerektiği yönündedir. Ancak 0.60 değeri her zaman "başarısızlık" anlamına gelmez. Hair ve arkadaşlarının (2010) metodolojik referanslarına göre; eğer araştırmanız daha önce test edilmemiş yepyeni bir kavramı ölçüyorsa (keşfedici - exploratory araştırma), <strong>0.60 değeri de kabul edilebilir alt sınır</strong> olarak raporlanabilir.</p>
<p>Ancak bu değere ulaştığınızda körü körüne kabul etmemelisiniz. Çözüm olarak şu iki adımı uygulayabilirsiniz: 1) Ölçekte "Ters kodlanmış" (Reverse scored) bir soru varsa ve bunu SPSS'te düzeltmeyi unuttuysanız, alfa değeriniz yapay olarak düşük çıkar. 2) İlgisiz veya kafa karıştırıcı bir soruyu ölçekten çıkartarak (Item deleted) alfa değerinizi yükseltebilirsiniz.</p>

<h2>Örnek Senaryo ve Tablo Yorumlama</h2>
<p>Bir "Müşteri Memnuniyeti" anketi hazırladınız. İlk analizde Cronbach Alpha değeri 0.62 çıktı. Aşağıdaki SPSS "Item-Total Statistics" tablosunu incelediğinizde, "Soru_4" numaralı değişkenin problemli olduğunu görebilirsiniz.</p>
<table>
  <thead><tr><th>Madde (Soru)</th><th>Düzeltilmiş Madde-Toplam Korelasyonu</th><th>Madde Silindiğinde Cronbach Alpha</th></tr></thead>
  <tbody>
    <tr><td>Soru 1</td><td>0.45</td><td>0.58</td></tr>
    <tr><td>Soru 2</td><td>0.52</td><td>0.55</td></tr>
    <tr><td>Soru 3</td><td>0.48</td><td>0.57</td></tr>
    <tr><td><strong>Soru 4</strong></td><td><strong>0.12</strong></td><td><strong>0.75</strong></td></tr>
  </tbody>
</table>
<p>Tabloda görüldüğü üzere, Soru 4'ün genel skorla korelasyonu çok düşük (0.12). Eğer bu soruyu analizden çıkartırsanız, Cronbach Alpha değeriniz anında 0.75'e yükselecektir.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Araştırmada kullanılan Müşteri Memnuniyeti Ölçeği'nin iç tutarlılık güvenirliği Cronbach Alpha katsayısı ile hesaplanmıştır. Yapılan ilk analizde güvenilirlik katsayısı α = .62 olarak bulunmuştur. Madde-toplam korelasyonu düşük olan (r = .12) 4. madde ölçekten çıkarıldıktan sonra, kalan 3 madde için Cronbach Alpha iç tutarlılık katsayısı α = .75 olarak hesaplanmış ve ölçeğin yeterli güvenilirlik düzeyine ulaştığı kabul edilmiştir (Hair vd., 2010)."</em></p>

<p><strong>Hesaplamak ve verilerinizi doğrulamak için → <a href="/istatistik/cronbach/">Analizus Güvenilirlik Analizi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Hair, J. F., Black, W. C., Babin, B. J., &amp; Anderson, R. E. (2010). Multivariate Data Analysis (7th ed.). Pearson.<br>DeVellis, R. F. (2012). Scale development: Theory and applications (3rd ed.). Sage Publications.</small>"""

    BlogPost.objects.get_or_create(
        slug='cronbach-alpha-0-6-cikti-ne-yapmaliyim',
        defaults={'title': 'Cronbach Alpha 0.6 Çıktı, Ne Yapmalıyım?', 'excerpt': 'SPSS güvenilirlik analizi sonuçlarında Cronbach Alpha değeri 0.60 çıktığında ölçek iptal mi edilmeli? Madde silme adımları ve APA raporlama örnekleriyle çözüm rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0093_fix_levels_icons_empty_category')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
