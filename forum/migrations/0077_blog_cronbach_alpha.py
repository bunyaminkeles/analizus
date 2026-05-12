# forum/migrations/0079_blog_cronbach_alpha_degeri.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='istatistik-101',
        defaults={'name': 'İstatistik 101', 'icon': 'bi-bar-chart', 'color': '#00d2ff'},
    )

    content = """<h2>Cronbach Alpha (α) Nedir?</h2>
<p>Tez hazırlarken veya bir Likert ölçeği geliştirirken araştırmacıların en sık karşılaştığı kavramlardan biri <strong>Cronbach Alpha (α)</strong> katsayısıdır. Bu istatistiksel metrik, bir ölçme aracının <strong>iç tutarlılığını</strong> ve güvenilirliğini değerlendirmek için kullanılır. Basitçe ifade etmek gerekirse, anketinizdeki soruların aynı yapıyı veya kavramı ne kadar tutarlı bir şekilde ölçtüğünü gösterir.</p>

<h2>Cronbach Alpha Değeri Kaç Olmalı?</h2>
<p>Akademik literatürde Cronbach Alpha değerinin yorumlanması için genel kabul görmüş belirli eşik değerleri bulunmaktadır. Bu değerler genellikle 0 ile 1 arasında değişir.</p>

<table>
  <thead>
    <tr>
      <th>Cronbach Alpha (α) Değeri</th>
      <th>İç Tutarlılık Düzeyi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0.90 ≤ α</td>
      <td>Mükemmel</td>
    </tr>
    <tr>
      <td>0.80 ≤ α &lt; 0.90</td>
      <td>İyi</td>
    </tr>
    <tr>
      <td>0.70 ≤ α &lt; 0.80</td>
      <td>Kabul Edilebilir</td>
    </tr>
    <tr>
      <td>0.60 ≤ α &lt; 0.70</td>
      <td>Şüpheli (Keşfedici araştırmalarda kullanılabilir)</td>
    </tr>
    <tr>
      <td>0.50 ≤ α &lt; 0.60</td>
      <td>Zayıf</td>
    </tr>
    <tr>
      <td>α &lt; 0.50</td>
      <td>Kabul Edilemez</td>
    </tr>
  </tbody>
</table>

<p>Sosyal bilimlerde genellikle <strong>0.70</strong> ve üzeri değerler "kabul edilebilir" olarak değerlendirilir. Ancak, yeni bir ölçek geliştirilen keşfedici (exploratory) araştırmalarda bu sınır 0.60'a kadar esnetilebilir.</p>

<h2>SPSS Kullanarak Cronbach Alpha Nasıl Hesaplanır?</h2>
<p>Ölçek değerlendirme sürecinde SPSS programı üzerinden Cronbach Alpha değerini hesaplamak oldukça basittir. Adım adım şu şekilde ilerleyebilirsiniz:</p>
<ol>
  <li>Üst menüden <code>Analyze</code> sekmesine tıklayın.</li>
  <li>Açılan menüden <code>Scale</code> seçeneğine gelin.</li>
  <li>Ardından <code>Reliability Analysis...</code> seçeneğine tıklayın.</li>
  <li>Güvenilirlik analizine dahil etmek istediğiniz maddeleri sol taraftaki kutudan sağ taraftaki <code>Items</code> kutusuna aktarın.</li>
  <li><code>Model</code> açılır menüsünün <strong>Alpha</strong> olarak seçili olduğundan emin olun.</li>
  <li>Detaylı sonuçlar için <code>Statistics</code> butonuna tıklayıp <code>Scale if item deleted</code> seçeneğini işaretleyin.</li>
  <li><code>Continue</code> ve ardından <code>OK</code> butonlarına basarak analizi tamamlayın.</li>
</ol>

<h2>Sonuçların APA Formatında Raporlanması</h2>
<p>Elde ettiğiniz bulguları tezinizde veya makalenizde Amerikan Psikoloji Derneği (APA) standartlarına uygun şekilde raporlamalısınız. Raporlama yaparken okuyucuya ölçeğin kaç maddeden oluştuğunu belirtmeniz faydalı olacaktır.</p>

<h3>Örnek APA Raporlama Şablonu</h3>
<p><em>"Araştırmada kullanılan 'Akademik Motivasyon Ölçeği'nin iç tutarlılık güvenilirliği Cronbach Alpha katsayısı ile incelenmiştir. 15 maddeden oluşan ölçeğin Cronbach Alpha iç tutarlılık katsayısı α = .86 olarak hesaplanmıştır. Bu sonuç, ölçeğin yüksek düzeyde güvenilirliğe sahip olduğunu göstermektedir (DeVellis, 2012)."</em></p>

<h2>Değer Düşük Çıkarsa Ne Yapılmalı?</h2>
<p>Eğer hesapladığınız değer 0.70'in altındaysa, şu durumları kontrol edebilirsiniz:</p>
<ul>
  <li><strong>Ters Kodlanmış Sorular:</strong> Anketinizdeki olumsuz ifadeli soruları SPSS'te <code>Transform &gt; Recode into Same Variables</code> menüsü ile tersine çevirdiğinizden (reverse coding) emin olun.</li>
  <li><strong>Madde Çıkarma:</strong> SPSS çıktısındaki <code>Cronbach's Alpha if Item Deleted</code> sütununu inceleyin. Eğer problemli bir soruyu çıkardığınızda alfa değeri önemli ölçüde artıyorsa, o maddeyi ölçekten çıkarmayı düşünebilirsiniz.</li>
</ul>

<hr>
<small>
<strong>Kaynakça:</strong><br>
DeVellis, R. F. (2012). Scale development: Theory and applications (3rd ed.). Sage Publications.<br>
Nunnally, J. C. (1978). Psychometric theory (2nd ed.). McGraw-Hill.<br>
Hair, J. F., Black, W. C., Babin, B. J., &amp; Anderson, R. E. (2010). Multivariate Data Analysis (7th ed.). Pearson.
</small>"""

    BlogPost.objects.get_or_create(
        slug='cronbach-alpha-degeri-kac-olmali-tezde-nasil-yorumlanir-raporlanir',
        defaults={
            'title': 'Cronbach Alpha Değeri Kaç Olmalı? Tezde Nasıl Yorumlanır ve Raporlanır?',
            'excerpt': 'Tez öğrencilerinin ve akademisyenlerin ölçek geliştirme sürecinde en çok başvurduğu iç tutarlılık ölçütü olan Cronbach Alpha (α) değeri hakkında bilmeniz gerekenler. SPSS hesaplama adımları ve APA standartlarında raporlama örnekleri.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0076_seed_donation_tiers'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]