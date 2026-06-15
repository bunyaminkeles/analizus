from django.db import migrations

# Her EXTRA_* değişkeni 150-200 kelimelik ek bölüm; <hr> öncesine eklenir.

EXTRA_6 = """
<h2>Yapay Zeka ile Etik Çalışmanın Geleceği</h2>
<p>Akademik yazının geleceği, yapay zekayı tamamen dışlamak ya da tamamen içselleştirmek arasında değil; araştırmacının özgün düşünsel katkısını merkeze alan <em>etik bir ortaklık modelinde</em> şekillenecektir. Bu modelde yapay zeka, dilbilgisi kontrolü, biçimlendirme önerileri ve hızlı literatür taraması gibi rutin görevlerde asistan konumunda kalırken; araştırma sorusunun belirlenmesi, bulguların yorumlanması, tartışmanın oluşturulması ve sonuçların savunulması tamamen araştırmacıya ait kalacaktır.</p>
<p>Bu ortaklığı şeffaflıkla raporlamak hem akademik bütünlüğü korumanın hem de AI teknolojisine duyulan güveni pekiştirmenin temelidir. Ulusal ve uluslararası üniversitelerin bu konuda netleşen yönetmelikler yayınlaması beklenmektedir; bu süreçte araştırmacıların beklenmek yerine proaktif biçimde etik standartları benimsemesi uzun vadeli akademik itibar açısından belirleyici olacaktır.</p>
"""

EXTRA_8 = """
<h2>Ölçüm Araçlarının Çeşitlenmesi: Altmetri ve Etki Metrikleri</h2>
<p>H-indeksi ve atıf sayısının ötesinde, akademik etkiyi çok boyutlu biçimde ölçen yeni araçlar giderek yaygınlaşmaktadır. <strong>Altmetri (Altmetrics)</strong>, bir yayının sosyal medyada, haber sitelerinde, politika belgelerinde ve Wikipedia'da ne kadar yer aldığını izleyen alternatif bir etki ölçüt ailesidir. Her makalenin yanında altmetri rozetleri artık birçok derginin web sayfasında görünmektedir. Bunun yanı sıra patent atıfları, politika belgelerine girme ve toplumsal etki raporları gibi göstergeler, DORA çerçevesinde akademisyenlerin değerlendirileceği yeni kriterlerin başında gelmektedir.</p>
<p>Bu çeşitlenme, özellikle sosyal bilimler ve sağlık bilimleri alanındaki araştırmacıların atıf dinamiklerinin farklı olduğu disiplinlerde niceliksel dezavantajlarını azaltma potansiyeli taşımaktadır. Araştırmacıların bu metrikleri takip etmesi ve kendi çalışmalarını çeşitli platformlarda görünür kılması, "yayınla ya da yok ol" baskısına karşı daha sağlıklı bir strateji oluşturabilir.</p>
"""

EXTRA_9 = """
<h2>Araştırmacı Kimliği ve ORCID'in Önemi</h2>
<p>Türkiye'nin akademik üretimini doğru ölçmenin önündeki pratik engellerden biri araştırmacı kimlik sorunudur. Aynı ismi taşıyan farklı araştırmacılar veya transkripsiyona bağlı imla farklılıkları, Türk araştırmacıların yayınlarının bibliyometrik veri tabanlarında dağınık görünmesine yol açmaktadır. <strong>ORCID (Open Researcher and Contributor ID)</strong>, araştırmacılara küresel ve benzersiz bir kimlik numarası atayarak bu sorunu çözer. ORCID kimliğini tüm yayınlarınıza, proje başvurularınıza ve dergi submisyonlarınıza eklemek, bibliyometrik profilinizin OpenAlex, Scopus ve WoS'ta tutarlı ve eksiksiz görünmesini sağlar. Türkiye'de ORCID kullanım oranının artırılması, ulusal akademik üretimin küresel ölçekte daha doğru temsil edilmesi için kritik bir politika önceliği olmalıdır.</p>
"""

