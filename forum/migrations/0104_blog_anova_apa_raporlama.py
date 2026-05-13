from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()
    category, _ = BlogCategory.objects.get_or_create(slug='istatistik', defaults={'name': 'İstatistik'})
    content = """<h2>ANOVA Sonucu Tezde Nasıl Raporlanır? (APA Formatı)</h2>
<p>SPSS veya başka bir programda Tek Yönlü ANOVA analizini tamamladınız. Ekranınızda F değerleri, serbestlik dereceleri ve p değerleri var. Peki bunları tezinizin Bulgular bölümüne nasıl aktaracaksınız? APA 7. baskı formatına uygun raporlama, savunmada danışmanınızın en çok dikkat ettiği noktalardan biridir.</p>

<h2>ANOVA Sonucunda Raporlanması Gereken Değerler</h2>
<table>
  <thead><tr><th>İstatistik</th><th>Sembol</th><th>Açıklama</th></tr></thead>
  <tbody>
    <tr><td>F değeri</td><td>F(df_arasında, df_içinde)</td><td>Gruplar arası / grup içi varyans oranı</td></tr>
    <tr><td>p değeri</td><td>p</td><td>İstatistiksel anlamlılık</td></tr>
    <tr><td>Eta Kare</td><td>η² veya ω²</td><td>Etki büyüklüğü — pratikte ne kadar önemli?</td></tr>
    <tr><td>Ortalama ve SS</td><td>M, SD</td><td>Her grubun ortalama ve standart sapması</td></tr>
  </tbody>
</table>

<h2>Eta Kare (η²) Yorumu</h2>
<p>η² = 0.01 küçük etki, η² = 0.06 orta etki, η² = 0.14 büyük etki olarak sınıflandırılır (Cohen, 1988). ANOVA anlamlı çıksa bile küçük etki boyutu, pratik önemi sorgulatır.</p>

<h2>Post-Hoc Test Sonucunun Raporlanması</h2>
<p>ANOVA anlamlı çıktığında hangi grupların birbirinden farklı olduğunu bulmak için post-hoc testler (Tukey HSD veya Bonferroni) yapılmalıdır. Post-hoc sonuçları grupları karşılaştırarak metin içinde verilir.</p>

<h2>Tam APA Raporlama Örneği</h2>
<p><em>"Eğitim düzeyinin (İlkokul, Lise, Üniversite) iş tatmini üzerindeki etkisini incelemek amacıyla tek yönlü ANOVA analizi uygulanmıştır. Analiz sonucunda eğitim düzeyi grupları arasında iş tatmini puanları bakımından istatistiksel olarak anlamlı farklılık bulunmuştur, F(2, 117) = 8.43, p &lt; .001, η² = .126. Tukey HSD post-hoc karşılaştırmaları sonucunda, üniversite mezunlarının (M = 72.4, SD = 8.2) hem ilkokul mezunlarından (M = 58.3, SD = 9.1; p = .001) hem de lise mezunlarından (M = 63.7, SD = 8.8; p = .012) anlamlı düzeyde daha yüksek iş tatmini bildirdiği görülmüştür."</em></p>

<h2>Raporlamada Sık Yapılan Hatalar</h2>
<p>1. F değerinden sonra serbestlik derecelerini yazmamak (F = 8.43 yerine F(2, 117) = 8.43 yazılmalı).<br>2. Anlamlı ANOVA'nın ardından post-hoc testi atlamak.<br>3. Etki büyüklüğünü raporlamamak (η² zorunludur).</p>

<p><strong>ANOVA analizinizi yapmak ve tabloları oluşturmak için → <a href="/istatistik/anova/">Analizus ANOVA aracını kullanın.</a></strong></p>
<hr>
<small><strong>Kaynakça:</strong><br>American Psychological Association. (2020). Publication manual of the APA (7th ed.).<br>Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.). Erlbaum.</small>"""

    BlogPost.objects.get_or_create(
        slug='anova-sonucu-tezde-nasil-raporlanir-apa-formati',
        defaults={'title': 'ANOVA Sonucu Tezde Nasıl Raporlanır? (APA Formatı)', 'excerpt': 'SPSS\'ten aldığınız ANOVA sonuçlarını tezinizin Bulgular bölümüne nasıl aktarırsınız? F değeri, serbestlik dereceleri, eta kare ve post-hoc test raporlama rehberi.', 'content': content, 'category': category, 'author': author, 'status': 'published'}
    )

class Migration(migrations.Migration):
    dependencies = [('forum', '0103_blog_korelasyon_yuksek_anlamsiz')]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]
