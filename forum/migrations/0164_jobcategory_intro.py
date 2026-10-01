from django.db import migrations, models

# Uzman Dizini kategori sayfaları (/uzmanlar/?cat=<id>) — GSC "Google farklı canonical seçti":
# başlık/içerik /uzmanlar/ ile aynıydı. Kategoriye özgü tanıtım metni; kimlikler ortamlar arasında
# farklı olduğu için başlığa göre doldurulur, alan doluysa dokunulmaz.
INTROS = {
    'AMOS (Path analizi)': (
        'AMOS, yapısal eşitlik modellemesi (YEM) ve yol (path) analizi için kullanılan bir yazılımdır; '
        'doğrulayıcı faktör analizi, aracılık ve düzenleyicilik modellerinin kurulması ile uyum indekslerinin '
        '(CFI, RMSEA, SRMR vb.) yorumlanması bu alanın konusudur. AMOS ile model kurma ve raporlama konusunda '
        'destek veren uzmanlar aşağıda listelenir.'
    ),
    'EViews analizleri': (
        'EViews, zaman serisi ve panel veri analizinde yaygın kullanılan bir ekonometri yazılımıdır; birim kök '
        've eşbütünleşme testleri, ARDL, VAR ve panel regresyon modelleri bu alanın tipik konularıdır. '
        'Ekonometrik modelin kurulması, sınanması ve sonuçların yorumlanması için destek veren uzmanlar aşağıdadır.'
    ),
    'Makine öğrenmesi modellemesi': (
        'Makine öğrenmesi modellemesi; sınıflandırma, regresyon ve kümeleme problemleri için veri ön işleme, '
        'model seçimi, hiperparametre ayarı ve çapraz doğrulamayla model başarısının değerlendirilmesini kapsar. '
        'Akademik çalışmanız veya projeniz için makine öğrenmesi desteği veren uzmanlar aşağıda listelenir.'
    ),
    'SPSS ile veri analizi': (
        'SPSS, sosyal ve sağlık bilimlerindeki tez ve makalelerde en sık kullanılan istatistik programlarından '
        'biridir; betimsel istatistikler, t-testi, ANOVA, korelasyon, regresyon ve güvenirlik analizleri bu '
        'kapsamdadır. Analizin yapılması, SPSS çıktılarının yorumlanması ve APA formatında raporlanması için '
        'destek veren uzmanlar aşağıdadır.'
    ),
    'Akademik danışmanlık': (
        'Akademik danışmanlık; araştırma sorusunun netleştirilmesi, yöntem seçimi, literatür taraması ve tez ya '
        'da makale sürecinin planlanmasında rehberlik anlamına gelir. Çalışmanın özgün emeği araştırmacıya '
        'aittir; uzmanlar süreci yönlendirir ve geri bildirim verir.'
    ),
    'NLP Modelleme': (
        'Doğal dil işleme (NLP); metin sınıflandırma, duygu analizi, konu modelleme ve adlandırılmış varlık '
        'tanıma gibi yöntemlerle metin verisinden bilgi çıkarılmasını kapsar. Açık uçlu anket yanıtları, sosyal '
        'medya verisi veya akademik metinler üzerinde NLP desteği veren uzmanlar aşağıda listelenir.'
    ),
    'Metin Editörlüğü': (
        'Akademik metin editörlüğü; tez, makale ve proje metinlerinde dil ve anlatımın, yazım kurallarının, '
        'akademik üslubun, kaynak gösterimi ve biçim kurallarına (APA vb.) uygunluğun gözden geçirilmesidir. '
        'Editörlük metnin içeriğini değiştirmez; anlatımın açık ve tutarlı olmasına yardımcı olur.'
    ),
    'Tez önerisi desteği': (
        'Tez önerisi; araştırma probleminin, amacın, önemin, yöntemin ve zaman planının enstitüye sunulmak '
        'üzere yazıldığı belgedir. Konunun daraltılması, araştırma soruları ile yöntemin tutarlılığı ve '
        'literatür çerçevesinin kurulması konusunda geri bildirim veren uzmanlar aşağıdadır.'
    ),
    'Etik kurul desteği': (
        'Etik kurul başvurusu; araştırmanın amacı, katılımcılar, veri toplama araçları, bilgilendirilmiş onam ve '
        'veri güvenliğine ilişkin belgelerin hazırlanmasını gerektirir. Başvuru dosyasının eksiksiz ve kurumun '
        'beklediği biçimde hazırlanması için destek veren uzmanlar aşağıda listelenir.'
    ),
    'Excel analizleri': (
        'Excel; veri temizleme, pivot tablolar, formüllerle hesaplama, grafikler ve Veri Çözümleme eklentisiyle '
        'temel istatistiksel analizler için kullanılır. Verinin düzenlenmesi, raporlanması veya Excel tabanlı '
        'analizler için destek veren uzmanlar aşağıdadır.'
    ),
    'SmartPLS analizleri': (
        'SmartPLS, kısmi en küçük kareler yöntemine dayalı yapısal eşitlik modellemesi (PLS-SEM) için kullanılan '
        'bir yazılımdır; ölçüm modelinin değerlendirilmesi (güvenirlik, birleşme ve ayırt edici geçerlik), '
        'yapısal model, aracılık ve düzenleyicilik analizleri bu alanın konusudur. SmartPLS ile model kurma ve '
        'raporlama desteği veren uzmanlar aşağıda listelenir.'
    ),
    'Güç analizi (Power analizi)': (
        'Güç (power) analizi, bir çalışmada beklenen etkiyi saptayabilmek için gereken örneklem büyüklüğünü '
        'hesaplamaya yarar; G*Power gibi araçlarla etki büyüklüğü, anlamlılık düzeyi ve istenen güce göre '
        'yapılır. Tez ve proje önerilerinde örneklem gerekçesinin hazırlanması için destek veren uzmanlar '
        'aşağıdadır.'
    ),
    'Tableau ile veri analizi': (
        'Tableau, verilerin etkileşimli grafikler ve gösterge panoları (dashboard) ile görselleştirilmesi için '
        'kullanılan bir iş zekâsı aracıdır. Verinin Tableau\'ya hazırlanması, panoların tasarlanması ve '
        'bulguların görsel olarak sunulması için destek veren uzmanlar aşağıda listelenir.'
    ),
    'Büyük veri analizi': (
        'Büyük veri analizi; tek bir bilgisayarın belleğine sığmayan ya da hızla üretilen verilerin uygun '
        'araçlarla (Python, SQL, dağıtık işleme çerçeveleri vb.) işlenmesini, özetlenmesini ve modellenmesini '
        'kapsar. Büyük ölçekli veri setleriyle çalışma konusunda destek veren uzmanlar aşağıdadır.'
    ),
    'Stata ile veri analizi': (
        'Stata; ekonometri, sağlık ve sosyal bilimlerde regresyon modelleri, panel veri, sağkalım analizi ve '
        'tekrarlanabilir komut dosyaları (do-file) için kullanılan bir istatistik yazılımıdır. Stata ile analiz '
        'yapılması ve sonuçların yorumlanması konusunda destek veren uzmanlar aşağıda listelenir.'
    ),
    'NVIVO ile nitel veri analizi': (
        'NVivo, görüşme dökümleri, açık uçlu yanıtlar ve belgeler gibi nitel verilerin kodlanması, '
        'temalandırılması ve görselleştirilmesi için kullanılan bir nitel veri analizi yazılımıdır. Tematik '
        'analiz, içerik analizi ve kodlama sürecinde NVivo desteği veren uzmanlar aşağıdadır.'
    ),
    'MAXQDA ile nitel veri analizi': (
        'MAXQDA, nitel ve karma yöntem araştırmalarında görüşme, odak grup ve doküman verilerinin kodlanması, '
        'kod sistemlerinin oluşturulması ve temaların görselleştirilmesi için kullanılan bir yazılımdır. MAXQDA '
        'ile içerik analizi ve tematik analiz konusunda destek veren uzmanlar aşağıda listelenir.'
    ),
    'Python ile veri analizi': (
        'Python; pandas, NumPy, SciPy, statsmodels ve scikit-learn gibi kütüphanelerle veri temizleme, '
        'istatistiksel analiz, görselleştirme ve modelleme için kullanılan bir programlama dilidir. Analizin '
        'Python ile yapılması ve tekrarlanabilir kod hazırlanması için destek veren uzmanlar aşağıdadır.'
    ),
    'Geçerlik & güvenirlik analizleri': (
        'Geçerlik ve güvenirlik analizleri, bir ölçme aracının ölçmek istediği yapıyı tutarlı ve doğru biçimde '
        'ölçüp ölçmediğini sınar; Cronbach alfa, açımlayıcı ve doğrulayıcı faktör analizi, birleşme ve ayırt '
        'edici geçerlik bu kapsamdadır. Ölçek geliştirme ve uyarlama çalışmalarında destek veren uzmanlar '
        'aşağıda listelenir.'
    ),
    'Python eğitimi': (
        'Python eğitimi; temel programlama, veri yapıları ve veri analizi kütüphanelerinin kullanımını '
        'uygulamalı olarak öğrenmek isteyen araştırmacılara yöneliktir. Birebir ya da grup hâlinde Python '
        'eğitimi veren uzmanlar aşağıdadır.'
    ),
}


def fill_intros(apps, schema_editor):
    JobCategory = apps.get_model('forum', 'JobCategory')
    for title, intro in INTROS.items():
        n = JobCategory.objects.filter(title=title, intro='').update(intro=intro)
        print(f"  {'✓' if n else '='} {title}")


def clear_intros(apps, schema_editor):
    JobCategory = apps.get_model('forum', 'JobCategory')
    for title, intro in INTROS.items():
        JobCategory.objects.filter(title=title, intro=intro).update(intro='')


class Migration(migrations.Migration):
    dependencies = [('forum', '0163_blog_seo_icerik_duzeltme')]
    operations = [
        migrations.AddField(
            model_name='jobcategory',
            name='intro',
            field=models.TextField(
                blank=True, default='', verbose_name='Tanıtım metni',
                help_text="Uzman Dizini'nde bu kategori seçildiğinde başlığın altında görünür (2 cümle önerilir).",
            ),
        ),
        migrations.RunPython(fill_intros, clear_intros),
    ]