EXTRA_11 = """
<h2>Araştırmacı için Veri Güvenliği Kontrol Listesi</h2>
<p>Tez sürecinde kişisel veri toplayan her araştırmacı aşağıdaki soruların yanıtını belgede tutmalıdır:</p>
<ul>
  <li>☐ Topladığım veri genel mi, yoksa özel nitelikli kişisel veri mı?</li>
  <li>☐ Katılımcılardan KVKK kapsamında aydınlatma ve rıza aldım mı?</li>
  <li>☐ Veriler şifreli depolama alanında mı tutuluyor?</li>
  <li>☐ Bulut kullanıyorsam sunucuların konumunu biliyor muyum?</li>
  <li>☐ Etik kurul başvurusunda veri saklama ve imha planı var mı?</li>
  <li>☐ Analiz sırasında kimlik bilgileri veriden ayrıştırıldı mı?</li>
</ul>
<p>Bu soruların tamamına "Evet" yanıtı verilebiliyorsa KVKK uyum riski minimumdur. Belirsizlik hissedilen maddelerde üniversitenizin Veri Koruma Sorumlusu'na (DPO) veya hukuk birimlerine danışmak en güvenli yaklaşımdır.</p>
"""

EXTRA_12 = """
<h2>Araştırma Etiği ve Anonimleştirme: Tezde Nasıl Belgelenir?</h2>
<p>Etik kurul başvurusunda ve tezin Yöntem bölümünde anonimleştirme prosedürü açıkça tanımlanmalıdır. Örnek metin: <em>"Katılımcılara ait isim, e-posta ve telefon gibi doğrudan tanımlayıcılar veri tabanından silinmiş; demografik bilgiler (yaş, meslek, eğitim) kategori aralıklarına dönüştürülmüştür. Elde edilen veri seti, herhangi bir dış veri seti ile eşleştirilerek bireysel kimliğin yeniden tespit edilemeyeceği düzeyde anonimleştirilmiştir."</em></p>
<p>Bu düzeyde bir belgeleme, hem etik kurulların hem de olası veri koruma denetimlerinin beklentilerini karşılar. Anonimleştirme sürecini adım adım belgeleyen bir protokol oluşturmak, özellikle sağlık verileri veya hassas sosyal konuları inceleyen araştırmalarda standart bir uygulama hâline gelmektedir. Veri koruma bilincinin akademik kültürün bir parçası olması, uzun vadede Türkiye'nin uluslararası araştırma iş birliklerindeki güvenilirliğini de güçlendirecektir.</p>
"""

EXTRA_13 = """
<h2>Araştırmacıların Savunuculuk Rolü</h2>
<p>Türkiye'de sağlık verisine erişim sorununu yalnızca kurumsal bir politika meselesi olarak değil, bireysel araştırmacıların aktif savunuculuk yapabileceği bir alan olarak görmek gerekir. Akademik dernekler, tıp fakülteleri ve bağımsız araştırma grupları, şeffaf veri paylaşım politikalarını birlikte savunabilir; uluslararası örnekleri (UK Biobank, Nordic registries) karar alıcılara somut model olarak sunabilir.</p>
<p>Kısa vadede ise araştırmacılar mevcut imkânlardan en iyi biçimde yararlanmalıdır: Sağlık Bakanlığı'nın yayımladığı istatistik yıllıkları ve TÜİK'in ADNKS (Adrese Dayalı Nüfus Kayıt Sistemi) verileri kısıtlı da olsa birer başlangıç noktasıdır. Uluslararası veri tabanlarındaki Türkiye odaklı çalışmalar, ulusal veritabanlarına alternatif karşılaştırmalı veri sağlayabilir. Araştırmacıların bu kısıtları yöntem bölümünde şeffaflıkla ifade etmesi, elde edilen bulguların genellenebilirlik sınırlarını net biçimde ortaya koyar.</p>
"""

