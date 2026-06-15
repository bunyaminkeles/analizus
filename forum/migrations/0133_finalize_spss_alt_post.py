from django.db import migrations

PATCH = """
<h2>Ücretsiz Araç Seçiminde Son Söz</h2>
<p>Hangi ücretsiz aracı seçerseniz seçin, en önemli adım analizlerinizi <strong>şimdi başlatmaktır</strong>. jamovi veya JASP'ı bilgisayarınıza kurmak 10 dakika, Analizus'u tarayıcıda açmak ise birkaç saniye alır. SPSS lisansı beklemek yerine bu araçlardan birini deneyerek hangi arayüzün size en doğal geldiğini keşfetmek, tez analizlerinize en verimli başlangıcı sağlar. Araç seçiminde mükemmeliyetçilik değil, sürdürülebilirlik belirleyicidir: sürecinizi tamamlayabileceğiniz araç, en iyi araçtır.</p>
"""


def finalize(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    slug = 'ucretsiz-spss-alternatifi-var-mi-tez-icin-en-iyi-secenekler'
    try:
        post = BlogPost.objects.get(slug=slug)
    except BlogPost.DoesNotExist:
        print(f'  UYARI: {slug} bulunamadı')
        return

    content = post.content
    hr_pos = content.rfind('<hr>')
    post.content = (content[:hr_pos] + PATCH + content[hr_pos:]) if hr_pos != -1 else content + PATCH
    post.save()

    text = re.sub(r'<[^>]+>', ' ', post.content)
    wc = len(text.split())
    status = '✓' if wc >= 800 else '✗'
    print(f'  {status} {slug[:50]} ({wc} kelime)')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0132_expand_blog_posts_part3'),
    ]

    operations = [
        migrations.RunPython(finalize, migrations.RunPython.noop),
    ]
