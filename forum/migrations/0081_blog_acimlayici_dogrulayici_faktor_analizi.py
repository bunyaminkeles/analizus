# forum/migrations/0081_blog_acimlayici_dogrulayici_faktor_analizi.py

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

    content = """<h2>Faktör Analizi Nedir?</h2>
<p>Sosyal bilimlerde ve psikometride yapı geçerliğini (construct validity) değerlendirmenin en güçlü yollarından biri <strong>Faktör Analizi</strong>'dir. Çok sayıda gözlenen değişkenin (örneğin ölçek maddeleri) arkasında yatan ve doğrudan gözlenemeyen örtük (latent) yapıları veya boyutları ortaya çıkarmak amacıyla kullanılır. Ölçek geliştirme ve uyarlama çalışmalarında araştırmacıların temel araçlarından biri olan faktör analizi, temel olarak iki alt türe ayrılır: <strong>Açımlayıcı Faktör Analizi (AFA)</strong> ve <strong>Doğrulayıcı Faktör Analizi (DFA)</strong>.</p>

<h2>Açımlayıcı Faktör Analizi (AFA) Nedir ve Ne Zaman Kullanılır?</h2>
<p>Açımlayıcı Faktör Analizi (AFA), verinin altında yatan yapıyı <em>keşfetmek</em> için kullanılır. Araştırmacının maddelerin hangi faktörler altında toplanacağına dair önceden belirlediği kesin bir teorik modeli yoktur; veri kendi konuşur.</p>
<ul>
  <li><strong>Ne zaman kullanılır?</strong> Yeni bir ölçek geliştiriyorsanız ve oluşturduğunuz soru havuzundaki maddelerin kaç alt boyutta toplandığını görmek istiyorsanız AFA tercih edilir.</li>
  <li><strong>Amacı:</strong> Değişken sayısını azaltmak, maddeler arasındaki ilişkileri açıklayan faktörleri bulmak ve işlevsiz (çapraşık veya düşük yük veren) maddeleri tespit edip ölçekten çıkarmaktır.</li>
</ul>

<h2>Doğrulayıcı Faktör Analizi (DFA) Nedir ve Ne Zaman Kullanılır?</h2>
<p>Doğrulayıcı Faktör Analizi (DFA), araştırmacının önceden belirlediği bir teorik veya ampirik modelin eldeki verilerle ne kadar <em>uyumlu olduğunu test etmek (doğrulamak)</em> için kullanılır. AFA'nın aksine DFA'da hangi maddenin hangi faktöre yükleneceği analize başlanmadan önce belirlenmiştir.</p>
<ul>
  <li><strong>Ne zaman kullanılır?</strong> Yabancı dilde geliştirilmiş ve yapısı belli olan bir ölçeği kendi kültürünüze/dilinize uyarlıyorsanız (Ölçek Uyarlama) veya AFA ile bulduğunuz yapıyı yeni bir örneklem üzerinde doğrulamak istiyorsanız DFA kullanmalısınız.</li>
  <li><strong>Amacı:</strong> Kurulan modelin veriye uygunluğunu Çıkarımsal İstatistik (Uyum İyiliği İndeksleri: RMSEA, CFI, TLI, SRMR vb.) yoluyla test etmektir.</li>
</ul>

<h2>AFA ve DFA Arasındaki Temel Farklar</h2>
<table>
  <thead>
    <tr>
      <th>Özellik</th>
      <th>Açımlayıcı Faktör Analizi (AFA)</th>
      <th>Doğrulayıcı Faktör Analizi (DFA)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Amaç</strong></td>
      <td>Teori oluşturmak, gizli yapıyı keşfetmek.</td>
      <td>Mevcut teoriyi veya modeli test etmek.</td>
    </tr>
    <tr>
      <td><strong>Model Özellikleri</strong></td>
      <td>Tüm maddeler tüm faktörlere serbestçe yüklenir.</td>
      <td>Maddeler sadece belirtilen faktörlere yüklenir, diğer yükler sıfır kabul edilir.</td>
    </tr>
    <tr>
      <td><strong>Yazılım Desteği</strong></td>
      <td>SPSS gibi temel istatistik programlarıyla kolayca yapılır.</td>
      <td>AMOS, LISREL, Mplus veya R (lavaan paketi) gibi özel YEM (Yapısal Eşitlik Modellemesi) yazılımları gerektirir.</td>
    </tr>
    <tr>
      <td><strong>Kullanım Alanı</strong></td>
      <td>Sıfırdan ölçek geliştirme süreci.</td>
      <td>Ölçek uyarlama veya AFA yapısının doğrulanması.</td>
    </tr>
  </tbody>
</table>

<h2>AFA Öncesi Varsayımlar: KMO ve Bartlett Küresellik Testi</h2>
<p>Veri setinizin faktör analizine uygun olup olmadığını belirlemek için iki temel test sonucu incelenmelidir:</p>
<ol>
  <li><strong>Kaiser-Meyer-Olkin (KMO) Örneklem Yeterliliği Ölçütü:</strong> KMO değeri 0 ile 1 arasında değişir. Örneklem büyüklüğünün analiz için yeterli olup olmadığını gösterir. Genellikle KMO &gt; 0.60 (tercihen 0.70 ve üzeri) faktör analizi için uygun kabul edilir.</li>
  <li><strong>Bartlett Küresellik Testi:</strong> Değişkenler arasında faktör oluşturmaya yetecek kadar yüksek korelasyon olup olmadığını test eder. Bu testin sonucunun istatistiksel olarak anlamlı çıkması (p &lt; 0.05) beklenir.</li>
</ol>

<h2>Ölçek Geliştirmede AFA ve DFA'nın Birlikte Kullanımı</h2>
<p>Modern psikometrik yaklaşımlarda, sıfırdan bir ölçek geliştiriliyorsa AFA ve DFA aynı veri seti üzerinden yapılmamalıdır. Doğru olan yöntem, örneklemi ikiye bölmek veya iki farklı örneklemden veri toplamaktır. <strong>Örneklem 1</strong> üzerinden AFA yapılarak faktör yapısı keşfedilir ve sorunlu maddeler ayıklanır. Ardından, elde edilen bu yeni yapı <strong>Örneklem 2</strong> üzerinden DFA ile doğrulanır.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Hair, J. F., Black, W. C., Babin, B. J., &amp; Anderson, R. E. (2010). Multivariate Data Analysis (7th ed.). Pearson.<br>
Tabachnick, B. G., &amp; Fidell, L. S. (2013). Using Multivariate Statistics (6th ed.). Pearson.<br>
Brown, T. A. (2015). Confirmatory Factor Analysis for Applied Research (2nd ed.). Guilford Press.
</small>"""

    BlogPost.objects.get_or_create(
        slug='acimlayici-ve-dogrulayici-faktor-analizi-afa-dfa-arasindaki-farklar',
        defaults={
            'title': 'Açımlayıcı ve Doğrulayıcı Faktör Analizi (AFA-DFA) Arasındaki Farklar ve Ne Zaman Hangisi Kullanılır?',
            'excerpt': 'Ölçek geliştirme ve uyarlama çalışmalarında yapı geçerliğini test etmek için kullanılan Açımlayıcı Faktör Analizi (AFA) ve Doğrulayıcı Faktör Analizi (DFA) arasındaki temel farkları, kullanım durumlarını ve KMO/Bartlett gibi ön şartları detaylıca inceliyoruz.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0080_blog_spsste_t_testi_adim_adim'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]