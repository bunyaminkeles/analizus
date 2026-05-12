# forum/migrations/0080_blog_spsste_t_testi_adim_adim.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='spss-rehberleri',
        defaults={'name': 'SPSS Rehberleri', 'icon': 'bi-table', 'color': '#3b82f6'},
    )

    content = """<h2>t-Testi Nedir ve Ne İşe Yarar?</h2>
<p>Nicel araştırmalarda en sık kullanılan istatistiksel analizlerden biri olan <strong>t-testi</strong>, iki grubun (veya aynı grubun iki farklı ölçümünün) ortalamaları arasında istatistiksel olarak anlamlı bir fark olup olmadığını belirlemek için kullanılır. Tez veya makalenizde bağımsız değişkeninizin bağımlı değişken üzerindeki etkisini inceleyip grup karşılaştırmaları yapmanız gerekiyorsa, t-testi genellikle ilk başvuracağınız parametrik analiz yöntemidir.</p>

<h2>t-Testi Türleri: Hangisini Kullanmalıyım?</h2>
<p>Hangi t-testini uygulayacağınız, araştırma deseninize ve verilerinizin yapısına bağlıdır.</p>

<table>
  <thead>
    <tr>
      <th>Test Türü</th>
      <th>Kullanım Amacı</th>
      <th>Örnek Durum</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Bağımsız Örneklem t-Testi (Independent Samples t-Test)</strong></td>
      <td>İki farklı ve birbiriyle ilişkisiz (bağımsız) grubun ortalamalarını karşılaştırır.</td>
      <td>Kadınların ve erkeklerin akademik başarı puanlarının karşılaştırılması.</td>
    </tr>
    <tr>
      <td><strong>Bağımlı Örneklem t-Testi (Paired Samples t-Test)</strong></td>
      <td>Aynı grubun iki farklı zamandaki, durumdaki veya koşuldaki ortalamalarını karşılaştırır.</td>
      <td>Öğrencilerin eğitim öncesi (ön test) ve eğitim sonrası (son test) puanlarının karşılaştırılması.</td>
    </tr>
  </tbody>
</table>

<h2>Adım Adım Bağımsız Örneklem t-Testi (Independent Samples)</h2>
<h3>SPSS Uygulama Adımları</h3>
<ol>
  <li>Üst menüden <code>Analyze &gt; Compare Means &gt; Independent-Samples T Test...</code> yolunu izleyin.</li>
  <li>Test edilecek sürekli bağımlı değişkeninizi (örneğin; Başarı Puanı) <code>Test Variable(s)</code> kutusuna aktarın.</li>
  <li>İki gruptan oluşan kategorik bağımsız değişkeninizi (örneğin; Cinsiyet) <code>Grouping Variable</code> kutusuna aktarın.</li>
  <li>Aktardığınız değişkenin yanındaki <code>Define Groups...</code> butonuna tıklayarak gruplarınıza SPSS'te atadığınız kodları (örneğin Kadın için 1, Erkek için 2) girin ve <code>Continue</code> butonuna basın.</li>
  <li><code>OK</code> butonuna tıklayarak analizi çalıştırın.</li>
</ol>

<h3>Sonuçların Yorumlanması</h3>
<p>SPSS çıktısında <strong>Independent Samples Test</strong> tablosunu dikkatle incelemelisiniz. Burada iki aşamalı bir kontrol yapılır:</p>
<ul>
  <li><strong>Levene's Test for Equality of Variances:</strong> İlk olarak varyansların homojenliği varsayımı kontrol edilir. Eğer <strong>Sig. (p-değeri) &gt; 0.05</strong> ise varyanslar eşittir (homojendir). Bu durumda <em>"Equal variances assumed"</em> yazan üst satırdaki değerler okunur. Eğer p &lt; 0.05 ise varyanslar eşit değildir, o zaman <em>"Equal variances not assumed"</em> yazan alt satırdaki t-testi sonuçları dikkate alınır.</li>
  <li><strong>t-testi Anlamlılık Değeri:</strong> Doğru satırı belirledikten sonra <strong>Sig. (2-tailed)</strong> [veya yeni SPSS sürümlerinde <em>Two-Sided p</em>] değerine bakılır. Eğer p &lt; 0.05 ise, iki grup ortalaması arasında istatistiksel olarak anlamlı (significant) bir fark olduğu sonucuna varılır. Hangi grubun daha yüksek olduğunu anlamak için <em>Group Statistics</em> tablosundaki ortalama (Mean) değerlere bakılır.</li>
</ul>

<h2>Adım Adım Bağımlı Örneklem t-Testi (Paired Samples)</h2>
<h3>SPSS Uygulama Adımları</h3>
<ol>
  <li>Üst menüden <code>Analyze &gt; Compare Means &gt; Paired-Samples T Test...</code> yolunu izleyin.</li>
  <li>Karşılaştırmak istediğiniz ilişkili iki değişkeni (örneğin; On_Test ve Son_Test) sol taraftaki listeden seçerek sağ taraftaki <code>Paired Variables</code> kutusuna <em>Variable 1</em> ve <em>Variable 2</em> eşleşmesi oluşturacak şekilde aktarın.</li>
  <li><code>OK</code> butonuna tıklayarak analizi başlatın.</li>
</ol>

<h3>Sonuçların Yorumlanması</h3>
<p>Analiz sonucunda doğrudan <strong>Paired Samples Test</strong> tablosuna bakılır. <strong>Sig. (2-tailed)</strong> değeri 0.05'ten küçükse (p &lt; 0.05), iki ölçüm (ön test ve son test) arasında istatistiksel olarak anlamlı bir farklılık olduğu yorumu yapılır.</p>

<h2>Sonuçların APA Formatında Raporlanması</h2>
<p>t-testi bulgularını raporlarken grupların ortalamalarını (M), standart sapmalarını (SD), t-testi istatistik değerini (t), serbestlik derecesini (df) ve anlamlılık düzeyini (p) okuyucuya sunmanız beklenir.</p>

<p><em>"Bağımsız örneklem t-testi sonuçlarına göre, kadın öğrencilerin problem çözme becerisi puanları (M = 82.4, SD = 10.5) ile erkek öğrencilerin puanları (M = 76.1, SD = 12.3) arasında kadın öğrenciler lehine istatistiksel olarak anlamlı bir fark bulunmuştur, t(98) = 2.74, p = .007."</em></p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Pallant, J. (2020). SPSS survival manual: A step by step guide to data analysis using IBM SPSS (7th ed.). Routledge.<br>
Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). Sage.<br>
Büyüköztürk, Ş. (2018). Sosyal Bilimler İçin Veri Analizi El Kitabı (24. Baskı). Pegem Akademi.
</small>"""

    BlogPost.objects.get_or_create(
        slug='spsste-t-testi-adim-adim-bagimsiz-ve-bagimli-orneklem-karsilastirmasi',
        defaults={
            'title': "SPSS'te t-Testi Adım Adım: Bağımsız ve Bağımlı Örneklem Karşılaştırması",
            'excerpt': 'Tez analizlerinde sıkça kullanılan bağımsız ve bağımlı örneklem t-testlerinin SPSS programında nasıl yapıldığını, varsayımlarını ve sonuçların APA formatında nasıl yorumlanıp raporlanacağını örneklerle öğrenin.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0079_blog_normallik_testi_sonuclari_nasil_yorumlanir'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]