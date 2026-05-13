from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>t-Testi Tablosu Teze Nasıl Eklenir?</h2>
<p>t-Testi analizini tamamladınız, SPSS'ten sonuçlar geldi. Şimdi bu sonuçları tezinizin Bulgular bölümüne aktarmanız gerekiyor. Hem metin içinde APA formatında yazmak hem de tabloya düzenlemek, danışmanların özellikle incelediği noktalardır. Bu yazıda adım adım hem tablo formatını hem de metin içi raporlamayı öğreneceksiniz.</p>

<h2>t-Testi Raporunda Yer Alması Gereken Değerler</h2>
<table>
  <thead><tr><th>Değer</th><th>Sembol</th><th>Nerede Bulunur (SPSS)?</th></tr></thead>
  <tbody>
    <tr><td>Ortalama</td><td>M</td><td>Group Statistics tablosu</td></tr>
    <tr><td>Standart Sapma</td><td>SD</td><td>Group Statistics tablosu</td></tr>
    <tr><td>t değeri</td><td>t</td><td>Independent Samples Test tablosu</td></tr>
    <tr><td>Serbestlik Derecesi</td><td>df</td><td>Independent Samples Test tablosu</td></tr>
    <tr><td>p değeri</td><td>p</td><td>Sig. (2-tailed) sütunu</td></tr>
    <tr><td>Cohen's d</td><td>d</td><td>Manuel hesaplanır: (M1-M2)/SD_havuzlu</td></tr>
  </tbody>
</table>

<h2>Teze Eklenecek Tablo Formatı</h2>
<p>Tablo başlığını tablo numarası ile birlikte tablonun üstüne yazın. APA formatında tablo başlıkları italik ve tablonun üstündedir:</p>
<p><em>Tablo 3</em><br><em>Cinsiyete Göre İş Tatmini Puanlarının t-Testi Sonuçları</em></p>
<table>
  <thead><tr><th>Grup</th><th>N</th><th>M</th><th>SD</th><th>t</th><th>df</th><th>p</th><th>d</th></tr></thead>
  <tbody>
    <tr><td>Kadın</td><td>54</td><td>68.4</td><td>9.2</td><td rowspan="2">3.41</td><td rowspan="2">102</td><td rowspan="2">.001</td><td rowspan="2">0.67</td></tr>
    <tr><td>Erkek</td><td>50</td><td>61.2</td><td>10.1</td></tr>
  </tbody>
</table>

<h2>Metin İçi APA Raporlama</h2>
<p>Tablo oluşturduktan sonra metin içinde kısaca sonucu yazın, tablodan tekrar etmeyin:</p>
<p><em>"Tablo 3'te görüldüğü üzere, kadın katılımcıların iş tatmini puanları (M = 68.4, SD = 9.2) erkek katılımcıların puanlarından (M = 61.2, SD = 10.1) istatistiksel olarak anlamlı biçimde yüksek bulunmuştur, t(102) = 3.41, p = .001, d = 0.67. Cohen (1988) sınıflandırmasına göre etki büyüklüğü orta-büyük düzeydedir."</em></p>

<h2>Levene Testi Sonucuna Göre Hangi Satırı Kullanacaksınız?</h2>
<p>SPSS'te t-Testi sonucu iki satır halinde gelir. Levene's Test for Equality of Variances'ın p değeri 0.05'ten büyükse "Equal variances assumed" satırını, 0.05'ten küçükse "Equal variances not assumed" satırını kullanırsınız.</p>

<p><strong>t-Testi analizinizi yapmak için → <a href="/istatistik/ttesti/">Analizus t-Testi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>American Psychological Association. (2020). Publication manual of the APA (7th ed.).<br>Cohen, J. (1988). Statistical power analysis for the behavioral sciences. Erlbaum.</small>"""

    BlogPost.objects.get_or_create(
        slug='t-testi-tablosu-teze-nasil-eklenir',
        defaults={'title': 't-Testi Tablosu Teze Nasıl Eklenir?', 'excerpt': 'SPSS\'ten aldığınız t-Testi sonuçlarını teze nasıl aktarırsınız? APA formatında tablo yapısı, metin içi raporlama, Levene testi yorumu ve Cohen\'s d etki büyüklüğü rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0104_blog_anova_apa_raporlama')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
