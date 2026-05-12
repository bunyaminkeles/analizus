# ANALİZUS.COM — BLOG YAZISI MIGRATION PROMPTU

## GÖREV

`analizus.com` için bir blog yazısı oluştur ve aşağıdaki Python migration dosyasını üret.
Araştır, içeriği yaz, şablonu doldur — tek çıktı tek Python dosyası.

---

## ADIM 1 — KONU BİLGİSİ (BURADAN BAŞLA)

```
Konu          : _______________________________________________
Hedef okuyucu : _______________________________________________  (tez öğrencisi / akademisyen / veri analisti)
Seviye        : _______________________________________________  (beginner / intermediate / advanced)
Kategori adı  : _______________________________________________  (örn: İstatistik Rehberi)
Kategori slug : _______________________________________________  (örn: istatistik-rehberi)
Etiketler     : _______________________________________________  (virgülle, 2–5 adet)
Son migration : _______________________________________________  (örn: 0078_fix_cronbach_excerpt_category)
Sonraki numara: _______________________________________________  (örn: 0079)
```

> Göndermeden önce son iki satırı doldur:
> ```bash
> ls forum/migrations/ | grep -v __pycache__ | sort | tail -1
> ```

---

## ADIM 2 — ARAŞTIR

WebSearch kullan. Her bilgi gerçek ve doğrulanmış olmalı — uydurma yasak.
Güncel sürüm numaraları, menü yolları, formüller, kaynak referansları topla.

---

## ADIM 3 — MIGRATION NUMARASI

Dosya adında ve `dependencies` içinde **KONU BİLGİSİ'ndeki "Sonraki numara"** değerini kullan.
Tahmin etme, prompt içindeki örnek numarayı kullanma.

---

## ADIM 4 — DOSYAYI ÜRET

### Dosya yolu (kesin, değişmez)

```
forum/migrations/<Sonraki numara>_blog_<konu-slug>.py
                  ^^^^^^^^^^^^^^
                  KONU BİLGİSİ'ndeki "Sonraki numara" değeri — 0077, 0078 vb.
forum app — başka hiçbir app'in migrations klasörüne yazma
```

### Şablon — SADECE boş string (`''`) olan yerleri ve `CONTENT` içeriğini doldur

⛔ **ŞABLONU YENİDEN YAZMA.** Fonksiyon adları, değişken adları, model çağrıları, `get_or_create` yapısı — hiçbirini değiştirme.
Gemini'nin kendi stiliyle yazdığı her satır hatalıdır. Şablon kopyalanır, boşluklar doldurulur.

```python
from django.db import migrations

CONTENT = """
[HTML içerik — kurallar aşağıda]
"""

POST = {
    'title':            '',   # max 200 karakter
    'slug':             '',   # tire ile, Türkçe özel karakter yok
    'excerpt':          '',   # ZORUNLU — boş bırakma! max 300 karakter, say ve kontrol et
    'level':            '',   # beginner / intermediate / advanced
    'meta_title':       '',   # KESİNLİKLE max 70 karakter — say ve kontrol et
    'meta_description': '',   # KESİNLİKLE max 160 karakter — say ve kontrol et
    'status':           'published',
    'is_featured':      False,
    'category_slug':    '',   # ⛔ ZORUNLU — boş bırakma! Türkçe özel karakter yok, tire ile (örn: istatistik-101)
    'category_name':    '',   # ⛔ ZORUNLU — boş bırakma!
    'category_icon':    'bi-bar-chart',
    'category_color':   '#00d2ff',
    'tags': [
        {'name': '', 'slug': ''},
        {'name': '', 'slug': ''},
    ],
}


def ekle(apps, schema_editor):
    BlogPost     = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    BlogTag      = apps.get_model('forum', 'BlogTag')
    User         = apps.get_model('auth', 'User')

    yazar = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not yazar:
        return

    # ⛔ ARAMA ALANI SADECE slug OLMALI — name ile get_or_create YAPMA, slug='' yaratır, UNIQUE constraint patlar
    kategori, _ = BlogCategory.objects.get_or_create(
        slug=POST['category_slug'],
        defaults={
            'name':  POST['category_name'],
            'icon':  POST['category_icon'],
            'color': POST['category_color'],
        },
    )

    post, olusturuldu = BlogPost.objects.get_or_create(
        slug=POST['slug'],
        defaults={
            'title':            POST['title'],
            'excerpt':          POST['excerpt'],
            'content':          CONTENT.strip(),
            'level':            POST['level'],
            'meta_title':       POST['meta_title'],
            'meta_description': POST['meta_description'],
            'status':           POST['status'],
            'is_featured':      POST['is_featured'],
            'author':           yazar,
            'category':         kategori,
        },
    )

    if olusturuldu:
        for t in POST['tags']:
            tag, _ = BlogTag.objects.get_or_create(
                slug=t['slug'],
                defaults={'name': t['name']},
            )
            post.tags.add(tag)


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0078_fix_cronbach_excerpt_category'),   # ← KONU BİLGİSİ'ndeki "Son migration" değeri
    ]

    operations = [
        migrations.RunPython(ekle, migrations.RunPython.noop),
    ]
```

