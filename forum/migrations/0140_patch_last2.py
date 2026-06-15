from django.db import migrations

PATCHES = {
    'p-degeri-krizinin-100-yilinda-istatistiksel-anlamlilik-bilimi-yanlis-mi-yonlendirdi': """
<p><strong>Önemli hatırlatma:</strong> Amerikan İstatistik Derneği (ASA) 2016'da yayımladığı bildirge ile p değerinin tek karar ölçütü olarak kullanılmasını açıkça eleştirmiştir. 2019 bildirgesinde ise "istatistiksel anlamlılık" kavramını terk etmeyi öneren 800'den fazla bilim insanının imzaladığı bir çağrı yayımlanmıştır. Bu gelişmeler, p &lt; .05 eşiğinin bilimsel bir kanun olmadığını; tarihsel ve kültürel bir uzlaşının ürünü olduğunu göstermektedir.</p>
""",
    'shapiro-wilk-p-0-049-normal-dagitim-var-mi-yok-mu': """
<p><strong>Son not:</strong> Normallik kararında çok kanallı düşünmek, tek bir p değerine kilitlenmekten her zaman daha sağlıklı ve savunulabilir bir yaklaşımdır. Tez jürisi "neden parametrik test kullandınız?" diye sorduğunda verilere dayalı çok adımlı gerekçeniz en güçlü yanıtınız olacaktır.</p>
""",
}


def patch_last2(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
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
        print(f'  {s} {wc:4d} | {slug[:55]}')


class Migration(migrations.Migration):
    dependencies = [('forum', '0139_finalize_batch3')]
    operations = [migrations.RunPython(patch_last2, migrations.RunPython.noop)]
