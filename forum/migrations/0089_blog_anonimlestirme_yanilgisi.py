# forum/migrations/0089_blog_anonimlestirme_yanilgisi.py

from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='veri-guvenligi-etik',
        defaults={'name': 'Veri Güvenliği & Etik'}
    )

    content = """<h2>Anonimleştirme Gerçekten İşe Yarıyor mu?</h2>
<p>Araştırmacılar, kurumlar ve şirketler veri paylaşırken kimlikleri gizlediklerini iddia ederek verileri "anonim" hale getirdiklerini söylerler. Genellikle isim, TC kimlik numarası veya telefon numarası gibi doğrudan tanımlayıcıların (direct identifiers) silinmesi yeterli görülür. Ancak modern veri bilimi, bu "isimsiz" veri setlerinin sandığımız kadar gizli olmadığını kanıtlamıştır.</p>

<h2>De-anonimleştirme (Re-identification) Nedir?</h2>
<p>De-anonimleştirme, sözde anonim hale getirilmiş bir veri setindeki kişilerin kimliklerinin, veri setindeki diğer dolaylı tanımlayıcılar (yaş, cinsiyet, posta kodu, meslek) ile farklı bir dış veri setinin (örneğin seçmen kayıtları) eşleştirilmesi (linkage attack) sonucu yeniden açığa çıkarılmasıdır.</p>

<h3>Tarihe Geçen Skandallar</h3>
<ul>
  <li><strong>Netflix Prize Davası:</strong> Netflix, film öneri algoritmasını geliştirmek için yarışmacılara "anonimleştirilmiş" bir izleme geçmişi veri seti sundu. Araştırmacılar, bu veri setini IMDB'deki halka açık film oylama saatleriyle eşleştirerek Netflix kullanıcılarının gerçek kimliklerini ve hatta siyasi/cinsel eğilimlerini ortaya çıkardı.</li>
  <li><strong>Massachusetts Valisi Olayı:</strong> Eyalet, hastane kayıtlarını anonimleştirerek yayınladı. Ancak bir araştırmacı, hastane verilerindeki "doğum tarihi, cinsiyet ve posta kodu" üçlüsünü halka açık seçmen kütükleriyle eşleştirerek, doğrudan valinin tıbbi kayıtlarını masasına koymayı başardı.</li>
</ul>

<h2>Gerçek Anonimlik İçin Gelişmiş Teknikler</h2>
<p>Basit maskeleme yöntemleri yerine, veri gizliliğini matematiksel olarak garanti altına alan modern teknikler kullanılmalıdır:</p>
<ol>
  <li><strong>k-Anonymity (k-Anonimlik):</strong> Bir veri setindeki herhangi bir kişinin, aynı özellikleri taşıyan en az <em>k-1</em> diğer kişiden ayırt edilememesi prensibidir. Örneğin k=5 ise, veri setindeki herhangi bir kişi, gruptaki diğer 4 kişiyle tamamen aynı demografik özelliklere sahiptir.</li>
  <li><strong>l-Diversity ve t-Closeness:</strong> k-Anonimliğin yetersiz kaldığı durumlar (hassas verilerin homojen olması vb.) için geliştirilmiş, grup içindeki hassas niteliklerin çeşitliliğini zorunlu kılan ileri düzey yöntemlerdir.</li>
  <li><strong>Differential Privacy (Diferansiyel Gizlilik):</strong> Veri tabanına kasıtlı olarak istatistiksel bir "gürültü" (noise) ekleyerek, genel veri analizinin doğruluğunu korurken herhangi bir bireyin o veri tabanında olup olmadığının anlaşılmasını imkansız hale getirir. Apple ve Google günümüzde bu yöntemi sıkça kullanmaktadır.</li>
</ol>
<hr>
<small>
<strong>Kaynakça:</strong><br>
Sweeney, L. (2002). k-anonymity: A model for protecting privacy. International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems, 10(05), 557-570.<br>
Narayanan, A., &amp; Shmatikov, V. (2008). Robust de-anonymization of large sparse datasets. 2008 IEEE Symposium on Security and Privacy (sp 2008), 111-125.<br>
Dwork, C. (2008). Differential privacy: A survey of results. International conference on theory and applications of models of computation.
</small>"""

    BlogPost.objects.get_or_create(
        slug='anonimlestirme-yanilgisi-isimsiz-veri-setlerinden-kimlik-yeniden-nasil-insa-ediliyor',
        defaults={
            'title': 'Anonimleştirme Yanılgısı: "İsimsiz" Veri Setlerinden Kimlik Yeniden Nasıl İnşa Ediliyor?',
            'excerpt': 'Veri setlerinden isimleri silmek anonimlik sağlamaz. De-anonimleştirme saldırılarını, Netflix skandalını ve veri gizliliğinde k-Anonymity ile Differential Privacy tekniklerini öğrenin.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0088_blog_tez_verilerini_google_driveda_tutmak'),
    ]

    operations = [
        migrations.RunPython(ekle, migrations.RunPython.noop),
    ]