EXTRA_14 = """
<h2>Survival Analizinin Sağlık Dışındaki Kullanım Alanları</h2>
<p>Survival analizi yalnızca tıbbi araştırmalarla sınırlı değildir; "zaman-içinde-olaya-kadar" yapısına sahip her araştırma sorusu bu yöntemi geçerli kılar. Sosyal bilimler ve yönetim çalışmalarında sık kullanılan örnekler:</p>
<ul>
  <li><strong>İşletme:</strong> Müşterilerin abonelikten çıkana kadar geçen süre (churn analysis); şirketlerin iflasa kadar yaşadıkları süre.</li>
  <li><strong>Eğitim:</strong> Öğrencilerin okul terk etmesine kadar geçen süre; bursun öğrenci başarısına etkisi.</li>
  <li><strong>Psikoloji:</strong> Terapi sonrası iyileşmenin kalıcılığı; depresif atağın nüksüne kadar geçen süre.</li>
  <li><strong>Mühendislik:</strong> Bir sistemin arıza göstermesine kadar geçen süre (güvenilirlik analizi).</li>
</ul>
<p>Bu çeşitlilik, survival analizinin sosyal bilimciler için de temel bir araç setine dâhil edilmesi gerektiğine işaret etmektedir. R'ın <em>survival</em> paketi ve Python'ın <em>lifelines</em> kütüphanesi bu analizleri sağlık dışı alanlarda da erişilebilir hale getirmektedir.</p>
"""

EXTRA_15 = """
<h2>Bağımsız Veri Doğrulamanın Önemi</h2>
<p>Enflasyon tartışmalarının özünde metodoloji şeffaflığı sorunu yatmaktadır. Resmi verinin güvenilirliğini artırmanın en etkili yolu, bağımsız araştırmacıların ve sivil inisiyatiflerin aynı yöntemi kullanarak verileri doğrulayabilmesidir. Bu açıdan TÜİK'in ham fiyat gözlem verilerini ve hesaplama algoritmalarını kamuoyuyla paylaşması, tartışmanın metodolojik temelde sürdürülmesini sağlayacak en önemli adımdır.</p>
<p>Akademik araştırmacılar için pratik öneri: Enflasyon verisini kullanırken her zaman hangi endeksin (manşet TÜFE, çekirdek enflasyon, ÜFE), hangi baz döneminin ve hangi kurumun yayımladığı verinin kullanıldığını açıkça belirtin. Farklı ölçüm yaklaşımlarına duyarlılık analizi yaparak bulgularınızın metodoloji seçimine ne ölçüde bağımlı olduğunu raporlamak, araştırmanızın sağlamlığını güçlendirir ve veri tartışmalarının ötesinde özgün bir bilimsel katkı sunar.</p>
"""

EXTRA_17 = """
<h2>Non-Parametrik Testlerde Güç ve Örneklem Büyüklüğü</h2>
<p>Non-parametrik testler, eşdeğer parametrik testlere göre genellikle daha az istatistiksel güce sahiptir; yani aynı örneklemde gerçek bir etkiyi tespit etme olasılıkları daha düşüktür. Bu fark genellikle %5–15 civarındadır: bağımsız t-testi için 100 kişi gereken bir araştırmada Mann-Whitney U testi için 110–115 kişi gerekebilir. Bu kayıp küçük görünse de sınırlı örneklemlerde önemli hâle gelir.</p>
<p>Araştırma tasarımı aşamasında normallik ihlali öngörülüyorsa bu farkı hesaba katarak örneklemi büyütmek metodolojik açıdan önerilir. Bunun yanı sıra, dönüşüm yöntemleri (log, karekök) ile verileri normal dağılıma yaklaştırmak mümkünse parametrik teste dönebilirsiniz; bu yaklaşım her zaman dönüşüm gerekçesinin tezde açıklanmasını gerektirir.</p>
"""

EXTRA_18 = """
<h2>Yanlış Test Seçiminin Sonuçları</h2>
<p>Araştırma tasarımına uymayan t-testi seçmek yalnızca p değerini değiştirmekle kalmaz; etki büyüklüğü tahminini ve güven aralıklarını da etkiler. Bağımlı tasarımda bağımsız t-testi uygulamak varyansı şişirerek gücü düşürür ve gerçek bir etkiyi gözden kaçırabilir. Tersine, bağımsız tasarımda bağımlı t-testi uygulamak (yani bireyler arasındaki eşleştirme bulunmadığı hâlde çiftler oluşturmak) analizi temelden geçersiz kılar. Bu nedenle veri toplama aşaması tamamlanmadan tasarımın bağımsız mı bağımlı mı olduğunu kesin biçimde belirleyip veri girişini buna göre yapmak kritik bir ön adımdır.</p>
"""

