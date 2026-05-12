# forum/migrations/0087_blog_veri_sahteliginden_veri_seffafligina.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='acik-bilim-arastirma-etigi',
        defaults={'name': 'Açık Bilim & Araştırma Etiği', 'icon': 'bi-eye', 'color': '#10b981'},
    )

    content = """<h2>Kara Kutudan Çıkmak: Neden Açık Bilime İhtiyacımız Var?</h2>
<p>Geleneksel akademik yayıncılık modelinde, araştırma süreci büyük bir "kara kutu" gibidir. Okuyucular ve hakemler, sadece yazarın makalesinde sunduğu özenle seçilmiş, temizlenmiş ve çoğu zaman anlamlı sonuçlar verecek şekilde filtrelenmiş analiz çıktılarını (pdf formatında) görürler. Ham verinin, analiz kodlarının (syntax) veya araştırma sorularının orijinal halinin paylaşılamaması; veri uydurma (fabrication), veri manipülasyonu (falsification) ve sadece işe yarayan kısımların raporlanması (selective reporting) gibi akademik ahlaksızlıklara zemin hazırlamıştır. İşte <strong>Açık Bilim (Open Science)</strong> hareketi, bu kapalı kapılar ardındaki bilimi şeffaflaştırmak için doğmuştur.</p>

<h2>Ön-Kayıt (Preregistration) Nedir?</h2>
<p>Açık bilimin en güçlü silahlarından biri ön-kayıt (preregistration) uygulamasıdır. Araştırmacı henüz veriyi toplamaya başlamadan önce; hipotezlerini, kullanacağı istatistiksel testleri ve örneklem büyüklüğünü belirler. Bunları <strong>OSF (Open Science Framework)</strong> veya <em>AsPredicted</em> gibi platformlara yükleyerek zaman damgasıyla dondurur (kaydeder). Bu sayede analiz aşamasında veriyle oynayıp hipotez değiştirme (HARKing - Hypothesizing After Results are Known) engellenmiş olur.</p>

<h2>FAIR İlkeleri ve Açık Veri (Open Data)</h2>
<p>Toplanan bilimsel verilerin başkaları tarafından incelenebilir veya tekrar analiz edilebilir olması için <strong>FAIR İlkeleri</strong> geliştirilmiştir. Veri şu özellikleri taşımalıdır:</p>
<ul>
  <li><strong>Findable (Bulunabilir):</strong> Veri seti dijital bir kimliğe (DOI vb.) sahip olmalıdır.</li>
  <li><strong>Accessible (Erişilebilir):</strong> Veriler standart protokollerle ücretsiz erişime açık olmalıdır.</li>
  <li><strong>Interoperable (Birlikte Çalışabilir):</strong> Veriler, farklı istatistik yazılımlarının okuyabileceği (örneğin .csv) ortak formatlarda tutulmalıdır.</li>
  <li><strong>Reusable (Yeniden Kullanılabilir):</strong> Verinin nasıl toplandığı ve değişkenlerin ne anlama geldiği (codebook) belgelenmiş olmalıdır.</li>
</ul>

<h2>Türkiye'de Açık Veri Mümkün mü? KVKK ve Engeller</h2>
<p>Küresel çapta Nature, Science ve APA gibi dev yayıncılar artık yazarlardan verilerini Mendeley Data, GitHub veya OSF gibi platformlara yüklemelerini zorunlu kılıyor. Ancak Türkiye'de durum biraz daha karmaşık.</p>
<p>Açık bilimin Türkiye akademisinde yaygınlaşmasının önündeki en büyük engeller şunlardır:</p>
<ol>
  <li><strong>Kişisel Verilerin Korunması Kanunu (KVKK) Endişesi:</strong> Araştırmacılar, toplanan anket veya mülakat verilerini paylaşmanın yasal bir suç oluşturacağından korkmaktadır. Oysa veriler <em>anonimleştirildiğinde (de-identification)</em> açık veri olarak paylaşılmalarında yasal bir sakınca yoktur.</li>
  <li><strong>"Verim Çalınır" Korkusu:</strong> Birçok akademisyen, büyük emeklerle topladığı veriyi yayınlamayı reddederek, o veriden yıllarca farklı farklı makaleler "sağmak" istemektedir.</li>
  <li><strong>Kurumsal Teşvik Eksikliği:</strong> Açık veri paylaşan veya ön-kayıt yapan araştırmacılara üniversiteler veya TÜBİTAK tarafından ek teşvik/puan sağlayan bir mekanizma henüz tam anlamıyla oturmamıştır.</li>
</ol>
<p>Bilimin güvenilirliğinin temel taşı şeffaflıktır. Veri paylaşımını bir "kayıp" değil, bilimin kümülatif doğasının bir gereği olarak görmek, yeni nesil araştırmacıların en önemli sorumluluğu olacaktır.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Munafò, M. R., Nosek, B. A., Bishop, D. V., Button, K. S., Chambers, C. D., Percie du Sert, N., ... &amp; Ioannidis, J. P. (2017). A manifesto for reproducible science. Nature Human Behaviour, 1(1), 0021.<br>
Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., ... &amp; Mons, B. (2016). The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data, 3, 160018.<br>
Nosek, B. A., Ebersole, C. R., DeHaven, A. C., &amp; Mellor, D. T. (2018). The preregistration revolution. Proceedings of the National Academy of Sciences, 115(11), 2600-2606.
</small>"""

    BlogPost.objects.get_or_create(
        slug='veri-sahteliginden-veri-seffafligina-open-science-hareketi-ve-turkiyede-acik-veri',
        defaults={
            'title': 'Veri Sahteliğinden Veri Şeffaflığına: Open Science Hareketi ve Türkiye\'de Açık Veri Mümkün mü?',
            'excerpt': 'Açık bilim (Open science) hareketinin yükselişi, preregistration, OSF platformları, FAIR veri ilkeleri ve KVKK gölgesinde Türkiye\'de açık veri paylaşımının zorlukları.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0086_blog_turkiyenin_akademik_uretimi'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]
