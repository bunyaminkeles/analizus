# forum/migrations/0079_blog_normallik_testi_sonuclari_nasil_yorumlanir.py

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

    content = """<h2>Normallik Testi Nedir ve Neden Önemlidir?</h2>
<p>Nicel veri analizinde, özellikle Bağımsız Örneklem T-Testi veya ANOVA gibi parametrik testleri uygulamadan önce karşılamanız gereken en temel varsayım <strong>verilerin normal dağılıma</strong> sahip olmasıdır. Verilerinizin normal dağılıp dağılmadığını belirlemek için hipotez testleri olan normallik testlerine başvurulur. Bu testler, elinizdeki örneklem dağılımının ideal (teorik) bir normal dağılımdan anlamlı bir şekilde farklı olup olmadığını kontrol eder.</p>

<h2>Shapiro-Wilk ve Kolmogorov-Smirnov: Hangisini Seçmeliyim?</h2>
<p>Normallik sınaması söz konusu olduğunda en çok kullanılan iki istatistiksel test <strong>Shapiro-Wilk (S-W)</strong> ve <strong>Kolmogorov-Smirnov (K-S)</strong> testleridir. Bu iki testin seçimi genellikle örneklem büyüklüğüne (N) bağlıdır:</p>

<table>
  <thead>
    <tr>
      <th>Test Adı</th>
      <th>Kullanım Durumu (Örneklem Büyüklüğü)</th>
      <th>Özellikleri</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Shapiro-Wilk</strong></td>
      <td>Genellikle N &lt; 50 (Bazı kaynaklara göre N &lt; 300)</td>
      <td>Küçük örneklemlerde daha güçlü ve güvenilirdir. Verinin normal dağılımdan sapmalarına karşı hassastır.</td>
    </tr>
    <tr>
      <td><strong>Kolmogorov-Smirnov</strong></td>
      <td>Genellikle N ≥ 50</td>
      <td>Büyük örneklemlerde tercih edilir. Ancak, SPSS'te genellikle Lilliefors düzeltmesi ile birlikte kullanılır.</td>
    </tr>
  </tbody>
</table>

<p><em>Not: Modern istatistik literatüründe, Shapiro-Wilk testinin her iki durum için de daha tutarlı sonuçlar verdiği sıkça vurgulanmaktadır.</em></p>

<h2>SPSS'te Normallik Testi Nasıl Yapılır?</h2>
<p>SPSS programında verilerinizin normal dağılıp dağılmadığını kontrol etmek için şu adımları izleyebilirsiniz:</p>
<ol>
  <li>Üst menüden <code>Analyze</code> sekmesine tıklayın.</li>
  <li><code>Descriptive Statistics</code> üzerine gelin ve <code>Explore...</code> seçeneğine tıklayın.</li>
  <li>Test etmek istediğiniz sürekli değişkeni (veya ölçek puanını) <code>Dependent List</code> kutusuna atın.</li>
  <li>Eğer gruplar arası (örneğin cinsiyete göre) bir normallik incelemesi yapacaksanız, grup değişkeninizi <code>Factor List</code> kutusuna ekleyin.</li>
  <li>Sağ taraftaki <code>Plots...</code> butonuna tıklayın.</li>
  <li>Açılan pencerede <code>Normality plots with tests</code> kutucuğunu işaretleyin.</li>
  <li>Önce <code>Continue</code>, ardından <code>OK</code> butonuna basarak analizi çalıştırın.</li>
</ol>

<h2>Test Sonuçları (p-değeri) Nasıl Yorumlanır?</h2>
<p>SPSS çıktısındaki <strong>"Tests of Normality"</strong> tablosunda hem Kolmogorov-Smirnov hem de Shapiro-Wilk testlerinin sonuçları yer alır. Yorumlama yaparken <strong>Sig. (p-değeri)</strong> sütununa bakılır.</p>
<ul>
  <li><strong>p > 0.05 ise:</strong> Veriler normal dağılmaktadır (Normallik varsayımı sağlanmıştır). Testin temel hipotezi (H0: Veri normal dağılıma uyar) reddedilemez.</li>
  <li><strong>p < 0.05 ise:</strong> Veriler normal dağılmamaktadır. Dağılımın normalden anlamlı derecede saptığı anlamına gelir.</li>
</ul>

<h2>Sadece Normallik Testleri Yeterli mi? Çarpıklık ve Basıklık Değerleri</h2>
<p>Büyük örneklemlerde (örneğin N > 300), normallik testleri çok küçük sapmaları bile anlamlı bularak (p < 0.05) verinin normal dağılmadığını söyleyebilir. Bu nedenle normallik testleri tek başına yeterli görülmez. Mutlaka <strong>Çarpıklık (Skewness)</strong> ve <strong>Basıklık (Kurtosis)</strong> değerleri ile grafiksel yöntemler de incelenmelidir.</p>

<p>Genel kabul gören kurala göre, Çarpıklık ve Basıklık değerleri <strong>-1.5 ile +1.5</strong> (bazı kaynaklara göre -2 ile +2) arasında ise verinin normal dağılıma sahip olduğu kabul edilebilir. Ek olarak, Q-Q Plot grafikleri ve Histogramlar da dağılımın görsel olarak yorumlanmasında en büyük yardımcılarınızdır.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Tabachnick, B. G., &amp; Fidell, L. S. (2013). Using multivariate statistics (6th ed.). Pearson.<br>
Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>
George, D., &amp; Mallery, P. (2019). IBM SPSS Statistics 26 Step by Step: A Simple Guide and Reference (16th ed.). Routledge.
</small>"""

    BlogPost.objects.get_or_create(
        slug='normallik-testi-sonuclari-nasil-yorumlanir-shapiro-wilk-kolmogorov-smirnov',
        defaults={
            'title': 'Normallik Testi Sonuçları Nasıl Yorumlanır? Shapiro-Wilk ve Kolmogorov-Smirnov Karşılaştırması',
            'excerpt': 'Tez ve makalelerinizde parametrik testlere geçmeden önce yapmanız gereken normallik testlerini (Shapiro-Wilk ve Kolmogorov-Smirnov) nasıl seçeceğinizi ve SPSS sonuçlarını nasıl yorumlayacağınızı adım adım öğrenin.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0078_fix_cronbach_excerpt_category'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]