from django.db import migrations

PATCHES = {
    'turkiyenin-akademik-uretimi-nereye-gidiyor-openalex-ve-tr-dizin-verileriyle': """
<p><strong>Sonuç olarak:</strong> Türkiye'nin akademik geleceği, mevcut nicel birikim üzerine niteliksel bir dönüşüm inşa etmeyi gerektirmektedir. Bireysel araştırmacıların ORCID kullanımından açık erişim politikalarını benimsemeye kadar uzanan pratik adımları, bu dönüşümü aşağıdan yukarıya mümkün kılacaktır. Bibliyometrik veriyi anlamak ve kullanmak artık yalnızca politika yapıcıların değil, her araştırmacının temel yetkinlikleri arasında yer almaktadır.</p>
""",
    'anonimlestirme-yanilgisi-isimsiz-veri-setlerinden-kimlik-yeniden-nasil-insa-ediliyor': """
<p><strong>Araştırmacı için özet:</strong> Verilerinizdeki doğrudan tanımlayıcıları silmek yalnızca ilk adımdır. k-Anonimlik kriterini karşılamak, diferansiyel gizlilik yöntemlerini değerlendirmek ve veri paylaşımından önce re-identification riskini sistematik biçimde test etmek, gerçek anlamda etik ve güvenli bir araştırma pratiğinin temel bileşenleridir. Bu teknikleri öğrenmek ve uygulamak hem araştırmacının hem de katılımcıların çıkarını korur.</p>
""",
    'bagimsiz-mi-bagimli-mi-t-testi-fark-ne-zaman-onemli': """
<h2>Sonuç: Tasarım Analizi Belirler</h2>
<p>Bağımsız ve bağımlı t-testi arasındaki seçim, yalnızca istatistiksel bir karar değil; araştırma tasarımının doğrudan bir yansımasıdır. Veri toplamadan önce hangi t-testinin uygulanacağını belirlemek ve veri girişini bu tasarıma göre yapılandırmak, analizin bütünlüğü açısından kritiktir. Tasarım netleştiğinde doğru test, tek ve açık bir seçenek olarak kendini gösterir; hangi testi kullanacağınızı bilmiyorsanız tasarımınızı yeniden netleştirmeniz gerekiyordur.</p>
""",
    'ki-kare-mi-lojistik-regresyon-mu-ikisinin-farki-ne': """
<p><strong>Son not:</strong> Ki-kare ve lojistik regresyon, kategorik bağımlı değişken analizinin birbirini tamamlayan iki aracıdır. Araştırma sorunuzun yalnızca ilişki mi, yoksa tahmin modeli mi gerektirdiğini belirleyerek doğru analizi seçin; bu seçimi tezin Yöntem bölümünde açıkça gerekçelendirin. Doğru seçim ve güçlü gerekçelendirme, savunmada metodolojik güveninizin temelini oluşturacaktır.</p>
""",
}


def finalize_last4(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    for slug, patch in PATCHES.items():
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug[:50]} bulunamadı')
            continue
        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + patch + content[hr_pos:]) if hr_pos != -1 else content + patch
        post.save()
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        s = '✓' if wc >= 800 else '✗'
        print(f'  {s} {wc:4d} | {slug[:50]}')


class Migration(migrations.Migration):
    dependencies = [('forum', '0136_finalize_batch2')]
    operations = [migrations.RunPython(finalize_last4, migrations.RunPython.noop)]
