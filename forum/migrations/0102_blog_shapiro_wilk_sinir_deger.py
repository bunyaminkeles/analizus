from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Shapiro-Wilk p=0.049 Çıktı, Normal Dağılım Var mı Yok mu?</h2>
<p>Normallik testi yaptınız ve Shapiro-Wilk p değeri tam sınırda, 0.049 çıktı. 0.05'ten küçük olduğu için teknik olarak "normal dağılım yok" demek gerekiyor ama bu kadar yakın bir değerde gerçekten non-parametrik teste mi geçmek zorundasınız? Bu soru, istatistik danışmanlarının da sıklıkla tartıştığı nüanslı bir konudur.</p>

<h2>Shapiro-Wilk Testinin Kısıtlaması: Büyük Örnekleme Duyarlılık</h2>
<p>Shapiro-Wilk testinin kritik bir özelliği vardır: <strong>örneklem büyüdükçe çok küçük sapmalara bile anlamlı tepki verir.</strong> N = 200 olan bir örneklemde veriler neredeyse mükemmel normal dağılıyor olsa bile, çok ufak bir sapma nedeniyle p &lt; 0.05 çıkabilir. Tersine, N = 20 olan küçük bir örneklemde veri çok çarpık olsa bile p &gt; 0.05 çıkabilir çünkü test yetersiz güce sahiptir.</p>
<p>Bu nedenle Shapiro-Wilk testini tek başına karar verici olarak kullanmak doğru değildir.</p>

<h2>p=0.049 Durumunda Kontrol Edilmesi Gereken 3 Ek Ölçüt</h2>
<table>
  <thead><tr><th>Kontrol</th><th>Kabul Edilebilir Sınır</th><th>Ne Anlama Gelir?</th></tr></thead>
  <tbody>
    <tr><td>Çarpıklık (Skewness)</td><td>-1.5 ile +1.5 arası</td><td>Bu sınırlar içindeyse normal dağılım varsayımı sürdürülebilir</td></tr>
    <tr><td>Basıklık (Kurtosis)</td><td>-1.5 ile +1.5 arası</td><td>Uç değerlerin fazlalığı veya azlığı hakkında bilgi verir</td></tr>
    <tr><td>Örneklem Büyüklüğü</td><td>N &gt; 50 ise</td><td>Merkezi Limit Teoremi'ne göre dağılım normal kabul edilebilir</td></tr>
  </tbody>
</table>

<h2>Karar Algoritması</h2>
<p>Shapiro-Wilk p = 0.049 çıktığında şu soruları sorun:</p>
<p><strong>1. Örneklem büyüklüğünüz N &gt; 100 mü?</strong> Evet ise bu p değeri büyük olasılıkla örneklem büyüklüğüne bağlı hassasiyetten kaynaklanıyordur. Çarpıklık ve basıklık değerlerine bakın.</p>
<p><strong>2. Çarpıklık ve basıklık değerleri -1.5 ile +1.5 arasında mı?</strong> Evet ise parametrik teste devam edebilir ve tezinizde bunu gerekçelendirebilirsiniz.</p>
<p><strong>3. Histogram ve Q-Q Plot'a baktınız mı?</strong> Grafiksel yöntemler, sayısal testlerin veremediği bütünsel resmi sunar. Eğri çan şeklini andırıyorsa ve Q-Q Plot çizgiye yakın seyrediyorsa normallik kabul edilebilir.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Verilerin normal dağılım gösterip göstermediğini incelemek amacıyla Shapiro-Wilk normallik testi uygulanmıştır. Test sonucunda p = .049 bulunmuş olmakla birlikte, çarpıklık değerinin (Skewness = 0.42, SE = 0.19) ve basıklık değerinin (Kurtosis = 0.87, SE = 0.38) kabul edilebilir sınırlar içinde (-1.5 ile +1.5) yer aldığı ve örneklem büyüklüğünün (N = 185) yeterli olduğu göz önüne alındığında, veri setinin normal dağılım varsayımını yeterince karşıladığı kabul edilmiş ve parametrik testler uygulanmıştır."</em></p>

<p><strong>Verilerinizin normallik analizini yapmak için → <a href="/istatistik/normallik/">Analizus Normallik Testi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>Kim, H. Y. (2013). Statistical notes for clinical researchers: Assessing normal distribution. Restorative Dentistry &amp; Endodontics, 38(1), 52–54.</small>"""

    BlogPost.objects.get_or_create(
        slug='shapiro-wilk-p-0-049-normal-dagitim-var-mi-yok-mu',
        defaults={'title': 'Shapiro-Wilk p=0.049 Çıktı, Normal Dağılım Var mı Yok mu?', 'excerpt': 'Shapiro-Wilk normallik testi p değeri tam sınırda 0.049 çıktığında ne yapmalısınız? Büyük örneklem duyarlılığı, çarpıklık-basıklık sınırları ve doğru karar verme rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0101_blog_r_kare_dusuk')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
