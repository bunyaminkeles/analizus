# forum/migrations/0085_blog_yayinla_ya_da_yok_ol_caginda.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='akademik-kariyer-etik',
        defaults={'name': 'Akademik Kariyer & Etik', 'icon': 'bi-briefcase', 'color': '#ef4444'},
    )

    content = """<h2>"Yayınla ya da Yok Ol" (Publish or Perish) Kültürü</h2>
<p>Günümüz akademik dünyasında, araştırmacıların değeri büyük ölçüde ürettikleri makale sayısı ve aldıkları atıflarla ölçülmektedir. Akademik teşvikler, doçentlik atamaları, proje fonları ve hatta kadroda kalabilmek gibi son derece hayati meselelerin salt nicel (kantitatif) performans kriterlerine bağlanması, akademide <strong>"Yayınla ya da Yok Ol"</strong> kültürünü doğurmuştur. Bu vahşi rekabet ortamı, bilimsel keşfin hazzını gölgede bırakırken, bilimsel etiği ciddi şekilde tehdit eden bazı karanlık uygulamaları da beraberinde getirdi.</p>

<h2>Predatory (Yağmacı) Dergiler ve Akademik İstismar</h2>
<p>Açık erişim (Open Access) hareketinin yozlaşmış bir versiyonu olan yağmacı dergiler, araştırmacılardan yüksek yayın ücretleri (Article Processing Charge - APC) talep edip, makaleleri hiçbir ciddi hakem değerlendirmesinden (peer-review) geçirmeden hızla yayınlayan platformlardır.</p>
<ul>
  <li><strong>Beall Listesi (Beall's List):</strong> Jeffrey Beall tarafından başlatılan ve yağmacı dergi ve yayıncıları ifşa eden bu liste, her ne kadar yasal baskılar sonucu orijinal haliyle kapanmış olsa da, hala akademik dünyanın en önemli gayri resmi filtrelerinden biri sayılmaktadır.</li>
  <li>Genç akademisyenler, doçentlik kriterlerini hızlıca sağlamak veya akademik teşvik puanı toplamak amacıyla bilerek veya bilmeyerek bu "para tuzağı" dergilerin ağına düşmektedir.</li>
</ul>

<h2>Citation Hacking, Atıf Kartelleri ve h-indeksi Fetişizmi</h2>
<p>Sadece makale yayımlamak da artık yeterli görülmüyor; bu makalelerin çokça atıf (citation) alması ve yazarın <strong>h-indeksi</strong> değerinin yüksek olması bekleniyor. Bu baskı, "İtibar Ekonomisi" olarak adlandırılan yeni bir kavram ortaya çıkardı.</p>
<p>Bu ekonominin karanlık yüzünde şunlar yer almaktadır:</p>
<ol>
  <li><strong>Atıf Kartelleri (Citation Rings):</strong> Bir grup akademisyenin kendi aralarında anlaşıp, makalelerinin içeriğinden bağımsız olarak birbirlerine karşılıklı ve yoğun atıf yapmalarıdır.</li>
  <li><strong>Zorlayıcı Atıflar (Coercive Citation):</strong> Bazı dergi editörlerinin veya hakemlerin, makalenin kabul edilmesi şartı olarak kendi çalışmalarına atıf yapılmasını dayatmasıdır. Bu, akademik gücün açık bir şekilde kötüye kullanılmasıdır.</li>
</ol>

<h2>Çözüm: Nicelikten Niteliğe Dönüş Mümkün mü?</h2>
<p>Avrupa ve Kuzey Amerika'daki birçok üniversite ve araştırma enstitüsü DORA (San Francisco Declaration on Research Assessment) gibi bildirgeleri imzalayarak, akademisyen değerlendirmelerinde sadece Dergi Etki Faktörü (Impact Factor) ve h-indeksi gibi metrikleri kullanmayı bırakacaklarını taahhüt ediyorlar. Makale sayısından ziyade bilime ve topluma yapılan <em>gerçek katkıların</em> ödüllendirileceği bir akademik değerlendirme sistemine geçiş yapmak, akademi için artık bir zorunluluk, bilimsel dürüstlük için bir ölüm-kalım meselesidir.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Beall, J. (2012). Predatory publishers are corrupting open access. Nature, 489(7415), 179.<br>
Brembs, B., Button, K., &amp; Munafò, M. R. (2013). Deep impact: unintended consequences of journal rank. Frontiers in Human Neuroscience, 7, 291.<br>
DORA (Declaration on Research Assessment). (2012). San Francisco Declaration on Research Assessment.
</small>"""

    BlogPost.objects.get_or_create(
        slug='yayinla-ya-da-yok-ol-caginda-akademisyenin-sessiz-intihari-predatory-dergiler',
        defaults={
            'title': '"Yayınla ya da Yok Ol" Çağında Akademisyenin Sessiz İntiharı: Predatory Dergiler, Citation Hacking ve İtibar Ekonomisi',
            'excerpt': 'Publish or perish baskısının akademide yarattığı yozlaşma, yağmacı (predatory) dergiler, atıf kartelleri, h-indeksi fetişizmi ve akademik itibar ekonomisinin perde arkası.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0084_blog_p_degeri_krizinin_100_yilinda'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]
