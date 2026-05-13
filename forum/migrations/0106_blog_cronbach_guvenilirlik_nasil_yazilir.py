from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Cronbach Alpha Güvenilirlik Bulguları Nasıl Yazılır?</h2>
<p>Anket çalışmalarında kullandığınız ölçeğin güvenilirliğini Cronbach Alpha ile hesapladınız. Elde ettiğiniz değerleri tezinizin Yöntem veya Bulgular bölümüne nasıl aktaracaksınız? Güvenilirlik analizinin raporlanması, hem ölçek geçerliğini hem de sonuçlara olan güveni doğrudan etkiler.</p>

<h2>Cronbach Alpha Raporunda Yer Alması Gerekenler</h2>
<table>
  <thead><tr><th>Bilgi</th><th>Nerede Raporlanır</th><th>Örnek</th></tr></thead>
  <tbody>
    <tr><td>Cronbach Alpha değeri</td><td>Yöntem veya Bulgular</td><td>α = .82</td></tr>
    <tr><td>Madde sayısı</td><td>Yöntem</td><td>12 maddeden oluşan ölçek</td></tr>
    <tr><td>Madde silme işlemi</td><td>Bulgular (eğer yapıldıysa)</td><td>4. madde çıkarıldı, α .68'den .79'a yükseldi</td></tr>
    <tr><td>Alt boyut güvenilirlikleri</td><td>Tablo veya metin</td><td>Her boyut için ayrı α değeri</td></tr>
  </tbody>
</table>

<h2>Güvenilirlik Tablo Formatı (Çok Boyutlu Ölçek)</h2>
<p>Birden fazla alt boyutu olan bir ölçekte her boyut için ayrı Cronbach Alpha değeri raporlanmalıdır:</p>
<table>
  <thead><tr><th>Alt Boyut</th><th>Madde Sayısı</th><th>Cronbach Alpha (α)</th></tr></thead>
  <tbody>
    <tr><td>Duygusal Bağlılık</td><td>5</td><td>.84</td></tr>
    <tr><td>Devam Bağlılığı</td><td>4</td><td>.76</td></tr>
    <tr><td>Normatif Bağlılık</td><td>4</td><td>.71</td></tr>
    <tr><td><strong>Toplam Ölçek</strong></td><td><strong>13</strong></td><td><strong>.88</strong></td></tr>
  </tbody>
</table>

<h2>Yöntem Bölümünde APA Raporlama</h2>
<p><em>"Araştırmada Meyer ve Allen (1991) tarafından geliştirilen ve Wasti (2000) tarafından Türkçe'ye uyarlanan Örgütsel Bağlılık Ölçeği kullanılmıştır. Ölçek; Duygusal Bağlılık (5 madde), Devam Bağlılığı (4 madde) ve Normatif Bağlılık (4 madde) olmak üzere üç alt boyuttan oluşmaktadır. Mevcut çalışmada ölçeğin iç tutarlılık güvenirlik katsayıları; Duygusal Bağlılık için α = .84, Devam Bağlılığı için α = .76, Normatif Bağlılık için α = .71 ve toplam ölçek için α = .88 olarak hesaplanmıştır."</em></p>

<h2>Güvenilirlik Değerlerinin Yorumlanması</h2>
<p>α ≥ .90 mükemmel, α ≥ .80 iyi, α ≥ .70 kabul edilebilir, α ≥ .60 (keşfedici araştırmalarda) sınırlı kabul edilebilir, α &lt; .60 yetersiz olarak değerlendirilir (George &amp; Mallery, 2003).</p>

<p><strong>Cronbach Alpha değerlerinizi hesaplamak için → <a href="/istatistik/cronbach/">Analizus Güvenilirlik Analizi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>George, D., &amp; Mallery, P. (2003). SPSS for Windows step by step (4th ed.). Allyn &amp; Bacon.<br>American Psychological Association. (2020). Publication manual of the APA (7th ed.).</small>"""

    BlogPost.objects.get_or_create(
        slug='cronbach-alpha-guvenilirlik-bulgulari-nasil-yazilir',
        defaults={'title': 'Cronbach Alpha Güvenilirlik Bulguları Nasıl Yazılır?', 'excerpt': 'Cronbach Alpha güvenilirlik analizi sonuçlarını tezin Yöntem ve Bulgular bölümlerine nasıl aktarırsınız? Alt boyut tablosu, APA formatı ve raporlama örnekleri.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0105_blog_t_testi_tablosu')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
