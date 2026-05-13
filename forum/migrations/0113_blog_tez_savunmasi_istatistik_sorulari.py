from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Tez Savunmasında İstatistik Soruları Nasıl Cevaplanır?</h2>
<p>Tez savunmanızda jüri üyeleri analiz tercihlerinizi, bulgularınızı ve metodolojik kararlarınızı sorgulayacaktır. Bu sorulara hazırlıksız yakalanmak savunmanın en zorlu anlarından birini oluşturur. Aşağıda en sık sorulan istatistiksel soruları ve bunlara verebileceğiniz güçlü, kısa yanıtları bulacaksınız.</p>

<h2>En Sık Sorulan İstatistik Soruları ve Cevap Şablonları</h2>

<p><strong>"Neden bu analizi seçtiniz?"</strong><br>
<em>"[Analiz adı], araştırma sorumun yapısına uygundur: [bağımlı değişken] üzerinde [bağımsız değişken]in etkisini test etmek için tasarlanmış parametrik/parametrik olmayan bir testtir. Örneklemimin [N] kişiden oluşması ve normallik varsayımının [sağlanması/sağlanmaması] bu seçimi desteklemektedir."</em></p>

<p><strong>"Örneklem büyüklüğü yeterli mi?"</strong><br>
<em>"Örneklem büyüklüğü Cochran formülüne göre hesaplanmış ve [N] kişi belirlenmiştir. Kullandığım [analiz türü] için gerekli minimum örneklem [n], elde ettiğim [N] ile karşılanmaktadır."</em></p>

<p><strong>"Normallik varsayımını nasıl kontrol ettiniz?"</strong><br>
<em>"Shapiro-Wilk testi uyguladım [N &lt; 50 için] / Kolmogorov-Smirnov testini kullandım [N ≥ 50]. Sonuçlar p = [değer] olup [0.05'ten büyük/küçük] olduğundan normallik varsayımı [sağlanmaktadır/sağlanmamaktadır]. Bu nedenle [parametrik/parametrik olmayan] testi tercih ettim."</em></p>

<p><strong>"p değeri 0.05'e çok yakın, bulgunuz güvenilir mi?"</strong><br>
<em>"İstatistiksel anlamlılık eşiği 0.05 olarak belirlenmiş olup p = [değer], bu eşiğin [altında/üzerinde] kalmaktadır. Buna ek olarak etki büyüklüğü ([d/η²/r] = [değer]) [küçük/orta/büyük] düzeyde olup bulgunun pratik önemi de değerlendirilmiştir."</em></p>

<h2>Jürinin Sevdiği İfadeler</h2>
<table>
  <thead><tr><th>Kaçının</th><th>Kullanın</th></tr></thead>
  <tbody>
    <tr><td>"Anlamlı çıktı, o yüzden kabul ettim"</td><td>"İstatistiksel anlamlılık ve etki büyüklüğü birlikte değerlendirilmiştir"</td></tr>
    <tr><td>"SPSS bunu otomatik hesapladı"</td><td>"SPSS çıktısında [tablo adı] incelenerek [değer] alınmıştır"</td></tr>
    <tr><td>"Varsayımları kontrol etmedim"</td><td>"Varsayım kontrolleri Yöntem bölümünde raporlanmıştır"</td></tr>
    <tr><td>"Bilmiyorum"</td><td>"Bu konuyu tezimde ele almadım, araştıracağım ve size döneceğim"</td></tr>
  </tbody>
</table>

<h2>Son Hazırlık İpucu</h2>
<p>Savunmadan önce tezinizdeki her tabloya bakarak şu üç soruyu cevaplayabildiğinizden emin olun: (1) Bu analizi neden seçtim? (2) Varsayımlar sağlandı mı? (3) Etki büyüklüğü ne anlama geliyor?</p>

<p><strong>Analizlerinizi gözden geçirmek için → <a href="/istatistik/normallik/">Analizus İstatistik Araçlarını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>American Psychological Association. (2020). Publication manual of the APA (7th ed.).<br>Cumming, G. (2014). The new statistics: Why and how. Psychological Science, 25(1), 7–29.</small>"""

    BlogPost.objects.get_or_create(
        slug='tez-savunmasinda-istatistik-sorulari-nasil-cevaplanir',
        defaults={'title': 'Tez Savunmasında İstatistik Soruları Nasıl Cevaplanır?', 'excerpt': 'Tez savunmasında jüri üyelerinin sorabileceği istatistiksel sorular ve güçlü cevap şablonları. Normallik, örneklem büyüklüğü, analiz seçimi ve p değeri sorularına hazırlanın.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0112_blog_ucretsiz_spss_alternatifi')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
