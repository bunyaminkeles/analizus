# forum/migrations/0086_blog_turkiyenin_akademik_uretimi.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='bibliometri-turkiyede-bilim',
        defaults={'name': "Bibliometri & Türkiye'de Bilim", 'icon': 'bi-graph-up', 'color': '#0ea5e9'},
    )

    content = """<h2>Türkiye Akademisinde Nicelik mi, Nitelik mi?</h2>
<p>Son yıllarda Türkiye yükseköğretim sisteminde üniversite sayısının hızla artması ve kadro/teşvik kriterlerinin revize edilmesiyle birlikte devasa bir akademik veri üretimi ortaya çıktı. Bibliometrik analizler, bir ülkenin bilimsel performansını, eğilimlerini ve dünya genelindeki konumunu anlamak için en güçlü araçlardan biridir. <strong>OpenAlex</strong> gibi açık bibliyografik veritabanları ve TÜBİTAK ULAKBİM bünyesindeki <strong>TR Dizin</strong> verileri incelendiğinde, Türkiye akademisinin 2020-2025 projeksiyonu çarpıcı gerçekleri gözler önüne seriyor.</p>

<h2>Veriler Ne Söylüyor? Sayısal Patlama ve Atıf Darboğazı</h2>
<p>YÖK ve diğer kurumların belirlediği niceliksel hedefler, Türkiye'deki araştırmacıları daha fazla makale üretmeye itti. Verilere göre Türkiye kökenli makale sayılarında her yıl istikrarlı bir yükseliş yaşanmakta. Ancak bu nicel büyüme, ne yazık ki nitel etkiye aynı oranda yansımıyor.</p>

<ul>
  <li><strong>Yayın Artışı:</strong> Sağlık bilimleri, mühendislik ve eğitim bilimleri önderliğinde Türkiye, dünyada en çok yayın üreten ilk 20 ülke arasındaki yerini sağlamlaştırmıştır.</li>
  <li><strong>Atıf (Etki) Sorunu:</strong> Üretilen makalelerin büyük bir bölümü ya hiç atıf almamakta ya da "kendine atıf (self-citation)" döngüsünde kalmaktadır. Gelişmiş ülkelerle kıyaslandığında Türkiye'nin "Makale Başına Düşen Atıf" ortalaması dünya ortalamasının altında seyretmektedir.</li>
  <li><strong>Q1/Q2 Dergilerdeki Pay:</strong> WOS (Web of Science) verilerine göre, kaliteli (Q1 ve Q2 çeyreklik dilimindeki) dergilerde yayımlanan Türkiye kökenli makalelerin oranı hala istenilen seviyeye ulaşamamıştır.</li>
</ul>

<h2>TR Dizin ve Ulusal Yayın Ekosistemi</h2>
<p>ULAKBİM tarafından yürütülen TR Dizin, ulusal dergilerin kalitesini artırmada kilit bir rol oynamaktadır. Son yıllarda yapılan doçentlik yönetmeliği değişikliklerinde TR Dizin indeksli makalelerin zorunlu tutulması, ulusal dergilere olan talebi patlatmıştır.</p>
<p>Ancak bu durum bazı sistemsel zorlukları da beraberinde getirdi:</p>
<ol>
  <li>Dergilerde yığılmalar yaşanmakta ve makale değerlendirme (hakemlik) süreçleri aylar, hatta yıllar sürmektedir.</li>
  <li>Hakem bulma krizi yaşanmakta, nicelik baskısı yüzünden bilimsel hakemliğin kalitesi tartışmaya açılmaktadır.</li>
  <li>Ulusal dergilerin İngilizce dilindeki yayın oranlarını artırarak bölgesel bir indeks olmaktan çıkıp uluslararası görünürlüğünü (OpenAlex, Scopus vb. platformlarda) artırması gerekmektedir.</li>
</ol>

<h2>Gelecek İçin Bilim Politikası Önerileri</h2>
<p>2025 ve sonrası için Türkiye'nin bilimsel üretim rotası "daha çok yayın" vizyonundan "daha etkili (high-impact) yayın" vizyonuna dönmelidir. Çok disiplinli uluslararası işbirlikleri (co-authorship) teşvik edilmeli, projeler makale sayısına göre değil, patent, teknolojik inovasyon veya toplumsal fayda çıktılarına göre değerlendirilmelidir.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Priem, J., Piwowar, H., &amp; Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv preprint arXiv:2205.01205.<br>
TÜBİTAK ULAKBİM. (2023). TR Dizin Değerlendirme Kriterleri ve İstatistikleri.<br>
YÖK (Yükseköğretim Kurulu). Üniversite İzleme ve Değerlendirme Genel Raporları.
</small>"""

    BlogPost.objects.get_or_create(
        slug='turkiyenin-akademik-uretimi-nereye-gidiyor-openalex-ve-tr-dizin-verileriyle',
        defaults={
            'title': 'Türkiye\'nin Akademik Üretimi Nereye Gidiyor? OpenAlex ve TR Dizin Verileriyle 2020-2025 Bibliometrik Manzara',
            'excerpt': 'Türkiye akademisinin son yıllardaki yayın haritası, atıf sorunları, nicelik-nitelik tartışmaları ve TR Dizin’in ulusal bilim yayıncılığındaki rolü üzerine detaylı bir bibliometrik analiz.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0085_blog_yayinla_ya_da_yok_ol_caginda'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]
