from django.db import migrations

# GSC (30 Eylül 2026): gösterimi yüksek, tıklama oranı düşük blog yazıları — yalnız <title> ve
# meta description (sayfadaki başlık/içerik/slug değişmez). Alan doluysa dokunulmaz: admin'den
# elle girilmiş değerin üstüne yazılmaz.
SEO_META = {
    'acimlayici-ve-dogrulayici-faktor-analizi-afa-dfa-arasindaki-farklar': (
        'AFA ve DFA Nedir? Farkları ve Ne Zaman Kullanılır',
        'Açımlayıcı (AFA) ve doğrulayıcı faktör analizi (DFA) nedir, farkları neler? KMO ve Bartlett '
        'varsayımları, ölçek geliştirmede ikisinin birlikte kullanımı.',
    ),
    'cronbach-alpha-degeri-kac-olmali-tezde-nasil-yorumlanir-raporlanir': (
        'Cronbach Alpha Nedir, Kaç Olmalı? Yorum ve Raporlama',
        "Cronbach alfa (α) iç tutarlılık katsayısı nedir, kaç olmalı? Kabul edilebilir değerler, SPSS'te "
        'hesaplama, APA raporlama ve değer düşük çıkarsa yapılacaklar.',
    ),
    'cronbach-alpha-guvenilirlik-bulgulari-nasil-yazilir': (
        'Cronbach Alpha Bulguları Nasıl Yazılır? APA Tablo Örneği',
        'Güvenirlik analizi sonuçlarını teze aktarın: alt boyut tablosu, madde-toplam korelasyonu, SPSS '
        'çıktısını okuma ve APA formatında raporlama örneği.',
    ),
    'normallik-testi-sonuclari-nasil-yorumlanir-shapiro-wilk-kolmogorov-smirnov': (
        'Normallik Testi Yorumu: Shapiro-Wilk mi, K-S mi?',
        'Shapiro-Wilk ve Kolmogorov-Smirnov testlerinden hangisi seçilmeli, p değeri nasıl yorumlanır? '
        'SPSS adımları, çarpıklık-basıklık ve örneklem etkisi.',
    ),
    'normallik-testi-saglanmazsa-hangi-test-kullanilir': (
        'Normallik Sağlanmazsa Hangi Test? Non-Parametrik Karşılıklar',
        'Normal dağılım sağlanmadığında t-testi, ANOVA ve Pearson yerine hangi non-parametrik test '
        'kullanılır? Dönüşüm tablosu ve APA raporlama örnekleri.',
    ),
    'vif-degeri-yuksek-cikti-cok-dogrusal-baglanti-ne-demek': (
        'VIF Değeri Kaç Olmalı? Çoklu Doğrusal Bağlantı',
        "Regresyonda VIF ve tolerance değerleri nasıl yorumlanır, VIF 10'u aşınca ne yapılır? SPSS'te "
        'kontrol adımları ve tezde APA raporlama örneği.',
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
    # Yalnız bu migration'ın yazdığı değerleri geri al
    BlogPost = apps.get_model('forum', 'BlogPost')
    for slug, (title, description) in SEO_META.items():
        BlogPost.objects.filter(slug=slug, meta_title=title).update(meta_title='')
        BlogPost.objects.filter(slug=slug, meta_description=description).update(meta_description='')


class Migration(migrations.Migration):
    dependencies = [('forum', '0161_sitesettings_promote_price_3_days_and_more')]
    operations = [migrations.RunPython(set_seo_meta, unset_seo_meta)]
