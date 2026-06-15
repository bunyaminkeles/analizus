from django.db import migrations

PATCHES = {
    'normallik-testi-sonuclari-nasil-yorumlanir-shapiro-wilk-kolmogorov-smirnov': """
<h2>Özet: Doğru Karar için Üç Adım</h2>
<p>Normallik testini yorumlarken tek bir p değerine güvenmek yerine üç adımlı bir süreç izleyin: (1) Shapiro-Wilk p değerini örneklem büyüklüğüyle birlikte okuyun — küçük n'lerde p &gt; .05 normalliği garanti etmez; büyük n'lerde p &lt; .05 küçük sapmayı işaret eder. (2) Çarpıklık ve basıklık değerlerini standart hatayla oranladığınızda |z| &lt; 1.96 çıkıyorsa dağılım pratikte normale yeterince yakındır. (3) Q-Q plot'ta noktalar referans çizgisine yakınsa grafiksel kanıt sayısal testi destekler. Bu üç kanal uyumlu sonuç veriyorsa güvenle karar verebilirsiniz; tutarsızlık varsa non-parametrik alternatifleri değerlendirin ve kararınızın gerekçesini tez yöntem bölümünde belirtin. Normallik testi nihai hüküm değil, kılavuzdur.</p>
""",
    'spsste-t-testi-adim-adim-bagimsiz-ve-bagimli-orneklem-karsilastirmasi': """
<h2>Pratik Özet</h2>
<p>SPSS t-testi analizinde doğru sütunu okumak, doğru kararı vermenin temelidir. Bağımsız t-testinde Levene p &gt; .05 ise eşit varyans satırı, aksi hâlde Welch düzeltmesi satırı esas alınır. Bağımlı t-testinde ise tek bir satır olduğu için bu seçim gerekmez. Her iki testte de etki büyüklüğü (Cohen's d) ayrıca hesaplanmalı; p değeriyle birlikte raporlanmalıdır. Bulguların metin içi ifadesinde parantez içinde sırasıyla t, df ve p değerleri verilmeli; tabloda B, SE ve β sütunları bulunmalıdır. Bu kurallara uyan bir bulgu bölümü hem metodolojik güvenilirlik hem de akademik okunabilirlik açısından eksiksiz sayılır.</p>
""",
    'acimlayici-ve-dogrulayici-faktor-analizi-afa-dfa-arasindaki-farklar': """
<h2>Özet: Hangi Analiz, Hangi Soru?</h2>
<p>AFA ile DFA arasındaki seçim bir teknik tercihten önce araştırma sorusunun niteliğini yansıtır. "Bu ölçeğin boyutları nedir?" sorusu AFA'ya, "Bu boyutlar doğrulanalı mı?" sorusu DFA'ya işaret eder. Tez danışmanı "geçerlilik analizi yap" dediğinde kastettiği genellikle DFA'dır; sıfırdan bir ölçek geliştiriyorsanız AFA zorunludur. Her iki analizde de yeterli örneklem büyüklüğü kritik önem taşır: AFA için madde başına en az 5–10 katılımcı, DFA için minimum 200 gözlem önerilmektedir. Uyum indeksleri ve faktör yükleri birlikte raporlandığında analizin bütünlüğü sağlanmış olur.</p>
""",
    'p-degeri-krizinin-100-yilinda-istatistiksel-anlamlilik-bilimi-yanlis-mi-yonlendirdi': """
<h2>Araştırmacı İçin Pratik Özet</h2>
<p>p değeri krizi, istatistiksel analizi daha dürüst ve şeffaf yapma çağrısıdır. Tezinizde bu çağrıya yanıt vermek için şu adımları izleyebilirsiniz: p değerini her zaman etki büyüklüğü (Cohen's d, η², r) ve güven aralığıyla birlikte raporlayın. Anlamlılık eşiğine ulaşamayan bulguları "negatif" olarak nitelendirmek yerine "yeterli istatistiksel güç sağlanamadı" veya "belirsizlik devam etmektedir" gibi nüanslı bir dille aktarın. Mümkünse çalışmanızı OSF üzerinden ön kaydedin — bu hem p-hacking riskini ortadan kaldırır hem de araştırmanızın akademik güvenilirliğini pekiştirir. Yüz yılın birikiminden çıkan ders şudur: tek bir sayı hiçbir zaman bütün hikâyeyi anlatamaz.</p>
""",
    'veri-sahteliginden-veri-seffafligina-open-science-hareketi-ve-turkiyede-acik-veri': """
<h2>Özet: Şeffaflık Bireysel Katkıyla Büyür</h2>
<p>Açık Bilim hareketi büyük kurumsal dönüşümler gerektirse de her araştırmacının kendi çalışmasında alabileceği küçük adımlar vardır: ORCID kimliği oluşturmak, veri setini Zenodo'da yayımlamak, analiz kodunu GitHub'da paylaşmak veya çalışmayı OSF'e yüklemek bunların başında gelir. Türkiye'de bu alışkanlıkların henüz yaygınlaşmadığı bir ortamda bu adımları atan araştırmacılar hem küresel bilim topluluğuna katkı sağlar hem de uluslararası görünürlüklerini artırır. Atıf alma oranı ile veri paylaşımı arasındaki pozitif korelasyon artık iyi belgelenmiştir; şeffaflık hem etik bir yükümlülük hem de stratejik bir akademik yatırımdır.</p>
""",
    'cronbach-alpha-0-6-cikti-ne-yapmaliyim': """
<h2>Özet: Adım Adım Eylem Planı</h2>
<p>α = .60 bulgusuyla karşılaştığınızda paniğe kapılmadan şu sırayı izleyin: (1) Madde-toplam korelasyonlarını inceleyin; .30 altındaki maddeleri işaretleyin. (2) "Alpha if item deleted" sütununu kontrol edin; silme durumunda alfa artıyorsa teorik gerekçeyi de tartın. (3) Gerekçesiz silemiyorsanız ya maddeyi yeniden ifade edin ya da omega katsayısını alternatif güvenilirlik göstergesi olarak raporlayın. (4) Standart bir ölçek kullanıyorsanız mevcut hâliyle raporlayıp düşük alfanın muhtemel nedenlerini tartışma bölümünde ele alın. Bu dört adımın herhangi biriyle elde ettiğiniz sonucu şeffaflıkla teze yansıtmak, α = .60'ı metodolojik zafiyet olmaktan çıkarıp olgunluk göstergesine dönüştürür.</p>
""",
    'shapiro-wilk-p-0-049-normal-dagitim-var-mi-yok-mu': """
<h2>Özet: Sınır Değerde Karar</h2>
<p>p = .049 borderline bir bulgudur ve tek başına net bir karar vermek için yeterli değildir. Doğru yaklaşım çok katmanlıdır: çarpıklık ve basıklık istatistikleri hafif sapma gösteriyorsa, Q-Q plot noktaları referans çizgisine yakınsa ve örneklem büyüklüğü n ≥ 30 ise parametrik testlere devam etmek Merkezi Limit Teoremi çerçevesinde savunulabilirdir. Buna karşın belirsizlik sürdüğünde hem parametrik hem non-parametrik analizi çalıştırıp sonuçların tutarlılığını raporlamak bulgularınıza ek güvenilirlik katar. Her durumda kararınızı ve gerekçenizi tezin yöntem bölümünde açıkça belirtmek metodolojik şeffaflığın ve akademik olgunluğun somut göstergesidir.</p>
""",
    'regresyon-analizi-tez-bulgular-bolumune-nasil-aktarilir': """
<h2>Özet: Eksiksiz Raporlama Kontrol Listesi</h2>
<p>Regresyon bulgularını teze aktarmadan önce şu listeyi gözden geçirin: (1) Model uyum istatistikleri (R², Düzeltilmiş R², F, p) raporlandı mı? (2) Her yordayıcı için B, SE B, β, t ve p değerleri tabloda yer alıyor mu? (3) Standardize olmayan katsayı B yorumlanabilir mi — birimi ve yorumu metin içinde açıklandı mı? (4) Varsayım kontrolleri (VIF, Durbin-Watson, artık normalliği, homokedastisite) raporlandı mı? (5) Logistik regresyonda Odds Ratio ve sınıflandırma doğruluğu eklendi mi? Bu beş maddeye "evet" diyorsanız bulgu bölümünüz metodolojik açıdan eksiksizdir ve savunmada regresyon tablosuna yönelik herhangi bir soruya hazırlıklısınız demektir.</p>
""",
}


def finalize_batch3(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    ok = fail = 0
    for slug, patch in PATCHES.items():
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug[:55]} bulunamadı')
            continue
        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + patch + content[hr_pos:]) if hr_pos != -1 else content + patch
        post.save()
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        s = '✓' if wc >= 800 else '✗'
        if wc >= 800:
            ok += 1
        else:
            fail += 1
        print(f'  {s} {wc:4d} | {slug[:55]}')
    print(f'\n  Başarılı: {ok} | Eksik: {fail}')


class Migration(migrations.Migration):
    dependencies = [('forum', '0138_expand_blog_batch3')]
    operations = [migrations.RunPython(finalize_batch3, migrations.RunPython.noop)]