EXTRA_20 = """
<h2>Çok Kategorili Bağımlı Değişken: Multinomial Lojistik Regresyon</h2>
<p>Bağımlı değişkeniniz ikiden fazla kategoriye sahipse (örneğin "Düşük / Orta / Yüksek" veya "A / B / C / D") ikili lojistik regresyon yetersiz kalır. Bu durumda <strong>Multinomial Lojistik Regresyon</strong> kullanılır. SPSS'te: Analyze → Regression → Multinomial Logistic. Model, her kategoriyi referans kategorisiyle karşılaştıran log-odds oranları üretir. Bağımlı değişken sıralı (ordinal) bir yapıya sahipse (örneğin "Düşük &lt; Orta &lt; Yüksek") <strong>Ordinal Lojistik Regresyon</strong> daha uygun bir seçimdir; bu analiz orantılı oranlar (proportional odds) varsayımı gerektirir ve SPSS'te Analyze → Regression → Ordinal yoluyla erişilir.</p>
"""

EXTRA_21 = """
<h2>Güç ve Örneklem Büyüklüğünü Savunmada Gerekçelendirmek</h2>
<p>p &gt; .05 bulan bir araştırmacı savunmada "Neden daha büyük örneklem almadınız?" sorusuyla karşılaşabilir. Bu soruya hazırlıklı olmak için şu argüman yapısını kullanın: <em>"Güç analizine göre belirlenen minimum örneklem [N] kişiydi ve bu sayıya ulaşıldı. Elde edilen örneklemde tespit edilemeyen etkiler, etki büyüklüğü [değer] ile küçük düzeyde kalmaktadır. Bu bulgu, uygulanan programın anlamlı bir etki yaratmadığını değil; mevcut örneklem boyutunda tespit sınırının altında kaldığını göstermektedir. Daha büyük bir çalışma ile bu olasılığın test edilmesi önerilmektedir."</em> Bu yapı hem metodolojik dürüstlüğü korur hem de bulguyu "başarısızlık" değil "sınır tespiti" olarak çerçeveler.</p>
"""

EXTRA_23 = """
<h2>R²'yi Tartışmak: Danışmanı ve Jüriyi İkna Etmek</h2>
<p>Düşük R² nedeniyle endişelenen araştırmacılar için savunmada kullanılabilecek ikna edici bir çerçeve: <em>"Sosyal bilim araştırmalarında bireysel davranış ve tutumlar onlarca değişkenin etkisiyle şekillenmektedir. Bu çalışmada incelenen [X değişkeni], bağımlı değişkendeki varyansın %12.6'sını açıklamakta olup bu oran ilgili alanyazınındaki [kaynak] ile uyumludur. Model F testi anlamlı bulunmuş (p = .005), katsayılar kuramsal beklentilerle örtüşmekte ve pratikte yorumlanabilir büyüklükte görünmektedir."</em> Bu gerekçelendirme R²'nin mutlak değerinden çok bağlamsal uygunluğunu vurgular; bu yaklaşım metodoloji açısından çok daha savunulabilirdir.</p>
"""

EXTRA_25 = """
<h2>Korelasyonu Nedensellikle Karıştırmamak</h2>
<p>Korelasyon analizinin en sık tekrarlanan hatası, yüksek korelasyon değerinin nedenselliği (causation) kanıtladığı varsayımıdır. Korelasyon her zaman nedenselliğin varlığına işaret etmez; aynı zamanda tersine nedensellik (reverse causation) veya gizli bir üçüncü değişken (confounding variable) tarafından da açıklanabilir. Nedensellik için korelasyon gerekli ama yeterli değildir.</p>
<p>Tezde: "Değişkenler arasında pozitif yönde anlamlı bir ilişki bulunmuştur" ifadesi doğruyken, "A değişkeni B'ye yol açmaktadır" ifadesi korelasyon analiziyle desteklenemez. Nedensellik iddiası için deneysel tasarım, boylamsal veri ya da yapısal eşitlik modellemesi gibi ileri yöntemler gerekir. Bu sınırlılığı tartışma bölümünde açıkça belirtmek hem akademik dürüstlüğü hem de bulguların sağlamlığını pekiştirir.</p>
"""

