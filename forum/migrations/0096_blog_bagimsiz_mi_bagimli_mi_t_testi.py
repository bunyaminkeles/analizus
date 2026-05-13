from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Bağımsız mı Bağımlı mı t-Testi? Fark Ne Zaman Önemli?</h2>
<p>Gruplar arası karşılaştırma yapmak isteyen her araştırmacının karşılaştığı ilk soru şudur: "Acaba bağımsız örneklem (Independent Samples) t-testi mi yapmalıyım, yoksa bağımlı örneklem (Paired Samples) t-testi mi?" Özellikle yüksek lisans öğrencileri veri setlerini kurarken bu iki test arasındaki yapısal farkı sıklıkla karıştırır. Yanlış testi seçmek, sadece p-değerinin hatalı çıkmasına değil, tüm tezin metodolojisinin çökmesine neden olabilir.</p>

<h2>Kısa Tanım: İki Testin Mantığı</h2>
<p><strong>Bağımsız Örneklem t-Testi:</strong> Birbiriyle tamamen ilgisiz, ayrı bireylerden oluşan iki farklı grubun ortalamalarını karşılaştırmak için kullanılır. Bir gruptaki kişinin skoru diğer gruptaki kişiyi hiçbir şekilde etkilemez.</p>
<p><strong>Bağımlı (Eşleştirilmiş) Örneklem t-Testi:</strong> Aynı katılımcı grubundan farklı zamanlarda veya farklı durumlarda alınan iki ölçümü (çiftleri) karşılaştırmak için kullanılır. Kişi kendi kendisiyle karşılaştırılır.</p>

<h2>Ne Zaman Kullanılır?</h2>
<p>Eğer çalışmanızda <strong>Kesitsel Tasarım (Cross-sectional)</strong> varsa ve katılımcıları iki kategoriye ayırıp (örneğin kontrol ve deney grubu veya kadın ve erkek) belirli bir değişken üzerindeki farklarını arıyorsanız, mutlaka "Bağımsız Örneklem" testini kullanmalısınız.</p>
<p>Buna karşılık, çalışmanızda <strong>Boylamsal (Longitudinal) veya Deneysel bir tasarım</strong> varsa ve bir gruba eğitim verip öncesindeki ve sonrasındaki durumları gözlemliyorsanız "Bağımlı Örneklem" testini kullanmalısınız.</p>

<h2>Örnek Senaryo Tablosu</h2>
<table>
  <thead><tr><th>Araştırma Sorusu</th><th>t-Testi Türü</th><th>Gerekçe</th></tr></thead>
  <tbody>
    <tr><td>Özel okul ve devlet okulu öğrencilerinin matematik başarı puanları arasında fark var mıdır?</td><td><strong>Bağımsız Örneklem</strong></td><td>Gruplar birbirinden tamamen farklıdır.</td></tr>
    <tr><td>Diyet programına katılan hastaların başlamadan önceki ve 3 ay sonraki kiloları arasında fark var mıdır?</td><td><strong>Bağımlı Örneklem</strong></td><td>Aynı hastanın iki ayrı ölçümü karşılaştırılır.</td></tr>
  </tbody>
</table>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><strong>Bağımsız Örneklem:</strong> <em>"Kadın katılımcıların algılanan stres düzeyleri (M = 45.2, SD = 8.1), erkek katılımcıların stres düzeylerinden (M = 39.4, SD = 9.3) istatistiksel olarak anlamlı düzeyde daha yüksek bulunmuştur, t(102) = 3.41, p = .001."</em></p>
<p><strong>Bağımlı Örneklem:</strong> <em>"Öğrencilerin eğitim sonrası başarı puanları (M = 85.6, SD = 5.2), eğitim öncesi puanlarına (M = 65.4, SD = 7.1) kıyasla anlamlı düzeyde artış göstermiştir, t(49) = 12.35, p &lt; .001."</em></p>

<p><strong>Hangi testin verinize uygun olduğunu hesaplamak için → <a href="/istatistik/ttesti/">Analizus t-Testi aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>Büyüköztürk, Ş. (2018). Sosyal Bilimler İçin Veri Analizi El Kitabı. Pegem Akademi.</small>"""

    BlogPost.objects.get_or_create(
        slug='bagimsiz-mi-bagimli-mi-t-testi-fark-ne-zaman-onemli',
        defaults={'title': 'Bağımsız mı Bağımlı mı t-Testi? Fark Ne Zaman Önemli?', 'excerpt': 'Independent ve Paired (Bağımsız ve Bağımlı) t-testleri arasındaki fark nedir? Araştırma tasarımınıza en uygun analizi seçmek için örnek senaryolar ve APA raporlaması.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0095_blog_normallik_testi_saglanmazsa')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
