"""
Admin kullanıcısı adına 4 tohum çalışma odası oluşturur.
Kullanım: python manage.py seed_study_rooms
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


ROOMS = [
    {
        'title': 'SEM ile Yapısal Eşitlik Modelleri — 2026 Bahar',
        'category_slug': 'yapisal-esitlik',
        'description': (
            'Yapısal eşitlik modellemesi (SEM) üzerine dönemlik bir çalışma grubu. '
            'AMOS, R lavaan veya SmartPLS kullananlar için hem teknik hem de yorumlama '
            'tartışmalarının yapıldığı, örnek analizlerin paylaşıldığı bir oda.'
        ),
        'goal': 'Dönem sonuna kadar en az 3 farklı SEM modeli örneği incelemek, '
                'varsayım testlerini ve uyum indekslerini birlikte çalışmak.',
        'creator_bio': 'Doktora öğrencisiyim, tez analizimde SEM kullanıyorum. '
                       'Hem öğrenmek hem de deneyimimi paylaşmak için bu odayı açtım.',
        'days': 85,
        'max_members': 25,
        'starter_posts': [
            'Merhaba herkese! Bu odayı SEM ile uğraşan herkese açık bir paylaşım alanı '
            'olarak düşündüm. Hangi yazılımı kullanıyorsunuz — AMOS, lavaan veya SmartPLS?',
            'Başlangıç olarak şunu paylaşayım: SEM\'de model uyumunu değerlendirirken '
            'CFI > 0.90, RMSEA < 0.08, SRMR < 0.08 kriterlerine bakıyoruz. '
            'Ama bu eşikler mutlak değil — örneklem büyüklüğü ve model karmaşıklığı da etkiler.',
            'Bu hafta için küçük bir ödev: Kullandığınız SEM modelinin uyum indekslerini ve '
            'hangi düzeltmeleri yaptığınızı kısaca paylaşır mısınız?',
        ],
    },
    {
        'title': 'Bibliometrik Analiz Atölyesi',
        'category_slug': 'bibliometrik-analizler',
        'description': (
            'Bibliometrik analiz yapanlar için pratik bir atölye odası. '
            'VOSviewer, Bibliometrix (R), CiteSpace kullanımı; ortak atıf analizi, '
            'kelime bulutu, işbirliği haritaları ve trend analizleri tartışılıyor.'
        ),
        'goal': 'Dönem içinde en az bir tam bibliometrik analiz akışını (veri toplama → '
                'temizleme → analiz → görselleştirme) birlikte tamamlamak.',
        'creator_bio': 'Akademik yazım ve literatür tarama konusunda deneyimliyim. '
                       'Bibliometrik yöntemleri öğrenenlerle birlikte ilerlemeyi seviyorum.',
        'days': 60,
        'max_members': 20,
        'starter_posts': [
            'Bu odada bibliometrik analizin pratik kısmını konuşacağız. '
            'Hangi veri tabanını kullanıyorsunuz — Web of Science, Scopus veya OpenAlex?',
            'VOSviewer\'ın en sık yapılan hatası: analiz öncesinde anahtar kelimeleri '
            'temizlememek. "machine learning" ile "Machine Learning" ayrı düğümler olarak '
            'görünür. Mutlaka thesaurus dosyası hazırlayın.',
            'Analizus\'taki OpenAlex Tarama aracıyla 500+ kayıt çekip buraya atabilirsiniz. '
            'Birlikte üzerinde çalışalım.',
        ],
    },
    {
        'title': 'SPSS Başlangıç — Soru & Cevap',
        'category_slug': 'spss-amos',
        'description': (
            'SPSS\'e yeni başlayanlar veya temel analizlerde takılanlar için '
            'açık kapı soru-cevap odası. Veri girişinden t-testine, ANOVA\'dan '
            'regresyona kadar tüm temel konular burada sorulabilir.'
        ),
        'goal': 'Odaya katılan her üyenin en az bir analizini SPSS\'te tamamlamasına yardımcı olmak.',
        'creator_bio': 'SPSS kullanımı konusunda yıllarca öğrencilere destek verdim. '
                       'Temel sorular için buradayım.',
        'days': 75,
        'max_members': 30,
        'starter_posts': [
            'SPSS\'te çalışırken en sık karşılaşılan sorun nedir sizce? '
            'Benim gördüğüm en yaygın: veri görünümü ile değişken görünümü farkını '
            'anlamamak. Değişken görünümünde ölçek türünü doğru seçmek çok önemli.',
            'Küçük bir SPSS ipucu: Analyze menüsünden Descriptive Statistics → Explore '
            'yolunu izlerseniz hem tanımlayıcı istatistikler hem de normallik testlerini '
            'tek seferde alırsınız. Shapiro-Wilk\'ı da oradan açabilirsiniz.',
            'Hangi analizi yapmak istediğinizi buraya yazın, adım adım anlatalım.',
        ],
    },
    {
        'title': 'Tez Yazım Süreci — Destek Grubu',
        'category_slug': 'tez-danismanligi',
        'description': (
            'Tez yazan, tez yazacak veya tez savunması hazırlayan herkes için '
            'duygusal ve teknik destek odası. Motivasyon, zaman yönetimi, '
            'danışman ilişkisi, literatür tarama ve yazım süreci burada konuşuluyor.'
        ),
        'goal': 'Tez sürecindeki engelleri birlikte aşmak; haftada en az bir somut '
                'ilerleme paylaşmak.',
        'creator_bio': 'Tez sürecinde çok zorlandım ve yalnız hissetmenin ne demek '
                       'olduğunu biliyorum. Bu oda bunun için var.',
        'days': 90,
        'max_members': 20,
        'starter_posts': [
            'Tez yazarken en büyük düşman ertelemedir. Küçük bir öneri: '
            '"tezimi yazacağım" yerine "bugün sadece giriş bölümünün ilk paragrafını yazacağım" '
            'deyin. Küçük hedefler büyük ilerleme sağlar.',
            'Bu haftaki paylaşım: Tez sürecinde nerede takıldınız? '
            'Metodoloji mi, literatür tarama mı, danışman iletişimi mi? '
            'Buraya yazın, birlikte düşünelim.',
            'Bir hatırlatma: Etik kurul başvurusu ve ORCID kaydı gibi idari işleri '
            'ertelemeyin. Bunlar beklenmedik zaman alıyor.',
        ],
    },
]


class Command(BaseCommand):
    help = '4 tohum çalışma odası oluşturur (admin kullanıcısı adına).'

    def handle(self, *args, **options):
        from forum.models import StudyRoom, StudyRoomMembership, StudyRoomPost, Category

        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stderr.write('Superuser bulunamadı.')
            return

        created = 0
        for data in ROOMS:
            if StudyRoom.objects.filter(title=data['title']).exists():
                self.stdout.write(f'  ATLA (zaten var): {data["title"]}')
                continue

            category = Category.objects.filter(slug=data['category_slug']).first()
            ends_at = timezone.now() + timedelta(days=data['days'])

            room = StudyRoom.objects.create(
                title=data['title'],
                description=data['description'],
                goal=data['goal'],
                creator_bio=data.get('creator_bio', ''),
                category=category,
                creator=admin,
                ends_at=ends_at,
                max_members=data['max_members'],
                is_public=True,
                status='active',
                terms_agreed=True,
                terms_agreed_at=timezone.now(),
            )

            StudyRoomMembership.objects.create(room=room, user=admin, role='creator')

            for msg in data.get('starter_posts', []):
                StudyRoomPost.objects.create(room=room, author=admin, message=msg)

            created += 1
            self.stdout.write(self.style.SUCCESS(f'  OLUŞTURULDU: {room.title}'))

        self.stdout.write(self.style.SUCCESS(f'\n{created} oda oluşturuldu.'))
