# forum/migrations/0083_blog_chatgpty_e_tezini_yazdirmak.py

from django.db import migrations

def create_blog_post(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='akademik-etik-ai',
        defaults={'name': 'Akademik Etik & AI', 'icon': 'bi-robot', 'color': '#8b5cf6'},
    )

    content = """<h2>Yapay Zeka Çağında "Yazarlık" Ne Anlama Geliyor?</h2>
<p>OpenAI'nin ChatGPT'yi piyasaya sürmesiyle birlikte akademik dünyada sismik bir sarsıntı yaşandı. Öğrencilerin ve hatta köklü araştırmacıların üretken yapay zeka (GenAI) araçlarını araştırma süreçlerine entegre etmesi, <strong>"akademik yazarlık (authorship)"</strong> kavramının temelden sarsılmasına neden oldu. Peki, literatür taramasını AI'a yaptırmak, metodolojiyi ona yazdırmak veya veriyi ona yorumlatmak sadece yeni bir asistan kullanmak mıdır, yoksa akademik intihalin dijital formata bürünmüş hali midir?</p>

<h2>COPE ve Akademik Yayıncılarda Yapay Zeka Etiği</h2>
<p>Yayın Etiği Komitesi (COPE), yapay zeka araçlarının yazar olarak kabul edilip edilemeyeceğine dair net bir duruş sergilemiştir. COPE rehberine göre <strong>ChatGPT veya herhangi bir büyük dil modeli (LLM), yazar olarak listelenemez.</strong> Bunun temel nedeni, bir makalede yazar olmanın yasal sorumluluk, etik hesap verebilirlik ve telif hakkı gibi insan doğasına ait yükümlülükler gerektirmesidir.</p>
<p>Bu bağlamda Elsevier, Springer Nature ve Taylor & Francis gibi büyük yayıncılar da politikalarını hızla güncelledi. Bu politikalara göre:</p>
<ul>
  <li>Yapay zeka araçları metin iyileştirme veya dilbilgisi düzeltme amacıyla kullanılabilir.</li>
  <li>Ancak fikir üretimi, veri analizi sonuçlarının yorumlanması veya doğrudan metin bloklarının kopyalanarak yapıştırılması kesinlikle ihlal sayılır.</li>
  <li>Makalenin yöntem veya teşekkür (acknowledgements) kısmında AI araçlarının nasıl ve ne amaçla kullanıldığı şeffaf bir şekilde bildirilmelidir.</li>
</ul>

<h2>Bilim Felsefesi Açısından Yapay Zeka ve Orijinallik</h2>
<p>Bilimsel bilginin üretimi sadece veri toplamak ve bunları kağıda dökmek değildir; aynı zamanda kavramsal bir sentez yapma, argüman inşa etme ve eleştirel düşünme sürecidir. Bir tezin veya makalenin bölümlerini tamamen bir yapay zekaya yazdırmak, araştırmacıyı "bilgi üreten" konumundan çıkarıp "bilgi derleyen" veya "editör" konumuna indirger.</p>
<p>Ayrıca, büyük dil modellerinin eğitim verilerinde yer alan <strong>halüsinasyon (hallucination)</strong> problemi, bilimsel doğruluğu ciddi şekilde tehdit etmektedir. Var olmayan referansların üretilmesi veya sahte metodolojik gerekçelerin sunulması, akademinin temel direği olan güvenilirliği aşındırır.</p>

<h2>Gelecekte Bizi Neler Bekliyor?</h2>
<p>Akademide yapay zekayı tamamen yasaklamanın uygulanabilir olmadığı açıktır. Bunun yerine "AI-Destekli Araştırma" ile "AI-Tarafından Üretilen Araştırma" arasındaki ince çizgiyi çizen etik yönergeler ve AI tespit araçları (Turnitin AI detector vb.) ön plana çıkacaktır. Akademisyenlerin ve doktora öğrencilerinin bu teknolojik evrime direnmesi değil, onu <em>şeffaf ve sorumlu bir şekilde</em> kullanmayı öğrenmesi gerekmektedir.</p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
COPE Council. (2023). Authorship and AI tools. Committee on Publication Ethics.<br>
Hosseini, M., Resnik, D. B., &amp; Holmes, K. (2023). The ethics of disclosing the use of artificial intelligence tools in writing scholarly manuscripts. Research Ethics.<br>
Thorp, H. H. (2023). ChatGPT is fun, but not an author. Science, 379(6630), 313.
</small>"""

    BlogPost.objects.get_or_create(
        slug='chatgpty-e-tezini-yazdirmak-bilim-midir-yoksa-akademinin-olum-sertifikasi-mi',
        defaults={
            'title': 'ChatGPT\'ye Tezini Yazdırmak Bilim midir, Yoksa Akademinin Ölüm Sertifikası mı? — Yapay Zeka Çağında "Yazarlık" Tartışması',
            'excerpt': 'Üretken yapay zekanın akademideki yükselişi, yazar olmanın ne anlama geldiğini yeniden tanımlıyor. COPE rehberleri, intihal tartışmaları ve bilim felsefesi ekseninde ChatGPT ve yapay zeka etiği.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0082_blog_tezde_yapilan_en_sik_10_istatistik_hatasi'),
    ]

    operations = [
        migrations.RunPython(create_blog_post, migrations.RunPython.noop),
    ]
