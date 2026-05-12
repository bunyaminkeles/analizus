# forum/migrations/0084_blog_p_degeri_krizinin_100_yilinda.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='bilim-felsefesi-metodoloji',
        defaults={'name': 'Bilim Felsefesi & Metodoloji', 'icon': 'bi-infinity', 'color': '#f59e0b'},
    )

    content = """<h2>p-Değeri Diktatörlüğü: Bilimsel Gerçeklik mi, İstatistiksel Yanılgı mı?</h2>
<p>Ronald Fisher'ın 1920'lerde istatistiksel analizlere kazandırdığı <strong>p-değeri (p-value)</strong>, aradan geçen 100 yılda akademik yayıncılığın en büyük putu haline geldi. Bugün pek çok araştırmacı, yüksek lisans tezlerinden prestijli makale başvurularına kadar her çalışmada "kutsal" <code>p &lt; 0.05</code> sınırını aşabilmek için amansız bir mücadele veriyor. Peki istatistiksel anlamlılık, gerçekten bilimsel anlamlılık ile eşdeğer mi?</p>

<h2>2016 ASA Bildirisi ve Paradigmada Çatlak</h2>
<p>Amerikan İstatistik Derneği (ASA), 2016 yılında bilim tarihinde nadir görülen bir adım atarak p-değerinin kullanımı üzerine resmi bir bildiri yayınladı. Bildirinin özü şuydu: <strong>p-değeri tek başına bir sonucun bilimsel önemini, pratik değerini veya bir hipotezin doğruluğunu kanıtlayamaz.</strong></p>
<p>Bu açıklamanın temel sebepleri şunlardı:</p>
<ol>
  <li>p-değeri araştırmanın sadece <em>boş hipoteze (null hypothesis) ne kadar zıt olduğunu</em> gösterir; araştırmacının kendi hipotezinin (H1) ne kadar doğru olduğunu göstermez.</li>
  <li>Çok büyük örneklemlerde en önemsiz, minicik farklar bile istatistiksel olarak anlamlı (p &lt; 0.05) çıkabilir.</li>
  <li>0.05 eşiği tamamen keyfi ve tarihsel bir kabule dayanır. p = 0.049 ile p = 0.051 arasındaki bilimsel gerçeklikte aslında hiçbir uçurum yoktur.</li>
</ol>

<h2>Replikasyon Krizi: Psikoloji ve Tıbbın Yüzleşmesi</h2>
<p>İstatistiksel anlamlılığa bu körü körüne bağlılık, bilim dünyasında günümüzde <strong>Replikasyon Krizi (Replication Crisis)</strong> olarak bilinen büyük bir skandalı doğurdu. 2010'lu yılların ortalarında, özellikle psikoloji ve tıp alanında daha önce saygın dergilerde yayınlanmış (ve p &lt; 0.05 çıkmış) yüzlerce çalışmanın yeniden tekrarlandığında aynı sonuçları vermediği ortaya çıktı. Araştırmacılar, anlamlı sonuç bulmak uğruna veriyi manipüle etme (p-hacking) veya sadece anlamlı sonuçları yayınlama (publication bias) gibi etik sorunlarla yüzleşmek zorunda kaldı.</p>

<h2>Çözüm Ne? Etki Büyüklüğü ve Bayesyen Yaklaşım</h2>
<p>Bilim felsefecileri ve metodologlar, sadece p-değerine bakarak bilim yapma devrinin kapanması gerektiğini savunuyor. Yeni dönemdeki standartlar şu şekilde evriliyor:</p>
<ul>
  <li><strong>Etki Büyüklüğü (Effect Size) ve Güven Aralıkları (Confidence Intervals):</strong> Artık farkın sadece "var" olduğunu söylemek yetmiyor, "ne kadar büyük" olduğunu (Cohen's d, Eta-squared) raporlamak zorunlu hale geliyor.</li>
  <li><strong>Bayesyen İstatistik:</strong> Sadece verinin modele uyumunu test eden Frekansçı (Frequentist) yaklaşımın ötesine geçerek, öncelikli inançlarımızı (prior) eldeki veriyle güncelleyerek (posterior) doğrudan hipotezlerin olasılığını hesaplayan Bayesyen yaklaşımlar popülerlik kazanıyor.</li>
</ul>
<p>Sonuç olarak, p-değeri bilimsel süreci tamamen yönlendiren bir yargıç değil, yalnızca elimizdeki veriye dair küçük bir ipucu veren bir dedektif olarak görülmelidir.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Wasserstein, R. L., &amp; Lazar, N. A. (2016). The ASA statement on p-values: context, process, and purpose. The American Statistician, 70(2), 129-133.<br>
Nuzzo, R. (2014). Scientific method: statistical errors. Nature News, 506(7487), 150.<br>
Cumming, G. (2014). The new statistics: Why and how. Psychological Science, 25(1), 7-29.
</small>"""

    BlogPost.objects.get_or_create(
        slug='p-degeri-krizinin-100-yilinda-istatistiksel-anlamlilik-bilimi-yanlis-mi-yonlendirdi',
        defaults={
            'title': 'P-Değeri Krizinin 100. Yılında: İstatistiksel Anlamlılık Bilimi Yanlış mı Yönlendirdi?',
            'excerpt': 'Amerikan İstatistik Derneğinin (ASA) bildirisi, replikasyon krizi ve Ronald Fisher’ın mirası ekseninde p-değeri fetişizmini ve bilim felsefesindeki istatistiksel devrimi tartışıyoruz.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0083_blog_chatgpty_e_tezini_yazdirmak'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]
