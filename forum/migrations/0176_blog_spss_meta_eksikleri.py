from django.db import migrations

# Faz 6 (10 Ekim 2026): GSC'de "spss benzeri programlar" (40 gösterim, sıra 27) sorgusu için yeni
# yazı yazmak yerine önce mevcut 3 ilgili yazı kontrol edildi — ucretsiz-spss-alternatifi... zaten
# tam SEO alanlarına sahipti (yeni yazı cannibalization yaratırdı), ama bu 2 yazının meta_title/
# meta_description'ı tamamen boştu. Alan doluysa dokunulmaz.
SEO_META = {
    'spss-mi-r-mi-tez-icin-hangisi-daha-kolay': (
        'SPSS mi R mi? Tez İçin Hangisi Daha Kolay? | Analizus',
        'Tez analizlerinde SPSS mi R mı kullanmalısınız? Öğrenme eğrisi, maliyet, çıktı kalitesi ve '
        'sosyal bilimlerdeki yaygınlık açısından karşılaştırmalı rehber.',
    ),
    'spsste-t-testi-adim-adim-bagimsiz-ve-bagimli-orneklem-karsilastirmasi': (
        "SPSS'te t-Testi Nasıl Yapılır? Adım Adım Rehber | Analizus",
        "SPSS'te bağımsız ve bağımlı örneklem t-testi adım adım: varsayım kontrolü, analiz adımları, "
        'APA formatında sonuç raporlama örnekleriyle anlatılıyor.',
    ),
}


def set_seo_meta(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    for slug, (title, description) in SEO_META.items():
        post = BlogPost.objects.filter(slug=slug).first()
        if post is None:
            print(f'  UYARI: {slug[:55]} bulunamadı')
            continue
        fields = []
        if not post.meta_title:
            post.meta_title = title
            fields.append('meta_title')
        if not post.meta_description:
            post.meta_description = description
            fields.append('meta_description')
        if fields:
            post.save(update_fields=fields)
        print(f"  {'✓' if fields else '='} {slug[:55]} {fields or 'dolu, dokunulmadı'}")


def unset_seo_meta(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    for slug, (title, description) in SEO_META.items():
        BlogPost.objects.filter(slug=slug, meta_title=title).update(meta_title='')
        BlogPost.objects.filter(slug=slug, meta_description=description).update(meta_description='')


class Migration(migrations.Migration):
    dependencies = [('forum', '0175_profile_directory_override_and_more')]
    operations = [migrations.RunPython(set_seo_meta, unset_seo_meta)]