EXTRA_30 = """
<h2>Danışmana Örneklem Büyüklüğünü Savunmak</h2>
<p>Birçok danışman, "Neden bu kadar katılımcı seçtiniz?" sorusunu soracaktır. Güçlü bir yanıt şu unsurları içermelidir: kullandığınız hesaplama yöntemi (Cochran, G*Power), seçilen etki büyüklüğünün gerekçesi (literatürdeki benzer çalışmalar), α ve güç düzeyleri ile tampon oranı. Örnek: <em>"G*Power analizi, orta etki büyüklüğünde (f = .25), α = .05 ve .80 güç ile ANOVA için 159 kişi gerektirdiğini göstermiştir. Yaklaşık %15 eksik veri payı öngörülerek 185 kişiye ulaşılmış; 178 tam veri ile analize geçilmiştir."</em></p>
<p>Örneklem gerekçesinin tezin Yöntem bölümüne eklenmesi savunmada bu soruyu büyük ölçüde etkisizleştirir. Danışman onayından önce güç analizini tamamlamak, hem örneklem büyüklüğü hem de araştırmanın genel metodolojik kalitesi açısından belirleyici bir avantaj sağlar.</p>
"""

SLUGS_EXTRA = [
    ('chatgpty-e-tezini-yazdirmak-bilim-midir-yoksa-akademinin-olum-sertifikasi-mi', EXTRA_6),
    ('yayinla-ya-da-yok-ol-caginda-akademisyenin-sessiz-intihari-predatory-dergiler', EXTRA_8),
    ('turkiyenin-akademik-uretimi-nereye-gidiyor-openalex-ve-tr-dizin-verileriyle', EXTRA_9),
    ('tez-verilerini-google-driveda-tutmak-suc-mu-kvkk-gdpr', EXTRA_11),
    ('anonimlestirme-yanilgisi-isimsiz-veri-setlerinden-kimlik-yeniden-nasil-insa-ediliyor', EXTRA_12),
    ('saglikta-veri-krizi-turkiyede-klinik-arastirmalarin-verisi-neden-hep-kayip', EXTRA_13),
    ('survival-analizi-101-kaplan-meier-cox-regresyon-ve-tedavi-etkili-mi', EXTRA_14),
    ('enflasyon-verilerine-guveniyor-muyuz-tuik-enag-resmi-veri-tartismasi', EXTRA_15),
    ('normallik-testi-saglanmazsa-hangi-test-kullanilir', EXTRA_17),
    ('bagimsiz-mi-bagimli-mi-t-testi-fark-ne-zaman-onemli', EXTRA_18),
    ('ki-kare-mi-lojistik-regresyon-mu-ikisinin-farki-ne', EXTRA_20),
    ('p-degeri-0-05-ten-buyuk-cikti-tezime-ne-yazarim', EXTRA_21),
    ('r-kare-dusuk-cikinca-regresyon-modeli-gecersiz-mi', EXTRA_23),
    ('korelasyon-yuksek-ama-anlamsiz-bu-nasil-olur', EXTRA_25),
    ('tez-icin-kac-anket-doldurulmali-orneklem-buyuklugu-nasil-hesaplanir', EXTRA_30),
]


def add_final_batch2(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    ok = fail = 0
    for slug, extra in SLUGS_EXTRA:
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug[:50]} bulunamadı')
            continue
        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + extra + content[hr_pos:]) if hr_pos != -1 else content + extra
        post.save()
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        s = '✓' if wc >= 800 else '✗'
        if wc >= 800:
            ok += 1
        else:
            fail += 1
        print(f'  {s} {wc:4d} | {slug[:50]}')
    print(f'\n  Başarılı: {ok} | Eksik: {fail}')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0134_expand_blog_posts_batch2'),
    ]

    operations = [
        migrations.RunPython(add_final_batch2, migrations.RunPython.noop),
    ]
