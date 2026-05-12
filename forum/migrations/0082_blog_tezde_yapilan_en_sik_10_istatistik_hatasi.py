# forum/migrations/0082_blog_tezde_yapilan_en_sik_10_istatistik_hatasi.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='tez-sureci',
        defaults={'name': 'Tez Süreci', 'icon': 'bi-mortarboard', 'color': '#6366f1'},
    )

    content = """<h2>İstatistiksel Hatalar Neden Önemlidir?</h2>
<p>Tez veya makale yazım sürecinde toplanan verilerin doğru analiz edilmesi, araştırmanın geçerliliği ve güvenilirliği açısından kritik bir öneme sahiptir. Yanlış uygulanan istatistiksel testler veya bulguların hatalı yorumlanması, aylar süren emeklerin heba olmasına ve jüri aşamasında tezinizin reddedilmesine yol açabilir. Araştırmacıların veri analizi aşamasında sıklıkla düştüğü hataları bilmek, bu tuzaklardan kaçınmanızı sağlayacaktır.</p>

<h2>Tezlerde En Sık Karşılaşılan 10 İstatistiksel Hata</h2>

<ol>
  <li><strong>Test Varsayımlarını (Assumptions) Göz Ardı Etmek</strong>
    <p>Her istatistiksel testin belirli ön şartları (varsayımları) vardır. Parametrik testler (T-testi, ANOVA vb.) genellikle verilerin normal dağılmasını ve varyansların homojenliğini gerektirir. Normallik testi (Shapiro-Wilk veya Kolmogorov-Smirnov) yapmadan doğrudan analizlere geçmek, en yaygın ve en tehlikeli hataların başında gelir.</p>
  </li>
  
  <li><strong>p-değerini (Anlamlılık) Yanlış Yorumlamak</strong>
    <p>Araştırmacıların düştüğü en büyük yanılgılardan biri, p-değerinin etkinin büyüklüğünü gösterdiğini sanmalarıdır. <em>p &lt; 0.05</em> sadece "istatistiksel olarak anlamlı bir fark var" demektir; farkın pratik hayatta ne kadar önemli veya büyük olduğunu göstermez. Bunun için mutlaka Etki Büyüklüğü (Effect Size - örneğin Cohen's d veya Eta-kare) raporlanmalıdır.</p>
  </li>

  <li><strong>Korelasyon ile Nedenselliği Birbirine Karıştırmak</strong>
    <p>Korelasyon analizi iki değişken arasındaki ilişkinin yönünü ve gücünü gösterir, ancak <strong>sebep-sonuç ilişkisi kanıtlamaz</strong>. "A değişkeni arttıkça B değişkeni de artıyor" demek, A'nın B'ye sebep olduğu anlamına gelmez. Nedensellik iddiası için deneysel tasarımlara ihtiyaç vardır.</p>
  </li>

  <li><strong>Anlamlı Sonuç Bulana Kadar Test Yapmak (P-Hacking)</strong>
    <p>Hipotezleri doğrulamak için verileri tekrar tekrar kırparak, farklı testler deneyerek veya sürekli değişken çıkarıp ekleyerek "zorla" p &lt; 0.05 bulmaya çalışmak etik bir ihlaldir ve akademik camiada "P-Hacking" olarak bilinir.</p>
  </li>

  <li><strong>Aykırı Değerleri (Outliers) Sadece Testi Bozduğu İçin Çıkarmak</strong>
    <p>Veri setindeki uç değerlerin, veriyi bozduğu veya analizleri anlamsız kıldığı için hiçbir mantıklı açıklama yapılmadan (örneğin veri giriş hatası olmadığı halde) silinmesi büyük bir hatadır. Uç değerlerin araştırmanın doğasından kaynaklanıp kaynaklanmadığı incelenmelidir.</p>
  </li>

  <li><strong>Yetersiz Örneklem Büyüklüğü ile Çalışmak</strong>
    <p>İstatistiksel testlerin bir "gücü" (statistical power) vardır. Çok küçük örneklemlerle yapılan çalışmalarda, gerçekte var olan bir farkı veya ilişkiyi tespit etmek imkansızlaşabilir. Araştırmaya başlamadan önce G*Power gibi programlarla minimum örneklem büyüklüğü (Power Analysis) hesaplanmalıdır.</p>
  </li>

  <li><strong>Bağımlı ve Bağımsız Verileri Karıştırmak</strong>
    <p>Aynı katılımcılardan alınan ön-test ve son-test gibi ilişkili ölçümlerde "Bağımsız Örneklem T-testi" kullanmak sık yapılan bir tasarımsal hatadır. Aynı kişilerden alınan tekrarlı ölçümlerde mutlaka "Bağımlı (Paired) Örneklem" testleri kullanılmalıdır.</p>
  </li>

  <li><strong>Ordinal (Sıralı) Verilere Sürekli Veri Muamelesi Yapmak</strong>
    <p>Eğitim durumu (İlkokul, Lise, Üniversite) gibi sıralı değişkenlerin aritmetik ortalamasını almak mantıklı değildir. Bu tür değişkenlerde ortalama yerine medyan (ortanca) raporlanmalı ve analizlerde parametrik olmayan (non-parametrik) testler tercih edilmelidir.</p>
  </li>

  <li><strong>Eksik (Missing) Verileri Yanlış Yönetmek</strong>
    <p>Anketlerde boş bırakılan soruların (eksik verilerin) SPSS'te "0" veya ortalama bir değer atanarak doğrudan doldurulması sonuçları saptırır. Eksik verilerin mekanizması incelenmeli (MCAR, MAR vb.) ve uygun atama yöntemleri (Multiple Imputation vb.) kullanılmalıdır.</p>
  </li>

  <li><strong>Sonuçları Eksik Raporlamak</strong>
    <p>Sadece <em>"Fark anlamlı bulunmuştur (p=0.03)"</em> diyerek cümleyi bitirmek APA formatına aykırıdır. Hangi grubun lehine bir fark olduğunu göstermek için grup ortalamaları, standart sapmalar, serbestlik derecesi ve test istatistik değerleri (t, F, r vb.) eksiksiz verilmelidir.</p>
  </li>
</ol>

<h2>Bu Hatalar Nasıl Önlenir?</h2>
<p>Veri toplama aşamasına geçmeden önce analiz planınızı detaylıca yapmalısınız. Tezinizin kurgusunu oluştururken mutlaka alanında uzman bir istatistikçiden veya tecrübeli danışmanlardan metodolojik destek almak, hataların veri toplandıktan sonra fark edilmesi gibi geri dönülemez sorunların önüne geçecektir.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Field, A. (2018). Discovering Statistics Using IBM SPSS Statistics (5th ed.). Sage Publications.<br>
Hair, J. F., Black, W. C., Babin, B. J., &amp; Anderson, R. E. (2010). Multivariate Data Analysis (7th ed.). Pearson.<br>
Wasserstein, R. L., &amp; Lazar, N. A. (2016). The ASA's Statement on p-Values: Context, Process, and Purpose. The American Statistician, 70(2), 129-133.
</small>"""

    BlogPost.objects.get_or_create(
        slug='tezde-yapilan-en-sik-10-istatistik-hatasi-ve-nasil-onlenir',
        defaults={
            'title': 'Tezde Yapılan En Sık 10 İstatistik Hatası ve Nasıl Önlenir?',
            'excerpt': 'Tez ve makale yazım sürecinde öğrencilerin ve araştırmacıların istatistiksel analizlerde en çok düştüğü 10 yaygın hata, p-değeri yanılgıları, varsayım ihlalleri ve bunları önleme yolları.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0081_blog_acimlayici_dogrulayici_faktor_analizi'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]