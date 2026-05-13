from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Ki-Kare mi Lojistik Regresyon mu? İkisinin Farkı Ne?</h2>
<p>Kategorik verilerle (örneğin "Evet/Hayır", "Kadın/Erkek", "Hasta/Sağlıklı") çalışırken araştırmacıların en çok kararsız kaldığı iki analiz yöntemi <strong>Ki-Kare (Chi-Square) Testi</strong> ve <strong>Lojistik Regresyon</strong> modelidir. İki analiz de bağımlı değişkenin kategorik olduğu durumlarda çalışır. Ancak araştırma sorunuz sadece bir "ilişkiyi" mi arıyor, yoksa karmaşık bir "tahmin modeli" mi kurmak istiyor; işte testin kaderini bu ayrım belirler.</p>

<h2>Kısa Tanım: Kavramsal Çerçeve</h2>
<p><strong>Ki-Kare Bağımsızlık Testi:</strong> İki kategorik değişken arasında anlamlı bir ilişki olup olmadığını test eder. Sadece "A ile B arasında bağlantı var mı?" sorusuna yanıt verir, etkinin boyutunu veya çoklu değişkenlerin etkisini modelleyemez.</p>
<p><strong>Lojistik Regresyon:</strong> İki sonuçlu kategorik bir bağımlı değişkeni, bir veya daha fazla bağımsız değişken kullanarak <em>tahmin etmeye</em> yarar. Hangi değişkenin olasılığı (Odds Ratio) kaç kat artırdığını gösterir.</p>

<h2>Ne Zaman Kullanılır?</h2>
<p>Elinizde sadece iki adet kategorik soru varsa ve bunların birbiriyle bağlantılı olup olmadığını çapraz tablolarla görmek istiyorsanız <strong>Ki-Kare testi</strong> yeterlidir. Fakat bir bağımlı değişkeni birden fazla bağımsız değişkenle (sürekli veya kategorik) tahmin eden bir model kurmak istiyorsanız <strong>Lojistik Regresyon</strong> şarttır.</p>

<h2>Örnek Senaryo Karşılaştırması</h2>
<table>
  <thead><tr><th>Araştırma Amacı</th><th>Analiz Yöntemi</th><th>Elde Edilecek Sonuç</th></tr></thead>
  <tbody>
    <tr><td>Cinsiyet ile kulüp üyeliği arasında ilişki var mıdır?</td><td><strong>Ki-Kare Testi</strong></td><td>İlişki var/yok (p değeri)</td></tr>
    <tr><td>Cinsiyet, yaş ve GPA birlikte kulübe üye olmayı yordamakta mıdır?</td><td><strong>Lojistik Regresyon</strong></td><td>GPA'nın her 1 birimlik artışı üyelik olasılığını 1.4 kat artırır (OR)</td></tr>
  </tbody>
</table>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><strong>Ki-Kare:</strong> <em>"Katılımcıların cinsiyetleri ile sigara kullanma durumları arasında istatistiksel olarak anlamlı bir ilişki bulunmuştur, χ²(1, N=200) = 5.42, p = .020."</em></p>
<p><strong>Lojistik Regresyon:</strong> <em>"Yaş, cinsiyet ve stres düzeyinin kalp krizi geçirme durumunu yordama gücünü incelemek amacıyla Lojistik Regresyon analizi uygulanmıştır. Model istatistiksel olarak anlamlı bulunmuş (χ²(3) = 24.12, p &lt; .001) ve artan yaşın kalp krizi geçirme olasılığını 1.15 kat artırdığı (OR = 1.15, %95 CI [1.02, 1.30], p = .012) tespit edilmiştir."</em></p>

<p><strong>Kategorik veri analizlerinizi hemen yapmak için → <a href="/istatistik/ki-kare/">Analizus Ki-Kare Testi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Hosmer, D. W., Lemeshow, S., &amp; Sturdivant, R. X. (2013). Applied logistic regression. Wiley.<br>Agresti, A. (2018). An introduction to categorical data analysis (3rd ed.). Wiley.</small>"""

    BlogPost.objects.get_or_create(
        slug='ki-kare-mi-lojistik-regresyon-mu-ikisinin-farki-ne',
        defaults={'title': 'Ki-Kare mi Lojistik Regresyon mu? İkisinin Farkı Ne?', 'excerpt': 'Kategorik bağımlı değişkenlerde çapraz tablo ilişkisi kuran Ki-Kare testi ile olasılık tahmin modeli kuran Lojistik Regresyon arasındaki farklar ve seçim rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0097_blog_anova_mi_mann_whitney_mi')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
