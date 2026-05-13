from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Eksik Veri (Missing Data) Tezde Nasıl Ele Alınır?</h2>
<p>Veri setinizi açtığınızda bazı hücrelerin boş olduğunu fark ettiniz. Analize nasıl devam edeceksiniz? Eksik verileri görmezden gelmek, silmek veya yanlış yöntemle doldurmak sonuçlarınızı ciddi biçimde çarpıtabilir. Bu yazıda eksik veri türlerini, kabul gören çözüm yöntemlerini ve tezde nasıl raporlayacağınızı bulacaksınız.</p>

<h2>Eksik Veri Türleri (Little & Rubin, 2002)</h2>
<table>
  <thead><tr><th>Tür</th><th>Kısaltma</th><th>Açıklama</th><th>Çözüm</th></tr></thead>
  <tbody>
    <tr><td>Tamamen Rastgele Eksik</td><td>MCAR</td><td>Eksiklik hiçbir değişkenle ilişkili değil</td><td>Liste silme veya ortalama atama kabul edilebilir</td></tr>
    <tr><td>Rastgele Eksik</td><td>MAR</td><td>Eksiklik gözlenen değişkenlerle açıklanabilir</td><td>Çoklu atama (MI) veya FIML önerilir</td></tr>
    <tr><td>Rastgele Olmayan Eksik</td><td>MNAR</td><td>Eksiklik bizzat eksik değerle ilişkili</td><td>Uzman danışmanlığı gerektirir — en sorunlu tür</td></tr>
  </tbody>
</table>

<h2>Yöntemlerin Karşılaştırması</h2>
<table>
  <thead><tr><th>Yöntem</th><th>Ne Zaman Kullanılır?</th><th>Dezavantaj</th></tr></thead>
  <tbody>
    <tr><td>Liste silme (Listwise deletion)</td><td>Eksiklik &lt; %5, MCAR</td><td>Örneklem küçülür, güç kaybı</td></tr>
    <tr><td>Ortalama ile doldurma</td><td>Nadiren önerilir</td><td>Varyansı düşürür, ilişkileri zayıflatır</td></tr>
    <tr><td>Çoklu atama (MI)</td><td>MAR, eksiklik &lt; %40</td><td>Karmaşık, yazılım gerektirir</td></tr>
    <tr><td>FIML (Full Information ML)</td><td>Yapısal modellerde (SEM)</td><td>Yazılım bağımlı (Amos, Mplus)</td></tr>
  </tbody>
</table>

<h2>Pratikte Ne Yapılır?</h2>
<p>1. Eksik veri oranını hesaplayın: değişken başına %5'in altındaysa liste silme genellikle kabul edilir.<br>2. Little's MCAR testini uygulayın (SPSS: Analyze → Missing Value Analysis).<br>3. %5–20 arası eksiklik için çoklu atama (SPSS Multiple Imputation) tercih edin.<br>4. %20'nin üzerinde eksik olan değişkeni analizden çıkarmayı değerlendirin.</p>

<h2>Tezde Nasıl Yazılır?</h2>
<p><em>"Veri setinde toplam gözlemlerin %3.2'si oranında eksik veri tespit edilmiştir. Little's MCAR testi sonucunda eksik verinin tamamen rastgele olduğu belirlenmiş (χ²(14) = 18.43, p = .189) ve liste silme yöntemi uygulanmıştır. Analize dahil edilen nihai örneklem 374 katılımcıdan oluşmaktadır."</em></p>

<p><strong>Verilerinizi analiz etmek için → <a href="/istatistik/normallik/">Analizus İstatistik Araçlarını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Little, R. J. A., &amp; Rubin, D. B. (2002). Statistical analysis with missing data (2nd ed.). Wiley.<br>Schafer, J. L., &amp; Graham, J. W. (2002). Missing data: Our view of the state of the art. Psychological Methods, 7(2), 147–177.</small>"""

    BlogPost.objects.get_or_create(
        slug='eksik-veri-missing-data-tezde-nasil-ele-alinir',
        defaults={'title': 'Eksik Veri (Missing Data) Tezde Nasıl Ele Alınır?', 'excerpt': 'Tez verinizde eksik gözlemler varsa ne yapmalısınız? MCAR, MAR, MNAR eksik veri türleri, liste silme ve çoklu atama yöntemleri ve APA formatında raporlama.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0109_blog_likert_hangi_test')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
