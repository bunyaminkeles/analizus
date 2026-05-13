# forum/migrations/0090_blog_saglikta_veri_krizi.py

from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='saglik-verisi-bilim-politikasi',
        defaults={'name': 'Sağlık Verisi & Bilim Politikası'}
    )

    content = """<h2>e-Nabız Var, Veri Yok: Türkiye'nin Sağlık İstatistiği Paradoksu</h2>
<p>Türkiye, "e-Nabız" gibi dünyanın en kapsamlı ve gelişmiş merkezi sağlık veri sistemlerinden birine sahip olmasına rağmen, iş bu verilerin bilimsel araştırmalara entegre edilmesine geldiğinde büyük bir kriz yaşıyor. Akademik araştırmalarda epidemiyolojik veriye ulaşmak, bir hekimin veya halk sağlığı uzmanının önündeki en büyük bürokratik engellerden biri haline gelmiş durumda.</p>

<h2>Klinik Veriler Neden Paylaşılamıyor?</h2>
<p>Birçok gelişmiş ülkede (örneğin Birleşik Krallık'taki UK Biobank veya ABD'deki SEER veritabanı), hastanelerden elde edilen anonimleştirilmiş devasa sağlık verileri açık erişimle (veya katı denetimlerle) araştırmacılara sunulmaktadır. Ancak Türkiye'de durum farklıdır:</p>
<ul>
  <li><strong>Aşırı Merkeziyetçilik:</strong> Sağlık verisi devletin tekelindedir. Araştırmacıların bu büyük veri havuzundan anonimleştirilmiş alt setleri talep etmesi için standart, şeffaf ve hızlı bir başvuru/onay portalı bulunmamaktadır.</li>
  <li><strong>Etik Kurul vs. Kurum İzni Çıkmazı:</strong> Sadece geriye dönük (retrospektif) bir dosya taraması yapmak için bile etik kurul onayı alındıktan sonra, ayrıca il sağlık müdürlüklerinden ve başhekimliklerden "kurum izni" alınması gerekmekte, bu süreç aylarca sürmektedir.</li>
  <li><strong>TÜİK'in Yetersiz Veri Dağılımı:</strong> Ölüm nedenleri ve hastalık prevalans istatistikleri, TÜİK (Türkiye İstatistik Kurumu) tarafından makro düzeyde ve çoğu zaman gecikmeli açıklanmaktadır. Araştırmacıların bölgesel veya demografik kırılımlarda mikro-veri talepleri genellikle cevapsız kalmaktadır.</li>
</ul>

<h2>Açık Sağlık Verisi Bilime Ne Kazandırır?</h2>
<p>Verinin kapalı kapılar ardında tutulması, ülkenin bilimsel potansiyelini felç etmektedir. Oysa anonimleştirilmiş sağlık verisinin (Open Health Data) ulusal bir protokol çerçevesinde akademiyle paylaşılması şunları sağlar:</p>
<ol>
  <li><strong>Kanıta Dayalı Tıp (EBM) Gelişir:</strong> Kendi toplumumuza ait gerçek dünya verileriyle (Real-World Data) hastalık trendleri, tedavi başarı oranları ve yan etkiler çok daha doğru analiz edilebilir.</li>
  <li><strong>Yapay Zeka (AI) ve Makine Öğrenimi Hızlanır:</strong> Radyolojik görüntülerin veya patoloji raporlarının etiketlenmiş açık veri setleri haline getirilmesi, Türkiye menşeli medikal AI çözümlerinin geliştirilmesini sağlar.</li>
  <li><strong>Maliyet-Etkinlik Analizleri Yapılır:</strong> Sağlık ekonomisi araştırmacıları, hangi ilacın veya politikanın bütçeye ne kadar yük getirdiğini daha net hesaplayabilir.</li>
</ol>
<p>Özetle, kişisel verilerin korunması esastır; ancak bu koruma, bilimin ilerlemesini engelleyen bir sansür mekanizmasına dönüşmemelidir.</p>
<hr>
<small>
<strong>Kaynakça:</strong><br>
Topol, E. J. (2019). Deep medicine: how artificial intelligence can make healthcare human again. Basic Books.<br>
Murdoch, T. B., &amp; Detsky, A. S. (2013). The inevitable application of big data to health care. JAMA, 309(13), 1351-1352.<br>
Sağlık Bakanlığı. (2020). Türkiye Sağlık İstatistikleri Yıllığı.
</small>"""

    BlogPost.objects.get_or_create(
        slug='saglikta-veri-krizi-turkiyede-klinik-arastirmalarin-verisi-neden-hep-kayip',
        defaults={
            'title': 'Sağlıkta Veri Krizi: Türkiye\'de Klinik Araştırmaların Verisi Neden Hep "Kayıp"? — e-Nabız Çağında Açık Veri Sorunu',
            'excerpt': 'Merkezi veri sistemlerine rağmen Türkiye\'de klinik veri setlerine erişim neden bu kadar zor? Açık sağlık verisi eksikliğinin epidemiyoloji ve tıbbi araştırmalara vurduğu darbe.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0089_blog_anonimlestirme_yanilgisi'),
    ]

    operations = [
        migrations.RunPython(ekle, migrations.RunPython.noop),
    ]