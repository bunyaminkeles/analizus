from django.db import migrations


BADGES_TO_REMOVE = [
    'ilk-adim',
    'kurucu-uye',
    'beta-tester',
    'premium-uye',
    'populer-yazar',
    'begenilen-yazar',
    'quiz-sampiyonu',
    # views.py'de inline oluşturulan artık rozetler
    'basari',
    'uzmanlik',
    'hipotez-avcisi',
    'raporlama-guru',
]

BADGES_TO_UPDATE = [
    # Achievement badges - puan eşikleri yükseltildi
    {'slug': 'yukselen-yildiz', 'points_required': 100, 'description': '100 akademik puan kazandınız'},
    {'slug': 'aktif-katilimci', 'points_required': 500, 'description': '500 akademik puan kazandınız'},
    {'slug': 'bilgi-kaynagi', 'points_required': 1000, 'description': '1000 akademik puan kazandınız'},
    {'slug': 'uzman', 'points_required': 2500, 'description': '2500 akademik puan kazandınız - TEKLİF VEREBİLİR'},
    {'slug': 'profesor', 'points_required': 5000, 'description': '5000 akademik puan kazandınız'},
    {'slug': 'efsane', 'points_required': 10000, 'description': '10000 akademik puan kazandınız - TÜM YETKİLER'},
    # Quiz badges - eşikler yükseltildi
    {'slug': 'spss-uzmani', 'description': 'SPSS kategorisinde 50 doğru cevap'},
    {'slug': 'python-ninja', 'description': 'Python kategorisinde 50 doğru cevap'},
    {'slug': 'r-ustadi', 'description': 'R kategorisinde 50 doğru cevap'},
    {'slug': 'istatistik-ustasi', 'description': 'İstatistik kategorisinde 50 doğru cevap'},
    {'slug': 'metodoloji-gurusu', 'description': 'Metodoloji kategorisinde 50 doğru cevap'},
    {'slug': 'quiz-efsanesi', 'description': "Quiz'de toplam 1000 doğru cevap - TEKLİF VEREBİLİR"},
    # Participation badges - eşikler yükseltildi
    {'slug': 'yardimsever', 'description': '50 soruya cevap verdi'},
    {'slug': 'konu-acici', 'description': '20 konu açtı'},
    {'slug': 'cozum-ustasi', 'description': '25 kez "En Faydalı Cevap" aldı - TEKLİF VEREBİLİR'},
    # Güvenilir Üye - ilan açma hakkı kaldırıldı (description güncellendi)
    {'slug': 'guvenilir-uye', 'description': 'E-posta, telefon ve LinkedIn doğrulandı'},
]


def cleanup_badges(apps, schema_editor):
    Badge = apps.get_model('forum', 'Badge')

    # Kaldırılan rozetleri sil (kullanıcılardan M2M ilişkisi de otomatik temizlenir)
    Badge.objects.filter(slug__in=BADGES_TO_REMOVE).delete()

    # Kalan rozetlerin eşiklerini ve açıklamalarını güncelle
    for badge_data in BADGES_TO_UPDATE:
        data = badge_data.copy()
        slug = data.pop('slug')
        Badge.objects.filter(slug=slug).update(**data)


def reverse_cleanup(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0045_update_donation_tiers'),
    ]

    operations = [
        migrations.RunPython(cleanup_badges, reverse_cleanup),
    ]
