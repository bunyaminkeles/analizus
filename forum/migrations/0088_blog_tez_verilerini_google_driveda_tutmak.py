from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='veri-guvenligi-arastirma-etigi',
        defaults={'name': 'Veri Güvenliği & Araştırma Etiği'}
    )

    content = """<h2>Akademik Araştırmalarda Veri Güvenliği Neden Önemli?</h2>
<p>Tez veya makale hazırlarken toplanan anket, mülakat veya deney verilerinin saklanması, araştırmacıların en az önemsediği ancak en büyük risk taşıyan konulardan biridir. Birçok araştırmacı, kolaylığı nedeniyle verilerini kişisel Google Drive veya Dropbox hesaplarında saklamayı tercih eder. Ancak bu masum görünen alışkanlık, KVKK (Kişisel Verilerin Korunması Kanunu) ve GDPR (Avrupa Genel Veri Koruma Tüzüğü) kapsamında ciddi ihlallere yol açabilir.</p>

<h2>Google Drive'da Veri Tutmak Suç Mu?</h2>
<p>Doğrudan "suç" demek ağır bir tabir olsa da, eğer topladığınız veri <strong>kişisel veri</strong> (isim, TC kimlik no, e-posta, ses kaydı, IP adresi) veya <strong>özel nitelikli kişisel veri</strong> (sağlık bilgisi, siyasi görüş, sendika üyeliği) içeriyorsa, bu verileri yurtdışı tabanlı bulut sunucularında (Google Drive vb.) onay almadan saklamak KVKK'nın açık bir ihlalidir.</p>
<ul>
  <li>KVKK Madde 9'a göre, kişisel veriler ilgili kişinin açık rızası olmaksızın yurtdışına aktarılamaz. (Bulut sunucuları genellikle yurtdışındadır).</li>
  <li>Veri güvenliğini sağlamak için gerekli teknik ve idari tedbirleri almamak, yüksek idari para cezalarına sebep olabilir.</li>
</ul>

<h2>Araştırmacının "Veri Sorumlusu" Olarak Yükümlülükleri</h2>
<p>Tez çalışması yürütürken siz ve üniversiteniz yasal olarak "Veri Sorumlusu" (Data Controller) sayılırsınız. Veri sorumlusunun temel yükümlülükleri şunlardır:</p>
<ol>
  <li><strong>Aydınlatma Yükümlülüğü:</strong> Katılımcılara verilerin nerede, nasıl ve ne kadar süreyle saklanacağı açıkça bildirilmelidir.</li>
  <li><strong>Açık Rıza Alınması:</strong> Sadece anketin başına "kabul ediyorum" kutucuğu koymak yetmez; verinin buluta yükleneceği biliniyorsa buna özel rıza alınmalıdır.</li>
  <li><strong>Anonimleştirme:</strong> Elde edilen veriler, analiz aşamasına geçilmeden önce kimlik bilgilerinden arındırılmalı (de-identification) veya takma ad kullanılmalıdır (pseudonymisation).</li>
</ol>

<h2>Tez Verileri Nasıl Güvenle Saklanmalı?</h2>
<p>Araştırma verilerinizi güvende tutmak için aşağıdaki adımları izleyebilirsiniz:</p>
<ul>
  <li>Verileri üniversitenizin size sağladığı yerel (on-premise) sunucularda veya harici şifrelenmiş sabit disklerde saklayın.</li>
  <li>Mutlaka bulut kullanacaksanız, verileri diskinizde AES-256 gibi güçlü şifreleme yöntemleriyle (örneğin Veracrypt kullanarak) şifreledikten sonra buluta yükleyin.</li>
  <li>Etik kurul başvurunuzda verilerin nerede depolanacağını (örn: "şifreli harici disk") ve saklama süresi bitince nasıl imha edileceğini net bir şekilde belirtin.</li>
</ul>
<hr>
<small>
<strong>Kaynakça:</strong><br>
Kişisel Verileri Koruma Kurumu (KVKK). (2016). 6698 Sayılı Kişisel Verilerin Korunması Kanunu.<br>
Avrupa Birliği Veri Koruma Tüzüğü (GDPR). (2018). General Data Protection Regulation.<br>
Borgman, C. L. (2015). Big data, little data, no data: Scholarship in the networked world. MIT press.
</small>"""

    BlogPost.objects.get_or_create(
        slug='tez-verilerini-google-driveda-tutmak-suc-mu-kvkk-gdpr',
        defaults={
            'title': 'Tez Verilerini Google Drive\'da Tutmak Suç mu? KVKK, GDPR ve Akademisyenin Bilmediği Veri Sorumlulukları',
            'excerpt': 'Akademik araştırmalarda kişisel verileri Google Drive gibi bulut sistemlerinde saklamanın yasal risklerini, KVKK/GDPR yükümlülüklerini ve veri güvenliğini nasıl sağlayacağınızı inceliyoruz.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0087_blog_veri_sahteliginden_veri_seffafligina'),
    ]

    operations = [
        migrations.RunPython(ekle, migrations.RunPython.noop),
    ]