from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>R² Düşük Çıkınca Regresyon Modeli Geçersiz mi Sayılır?</h2>
<p>Lineer regresyon analizinizi tamamladınız ve Model Summary tablosunda R² = 0.12 gibi düşük bir değer gördünüz. "Modelim sadece varyansın %12'sini açıklıyor, tezimi nasıl savunacağım?" diye düşünüyorsanız, doğru soruyu yanlış bağlamda soruyorsunuz olabilirsiniz. R² tek başına bir modelin iyi mi kötü mü olduğunu söylemez.</p>

<h2>R² Nedir ve Ne Söyler?</h2>
<p>R² (Determinasyon Katsayısı), bağımsız değişken(ler)in bağımlı değişkendeki varyansı açıklama oranını gösterir. R² = 0.12 demek, modelinizdeki bağımsız değişkenlerin bağımlı değişkendeki değişimin %12'sini açıkladığı anlamına gelir. Geri kalan %88 ise modele dahil edilmemiş başka faktörlerden kaynaklanır.</p>

<h2>Alan Bağlamına Göre Kabul Edilebilir R² Değerleri</h2>
<table>
  <thead><tr><th>Araştırma Alanı</th><th>Kabul Edilebilir R²</th><th>Gerekçe</th></tr></thead>
  <tbody>
    <tr><td>Sosyal Bilimler, Psikoloji</td><td>0.10 – 0.30</td><td>İnsan davranışı çok faktörlüdür; düşük R² normaldir</td></tr>
    <tr><td>Eğitim Bilimleri</td><td>0.15 – 0.35</td><td>Öğrenmeyi etkileyen sayısız değişken vardır</td></tr>
    <tr><td>İşletme, Finans</td><td>0.30 – 0.60</td><td>Sayısal veriler daha tahmin edilebilirdir</td></tr>
    <tr><td>Fizik, Mühendislik</td><td>0.80+</td><td>Kontrollü deneylerde yüksek açıklama beklenir</td></tr>
  </tbody>
</table>

<h2>Düşük R² ile Model Geçerli Olabilir mi?</h2>
<p>Evet. Şu koşullar sağlanıyorsa R² = 0.12 bile savunulabilir bir bulgudur:</p>
<p><strong>1. Model F testi anlamlı (p &lt; 0.05):</strong> F testi modelin bir bütün olarak anlamlı olup olmadığını test eder. F anlamlı ise model toplam olarak işe yarıyor demektir.</p>
<p><strong>2. Teorik gerekçe sağlam:</strong> Seçtiğiniz bağımsız değişkenlerin neden bağımlı değişkeni etkileyebileceğini literatürle destekliyorsanız, R²'nin düşük olması model seçiminin yanlış olduğu anlamına gelmez.</p>
<p><strong>3. Keşfedici (Exploratory) araştırma:</strong> Daha önce test edilmemiş ilişkileri keşfeden çalışmalarda düşük R² kabul edilebilir bir başlangıç bulgusudur.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p><em>"Kurulan regresyon modeli istatistiksel olarak anlamlı bulunmuştur, F(3, 96) = 4.62, p = .005. Model, iş tatmini puanlarındaki varyansın %12.6'sını açıklamaktadır (R² = .126, düzeltilmiş R² = .099). Sosyal bilimler alanındaki araştırmalarda bu düzeyde bir açıklama oranının kabul edilebilir olduğu bilinmektedir (Cohen, 1988)."</em></p>

<p><strong>R² ve regresyon katsayılarınızı hesaplamak için → <a href="/istatistik/lineer-regresyon/">Analizus Çoklu Doğrusal Regresyon aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.). Erlbaum.<br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.</small>"""

    BlogPost.objects.get_or_create(
        slug='r-kare-dusuk-cikinca-regresyon-modeli-gecersiz-mi',
        defaults={'title': 'R² Düşük Çıkınca Regresyon Modeli Geçersiz mi Sayılır?', 'excerpt': 'Regresyon analizinde R² değeri düşük çıktığında model geçersiz mi olur? Sosyal bilimlerde kabul edilebilir R² eşikleri, F testi önemi ve APA raporlama rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0100_blog_vif_degeri_yuksek')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