---

## İÇERİK KURALLARI (CONTENT)

- HTML formatı: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>`, `<strong>`, `<code>`
- `<h1>` kullanma
- Adım adım rehberlerde `<ol>` ile numaralandır
- Kod/menü yolları `<code>` içinde
- Sonunda `<hr>` ve `<small>` içinde kaynakça
- Uzunluk: 800–1500 kelime
- **Max 50.000 karakter** — aşarsa migration `full_clean` hatası verir

---

## YASAK — BUNLARI ASLA YAPMA

| Yasak | Doğrusu | Neden |
|-------|---------|-------|
| `'excerpt': ''` boş bırak | Gerçek özet metni yaz | `blank=True` yok — `save()` `full_clean()` çağırır, `ValidationError` fırlar |
| `BlogCategory.get_or_create(name='...')` | `get_or_create(slug='...', defaults={'name':...})` | `slug` unique zorunlu — `name` ile arama `slug=''` yaratır, UNIQUE constraint patlar |
| `apps.get_model('forum', 'Category')` | `apps.get_model('forum', 'BlogCategory')` | `Category` forum konularının modeli — `BlogCategory` farklı bir model |
| `apps.get_model('blog', 'Yazi')` | `apps.get_model('forum', 'BlogPost')` | App `forum`, model `BlogPost` — `blog` diye app yok |
| `apps.get_model('blog', 'BlogYazisi')` | `apps.get_model('forum', 'BlogPost')` | `BlogYazisi` mainzer-binger'a ait — bu proje analizdestek |
| `User.objects.get_or_create(username='...')` | `User.objects.filter(is_superuser=True).first()` | Yeni kullanıcı yaratır — mevcut superuser kullanılmalı |
| Fonksiyon adını `create_blog_post` yap | `ekle` olarak bırak | Şablon değiştirilmez |
| Dosyayı `ilan/`, `blog/`, `makaleanaliz/` içine koy | `forum/migrations/` | Yanlış app — Django bulamaz |
| `.objects.create(...)` | `.objects.get_or_create(...)` | İki kez çalışırsa `IntegrityError` — slug unique |
| `dependencies = [('forum', '0001_initial')]` | KONU BİLGİSİ'ndeki Son migration değerini yaz | Dependency chain bozulur |
| `migrations.RunPython(ekle)` tek argüman | `migrations.RunPython(ekle, migrations.RunPython.noop)` | Reverse migration çalışmaz |
| `status` alanını atla | `'status': 'published'` ekle | Yazı draft kalır, sitede görünmez |
| `0077_blog.py` (numarasız) | `0077_blog_<slug>.py` | 4 haneli önek zorunlu |
| Kullanılmayan `import` | Sadece `from django.db import migrations` | Temiz kod |

---

## ÇIKTI KURALI

Sadece Python dosyasını ver. Açıklama veya özet yazma.

---

## UYGULAMA (migration üretildikten sonra)

```bash
# 1. Kaydet
# forum/migrations/<Sonraki numara>_blog_<slug>.py

# 2. Test
cd /home/bunyamin/Documents/analizdestek
python manage.py migrate --check
python manage.py migrate

# 3. Commit
git add forum/migrations/<Sonraki numara>_blog_<slug>.py
git commit -m "feat(blog): <konu kısa özeti>"

# 4. Deploy
ssh root@204.168.195.246
cd /app && git pull && python manage.py migrate && systemctl restart gunicorn
```

**Prompt güncelleme:** Migration sonrası bu dosyada "Son migration" satırını yeni dosya adıyla güncelle, commit'e ekle:
```bash
git add blog_yazisi_create.md
```
