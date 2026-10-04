# Hizmet sayfası bölümlerini tek cümlelik tanımdan "tanım → ne zaman → teslimat" üçlüsüne
# genişletir (kullanıcı: "bu kadar kısa açıklama SEO için yeterli mi?" — haklı, plan şartnamesinde
# zaten bu üçlü vardı, pilot yazarken atlanmıştı). Korumalı: body hâlâ ilk seferki (tek cümlelik)
# metinle birebir aynıysa günceller; admin'den elle değiştirilmişse dokunmaz.
from django.db import migrations

# (service_page_slug, anchor): (eski_body, yeni_body)
UPDATES = {
    ('nicel-analiz', 'on-analizler'): (
        'Veri temizleme, eksik veri ve betimsel istatistiklerle analiz sürecine sağlam bir başlangıç.',
        'Veri temizleme, eksik veri ve betimsel istatistiklerle analiz sürecine sağlam bir başlangıç. '
        'Veri setinizi ilk kez analiz edecekseniz ya da sonuçlardan önce verinin güvenilir olduğundan '
        'emin olmak istiyorsanız bu aşamadan başlanır. Temizlenmiş veri seti, eksik veri raporu ve '
        'betimsel istatistik tablosu teslim edilir.'
    ),
    ('nicel-analiz', 'gecerlik-guvenirlik'): (
        'Ölçek geliştirme ve uyarlama çalışmalarında geçerlik-güvenirlik analizleri.',
        'Ölçek geliştirme ve uyarlama çalışmalarında geçerlik-güvenirlik analizleri. Yeni bir ölçek '
        'geliştiriyor ya da var olan bir ölçeği farklı bir örnekleme uyarlıyorsanız gereklidir. '
        'Cronbach alfa, madde-toplam korelasyonu ve gerekiyorsa açımlayıcı/doğrulayıcı faktör analizi '
        'sonuçları raporlanır.'
    ),
    ('nicel-analiz', 'iliski-korelasyon'): (
        'Değişkenler arası ilişkilerin korelasyon analizleriyle incelenmesi.',
        'Değişkenler arası ilişkilerin korelasyon analizleriyle incelenmesi. İki veya daha fazla '
        'değişken arasında bir ilişki olup olmadığını, yönünü ve gücünü görmek istediğinizde '
        'kullanılır. Korelasyon katsayıları, anlamlılık değerleri ve yorumlanmış sonuç raporu '
        'alırsınız.'
    ),
    ('nicel-analiz', 'fark-testleri'): (
        'Gruplar arası farkların t-testi, ANOVA ve non-parametrik testlerle değerlendirilmesi.',
        'Gruplar arası farkların t-testi, ANOVA ve non-parametrik testlerle değerlendirilmesi. İki ya '
        'da daha fazla grubu (ör. deney-kontrol, cinsiyet, yaş grubu) bir değişken üzerinden '
        'karşılaştırmak istediğinizde kullanılır. Uygun test seçimi, varsayım kontrolleri ve APA '
        'formatında yorumlanmış sonuçlar teslim edilir.'
    ),
    ('nicel-analiz', 'regresyon-sem'): (
        'Regresyon modelleri ve SmartPLS/AMOS ile yapısal eşitlik modellemesi (SEM).',
        'Regresyon modelleri ve SmartPLS/AMOS ile yapısal eşitlik modellemesi (SEM). Bir ya da birden '
        'fazla değişkenin başka bir değişkeni ne ölçüde yordadığını veya karmaşık değişken '
        'ilişkilerini bir model üzerinden test etmek istediğinizde kullanılır. Model uyum indeksleri, '
        'yol katsayıları ve model şeması dahil tam rapor alırsınız.'
    ),
    ('nicel-analiz', 'zaman-serisi-ekonometri'): (
        'EViews ile ekonometrik modelleme ve zaman serisi analizleri.',
        'EViews ile ekonometrik modelleme ve zaman serisi analizleri. Zaman içinde değişen verilerle '
        '(ör. enflasyon, satış, hisse fiyatı) tahmin ya da ilişki modeli kurmak istediğinizde '
        'kullanılır. Durağanlık testleri, model tahmini ve öngörü sonuçları raporlanır.'
    ),
    ('nicel-analiz', 'makine-ogrenmesi'): (
        'Sınıflandırma ve tahmin modelleri için makine öğrenmesi destekli analiz.',
        'Sınıflandırma ve tahmin modelleri için makine öğrenmesi destekli analiz. Geleneksel '
        'istatistiksel yöntemlerin yetersiz kaldığı büyük veya karmaşık veri setlerinde tahmin/'
        'sınıflandırma yapmak istediğinizde kullanılır. Model performans metrikleri (doğruluk, F1 '
        'skoru vb.) ve kullanılan kod/çıktı dosyaları teslim edilir.'
    ),
    ('akademik-danismanlik', 'tez-onerisi'): (
        'Araştırma sorusu, kapsam ve yöntem seçiminde tez önerisi aşamasına destek.',
        'Araştırma sorusu, kapsam ve yöntem seçiminde tez önerisi aşamasına destek. Tez konunuzu '
        'netleştirmeden ya da öneri jürisine çıkmadan önce yol haritanızı sağlamlaştırmak '
        'istediğinizde kullanılır. Araştırma sorusu, kapsam ve yöntem önerisini içeren geri bildirim '
        'alırsınız.'
    ),
    ('akademik-danismanlik', 'tez-danismanligi'): (
        'Tez yazım sürecinde yöntem ve yapı konusunda danışmanlık.',
        'Tez yazım sürecinde yöntem ve yapı konusunda danışmanlık. Tez yazım sürecinde yöntem, bölüm '
        'sırası ya da akademik yapı konusunda ikinci bir görüşe ihtiyaç duyduğunuzda kullanılır. '
        'Bölüm bazlı geri bildirim ve önerilen düzeltmeler iletilir.'
    ),
    ('akademik-danismanlik', 'etik-kurul'): (
        'Etik kurul başvuru dosyası hazırlığında yönlendirme.',
        'Etik kurul başvuru dosyası hazırlığında yönlendirme. Etik kurul başvurusu öncesi gerekli '
        'belgelerin eksiksiz ve kurula uygun hazırlandığından emin olmak istediğinizde kullanılır. '
        'Başvuru dosyanız gözden geçirilir, eksik/hatalı noktalar işaretlenerek iade edilir.'
    ),
    ('akademik-danismanlik', 'makale-hazirligi'): (
        'Akademik makale hazırlığında yöntem ve yapı danışmanlığı.',
        'Akademik makale hazırlığında yöntem ve yapı danışmanlığı. Çalışmanızı bir dergiye '
        'göndermeden önce yöntem ve yapı açısından gözden geçirtmek istediğinizde kullanılır. '
        'Makalenizin yöntem ve yapısına dair yazılı geri bildirim alırsınız.'
    ),
    ('akademik-danismanlik', 'metin-editorlugu'): (
        'Akademik metinlerde dil, anlatım ve format düzenlemesi.',
        'Akademik metinlerde dil, anlatım ve format düzenlemesi. Metniniz hazır ama dil, anlatım '
        'bütünlüğü ya da tez/dergi format kurallarına uygunluk konusunda son bir göz atılmasını '
        'istediğinizde kullanılır. Düzenlenmiş metin, değişiklik izleyici (track changes) ile teslim '
        'edilir.'
    ),
    ('akademik-danismanlik', 'anket-tasarimi'): (
        'Araştırmanıza uygun anket formu oluşturma desteği.',
        'Araştırmanıza uygun anket formu oluşturma desteği. Veri toplamaya başlamadan önce '
        'sorularınızın araştırma sorunuzu doğru ölçtüğünden emin olmak istediğinizde kullanılır. '
        'Gözden geçirilmiş anket formu ve madde bazlı geri bildirim alırsınız.'
    ),
    ('nitel-analiz', 'icerik-analizi'): (
        'Metin, görüşme ve doküman verilerinde sistematik içerik analizi.',
        'Metin, görüşme ve doküman verilerinde sistematik içerik analizi. Görüşme dökümü, doküman ya '
        'da açık uçlu anket yanıtlarınızı sistematik biçimde kategorilere ayırmak istediğinizde '
        'kullanılır. Kodlama şeması, kategori frekansları ve yorumlanmış bulgular raporlanır.'
    ),
    ('nitel-analiz', 'konu-analizi'): (
        'Veride tekrarlayan tema ve örüntülerin belirlenmesi.',
        'Veride tekrarlayan tema ve örüntülerin belirlenmesi. Verinizde tekrar eden tema ve '
        'örüntüleri ortaya çıkarmak, araştırma sorunuza bütüncül bir bakış kazanmak istediğinizde '
        'kullanılır. Tema haritası ve her temayı destekleyen örnek alıntılarla rapor teslim edilir.'
    ),
    ('nitel-analiz', 'maxqda'): (
        'MAXQDA yazılımıyla nitel veri kodlama ve analiz.',
        'MAXQDA yazılımıyla nitel veri kodlama ve analiz. Büyük hacimli nitel veriyi yazılım destekli, '
        'izlenebilir biçimde kodlamak istediğinizde kullanılır. MAXQDA proje dosyası ve kodlama '
        'raporu teslim edilir.'
    ),
    ('nitel-analiz', 'nvivo'): (
        'NVivo yazılımıyla nitel veri kodlama ve analiz.',
        'NVivo yazılımıyla nitel veri kodlama ve analiz. NVivo\'ya özgü sorgu ve görselleştirme '
        'araçlarından (kelime bulutu, kodlama karşılaştırma vb.) yararlanmak istediğinizde kullanılır. '
        'NVivo proje dosyası ve kodlama raporu teslim edilir.'
    ),
    ('veri-ve-yapay-zeka', 'veri-temizleme-buyuk-veri'): (
        'Büyük veri setlerinin temizlenmesi, birleştirilmesi ve işlenmesi.',
        'Büyük veri setlerinin temizlenmesi, birleştirilmesi ve işlenmesi. Veri setiniz büyük, '
        'dağınık ya da birden fazla kaynaktan geliyorsa ve analiz öncesi düzenli hale getirilmesi '
        'gerekiyorsa kullanılır. Temizlenmiş ve birleştirilmiş veri seti ile yapılan işlemlerin '
        'dökümü teslim edilir.'
    ),
    ('veri-ve-yapay-zeka', 'makine-ogrenmesi'): (
        'Sınıflandırma ve tahmin modelleri için makine öğrenmesi destekli analiz.',
        'Sınıflandırma ve tahmin modelleri için makine öğrenmesi destekli analiz. Elinizdeki veriyle '
        'otomatik tahmin ya da sınıflandırma yapan bir model kurmak, bunu bir uygulamaya entegre '
        'etmek istediğinizde kullanılır. Eğitilmiş model, performans metrikleri ve kullanım kılavuzu '
        'teslim edilir.'
    ),
    ('veri-ve-yapay-zeka', 'yapay-zeka-modelleme'): (
        'Araştırma ve uygulama projeleri için yapay zeka modeli geliştirme.',
        'Araştırma ve uygulama projeleri için yapay zeka modeli geliştirme. Araştırma ya da ürün '
        'fikrinizi bir yapay zeka modeliyle hayata geçirmek istediğinizde kullanılır. Model mimarisi, '
        'eğitim süreci dokümantasyonu ve çalışır kod teslim edilir.'
    ),
    ('veri-ve-yapay-zeka', 'nlp'): (
        'Metin madenciliği ve doğal dil işleme projelerinde destek.',
        'Metin madenciliği ve doğal dil işleme projelerinde destek. Metin verinizden (yorumlar, '
        'makaleler, sosyal medya vb.) otomatik anlam çıkarmak, sınıflandırmak ya da özetlemek '
        'istediğinizde kullanılır. İşlenmiş metin verisi, model çıktıları ve yöntem raporu teslim '
        'edilir.'
    ),
    ('veri-ve-yapay-zeka', 'python-veri-analizi'): (
        'Python ile veri işleme, analiz ve otomasyon.',
        'Python ile veri işleme, analiz ve otomasyon. Analizlerinizi tekrarlanabilir, '
        'otomatikleştirilebilir bir yapıda (kod olarak) almak istediğinizde kullanılır. Çalışır '
        'Python kodu (Jupyter Notebook/script) ve analiz çıktıları teslim edilir.'
    ),
    ('veri-ve-yapay-zeka', 'veri-gorsellestirme'): (
        'Power BI ve Tableau ile etkileşimli gösterge panelleri ve raporlama.',
        'Power BI ve Tableau ile etkileşimli gösterge panelleri ve raporlama. Verinizi karar '
        'vericilere ya da jüriye etkileşimli, anlaşılır bir gösterge panelinde sunmak istediğinizde '
        'kullanılır. Etkileşimli dashboard dosyası ve kullanım açıklaması teslim edilir.'
    ),
}


def expand_bodies(apps, schema_editor):
    ServicePageSection = apps.get_model('forum', 'ServicePageSection')
    for (page_slug, anchor), (old_body, new_body) in UPDATES.items():
        ServicePageSection.objects.filter(
            service_page__slug=page_slug, anchor=anchor, body=old_body,
        ).update(body=new_body)


def shrink_bodies(apps, schema_editor):
    ServicePageSection = apps.get_model('forum', 'ServicePageSection')
    for (page_slug, anchor), (old_body, new_body) in UPDATES.items():
        ServicePageSection.objects.filter(
            service_page__slug=page_slug, anchor=anchor, body=new_body,
        ).update(body=old_body)


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0172_servicepage_remaining_3'),
    ]

    operations = [
        migrations.RunPython(expand_bodies, shrink_bodies),
    ]
