from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>Regresyon Analizi Tez Bulgular Bölümüne Nasıl Aktarılır?</h2>
<p>Çoklu doğrusal regresyon analizi tamamlandığında SPSS veya R ekranınızda onlarca sayı görünür. Bunların hepsini teze yazmak hem gereksizdir hem de danışmanınızı bunaltır. Bulgular bölümünde yalnızca okuyucunun araştırma sorusunu anlayabilmesi için gereken istatistikler raporlanmalıdır. Bu yazıda hangi değerlerin zorunlu, hangilerinin isteğe bağlı olduğunu ve APA 7 formatında nasıl sunulacağını öğreneceksiniz.</p>

<h2>Regresyon Tablosunda Olması Gereken Sütunlar</h2>
<table>
  <thead><tr><th>Sütun</th><th>Sembol</th><th>Açıklama</th></tr></thead>
  <tbody>
    <tr><td>Standartlaştırılmamış katsayı</td><td>B</td><td>Ham etki — ölçek birimiyle yorumlanır</td></tr>
    <tr><td>Standart hata</td><td>SE</td><td>B katsayısının tahmindeki hassasiyeti</td></tr>
    <tr><td>Standartlaştırılmış katsayı</td><td>β</td><td>Değişkenler arası göreli önemi karşılaştırır</td></tr>
    <tr><td>t değeri</td><td>t</td><td>Her yordayıcının anlamlılık testi</td></tr>
    <tr><td>p değeri</td><td>p</td><td>İstatistiksel anlamlılık</td></tr>
    <tr><td>VIF</td><td>VIF</td><td>Çoklu bağlantı kontrolü — 10'dan küçük olmalı</td></tr>
  </tbody>
</table>

<h2>Model Özet Değerleri — Tablo Altına veya Metin İçine Eklenir</h2>
<table>
  <thead><tr><th>Değer</th><th>Sembol</th><th>Eşik / Yorum</th></tr></thead>
  <tbody>
    <tr><td>R Kare</td><td>R²</td><td>Bağımlı değişkendeki varyansın açıklanan oranı</td></tr>
    <tr><td>Düzeltilmiş R Kare</td><td>R²<sub>adj</sub></td><td>Değişken sayısına göre düzeltilmiş — tercih edilir</td></tr>
    <tr><td>F değeri</td><td>F(df₁, df₂)</td><td>Modelin bütünü olarak anlamlılığı</td></tr>
    <tr><td>Durbin-Watson</td><td>DW</td><td>Otokorelasyon — 1.5–2.5 arası kabul edilir</td></tr>
  </tbody>
</table>

<h2>APA 7 Formatında Regresyon Tablosu Örneği</h2>
<p><em>Tablo 5</em><br><em>Çalışma Motivasyonu, Öz-Yeterlik ve Sosyal Destek Değişkenlerinin İş Performansını Yordaması</em></p>
<table>
  <thead><tr><th>Yordayıcı</th><th>B</th><th>SE</th><th>β</th><th>t</th><th>p</th><th>VIF</th></tr></thead>
  <tbody>
    <tr><td>Sabit</td><td>12.34</td><td>3.21</td><td>—</td><td>3.84</td><td>.001</td><td>—</td></tr>
    <tr><td>Çalışma Motivasyonu</td><td>0.48</td><td>0.09</td><td>.41</td><td>5.33</td><td>&lt;.001</td><td>1.82</td></tr>
    <tr><td>Öz-Yeterlik</td><td>0.31</td><td>0.11</td><td>.22</td><td>2.82</td><td>.005</td><td>1.74</td></tr>
    <tr><td>Sosyal Destek</td><td>0.19</td><td>0.12</td><td>.13</td><td>1.58</td><td>.116</td><td>1.63</td></tr>
  </tbody>
</table>
<p><em>Not.</em> R² = .38, R²<sub>adj</sub> = .36, F(3, 146) = 29.87, p &lt; .001. VIF değerleri çoklu bağlantı sorunu olmadığını göstermektedir.</p>

<h2>Metin İçi APA Raporlama</h2>
<p><em>"Çalışma motivasyonu, öz-yeterlik ve sosyal desteğin iş performansını yordayıp yordamadığını incelemek amacıyla çoklu doğrusal regresyon analizi uygulanmıştır. Model istatistiksel olarak anlamlı bulunmuş, F(3, 146) = 29.87, p &lt; .001, ve bağımlı değişkendeki varyansın %38'ini açıklamıştır (R²<sub>adj</sub> = .36). Standardize katsayılar incelendiğinde çalışma motivasyonunun (β = .41, p &lt; .001) ve öz-yeterliğin (β = .22, p = .005) iş performansını anlamlı düzeyde yordadığı; sosyal desteğin ise anlamlı bir yordayıcı olmadığı görülmüştür (β = .13, p = .116)."</em></p>

<h2>Sık Yapılan Hatalar</h2>
<p>1. Standartlaştırılmamış (B) ile standartlaştırılmış (β) katsayıyı karıştırmak.<br>2. Model genel F testini raporlamayı unutmak.<br>3. Anlamlı çıkmayan yordayıcıları "etkisi yok" diye yorumlamak — "anlamlı düzeyde yordamamaktadır" ifadesini kullanın.<br>4. Varsayım kontrollerini (normallik, doğrusallık, VIF) bulgulara yazmamak.</p>

<p><strong>Regresyon analizinizi yapmak için → <a href="/istatistik/lineer-regresyon/">Analizus Lineer Regresyon aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>American Psychological Association. (2020). Publication manual of the APA (7th ed.).<br>Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>Hair, J. F., Black, W. C., Babin, B. J., & Anderson, R. E. (2019). Multivariate data analysis (8th ed.). Cengage.</small>"""

    BlogPost.objects.get_or_create(
        slug='regresyon-analizi-tez-bulgular-bolumune-nasil-aktarilir',
        defaults={'title': 'Regresyon Analizi Tez Bulgular Bölümüne Nasıl Aktarılır?', 'excerpt': 'Çoklu doğrusal regresyon sonuçlarını tezin Bulgular bölümüne nasıl aktarırsınız? APA 7 formatında regresyon tablosu, B, β, R², F ve VIF raporlama rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0106_blog_cronbach_guvenilirlik_nasil_yazilir')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
