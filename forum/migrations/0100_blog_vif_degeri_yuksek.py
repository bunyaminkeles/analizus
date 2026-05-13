from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>VIF Değeri Yüksek Çıktı, Çoklu Doğrusal Bağlantı Ne Demek?</h2>
<p>Lineer regresyon analizinde SPSS veya başka bir programdan elde ettiğiniz "Collinearity Statistics" tablosunda VIF değerlerinden biri 10'un üzerinde çıktı. Danışmanınız "çoklu doğrusal bağlantı (multicollinearity) var" dedi. Peki bu ne anlama geliyor ve tez süreciniz için ne yapmanız gerekiyor?</p>

<h2>VIF Nedir?</h2>
<p>VIF (Variance Inflation Factor — Varyans Şişirme Faktörü), bir regresyon modelindeki bağımsız değişkenlerin birbirleriyle ne kadar ilişkili olduğunu ölçer. Temel mantık şudur: Eğer iki bağımsız değişken birbiriyle çok yüksek korelasyona sahipse (örneğin r = 0.90), model bunların bireysel etkisini güvenilir biçimde hesaplayamaz. VIF değeri, bu şişmeyi sayısal olarak ifade eder.</p>

<h2>VIF Değerleri Nasıl Yorumlanır?</h2>
<table>
  <thead><tr><th>VIF Değeri</th><th>Yorum</th><th>Yapılacak İşlem</th></tr></thead>
  <tbody>
    <tr><td>1.0 – 5.0</td><td>Düşük / Kabul edilebilir</td><td>Sorun yok, analize devam</td></tr>
    <tr><td>5.0 – 10.0</td><td>Orta düzey</td><td>Dikkatli yorumla, gerekirse önlem al</td></tr>
    <tr><td>&gt; 10.0</td><td>Yüksek / Ciddi multicollinearity</td><td>Değişken çıkar veya dönüştür</td></tr>
  </tbody>
</table>

<h2>VIF Yüksek Çıkınca Ne Yapılır?</h2>
<p><strong>1. Sorunlu değişkeni modelden çıkarın:</strong> İki yüksek korelasyonlu değişkenden teorik olarak daha az önemli olanı çıkarmak çoğu zaman en pratik çözümdür.</p>
<p><strong>2. Değişkenleri birleştirin:</strong> Birbiriyle yüksek korelasyonlu ölçekler varsa bunları ortalama alarak tek bir bileşik değişkene dönüştürebilirsiniz.</p>
<p><strong>3. Ridge Regresyon kullanın:</strong> Multicollinearity problemi ciddiyse Ridge Regresyon gibi düzenlileştirme (regularization) yöntemleri tercih edilebilir.</p>
<p><strong>4. Veri toplayın:</strong> Daha büyük örneklem bazen multicollinearity etkisini azaltır ancak kesin çözüm değildir.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Regresyon modelinde çoklu doğrusal bağlantı sorununun olup olmadığı VIF (Varyans Şişirme Faktörü) değerleri ile incelenmiştir. Analiz sonucunda tüm bağımsız değişkenlerin VIF değerlerinin 10'un altında kaldığı (VIF aralığı: 1.12 – 3.45) ve tolerans değerlerinin 0.10'un üzerinde olduğu görülmüştür. Bu bulgular, modelde çoklu doğrusal bağlantı sorununun bulunmadığına işaret etmektedir (Hair vd., 2010)."</em></p>

<p><strong>Regresyon analizinizi ve VIF değerlerinizi hesaplamak için → <a href="/istatistik/lineer-regresyon/">Analizus Çoklu Doğrusal Regresyon aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Hair, J. F., Black, W. C., Babin, B. J., &amp; Anderson, R. E. (2010). Multivariate Data Analysis (7th ed.). Pearson.<br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.</small>"""

    BlogPost.objects.get_or_create(
        slug='vif-degeri-yuksek-cikti-cok-dogrusal-baglanti-ne-demek',
        defaults={'title': 'VIF Değeri Yüksek Çıktı, Çoklu Doğrusal Bağlantı Ne Demek?', 'excerpt': 'Regresyon analizinde VIF değeri 10\'un üzerinde çıktığında ne yapmalısınız? Multicollinearity (çoklu doğrusal bağlantı) sorununun tanımı, yorumu ve tezdeki çözüm yolları.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0099_blog_p_degeri_0_05_buyuk')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
