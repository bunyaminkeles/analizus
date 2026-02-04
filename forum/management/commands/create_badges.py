from django.core.management.base import BaseCommand
from forum.models import Badge, Profile


class Command(BaseCommand):
    help = 'Varsayılan rozetleri oluşturur'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Rozetler oluşturuluyor...'))

        badges_data = [
            # ═══════════════════════════════════════════════════════════════
            # BAŞARI ROZETLERİ (Akademik Puana Göre Otomatik)
            # ═══════════════════════════════════════════════════════════════
            {
                'name': 'Yükselen Yıldız',
                'slug': 'yukselen-yildiz',
                'description': '100 akademik puan kazandınız',
                'icon': 'bi-star',
                'color': '#3b82f6',
                'badge_type': 'achievement',
                'points_required': 100,
            },
            {
                'name': 'Aktif Katılımcı',
                'slug': 'aktif-katilimci',
                'description': '500 akademik puan kazandınız',
                'icon': 'bi-lightning',
                'color': '#8b5cf6',
                'badge_type': 'achievement',
                'points_required': 500,
            },
            {
                'name': 'Bilgi Kaynağı',
                'slug': 'bilgi-kaynagi',
                'description': '1000 akademik puan kazandınız',
                'icon': 'bi-book',
                'color': '#f59e0b',
                'badge_type': 'achievement',
                'points_required': 1000,
            },
            {
                'name': 'Uzman',
                'slug': 'uzman',
                'description': '2500 akademik puan kazandınız - TEKLİF VEREBİLİR',
                'icon': 'bi-mortarboard',
                'color': '#ef4444',
                'badge_type': 'achievement',
                'points_required': 2500,
            },
            {
                'name': 'Profesör',
                'slug': 'profesor',
                'description': '5000 akademik puan kazandınız',
                'icon': 'bi-award',
                'color': '#dc2626',
                'badge_type': 'achievement',
                'points_required': 5000,
            },
            {
                'name': 'Efsane',
                'slug': 'efsane',
                'description': '10000 akademik puan kazandınız - TÜM YETKİLER',
                'icon': 'bi-trophy',
                'color': '#eab308',
                'badge_type': 'achievement',
                'points_required': 10000,
            },

            # ═══════════════════════════════════════════════════════════════
            # UZMANLIK ROZETLERİ (Quiz Kategorilerine Göre Otomatik)
            # ═══════════════════════════════════════════════════════════════
            {
                'name': 'SPSS Uzmanı',
                'slug': 'spss-uzmani',
                'description': 'SPSS kategorisinde 50 doğru cevap',
                'icon': 'bi-bar-chart-fill',
                'color': '#0ea5e9',
                'badge_type': 'specialty',
                'points_required': 0,
            },
            {
                'name': 'Python Ninja',
                'slug': 'python-ninja',
                'description': 'Python kategorisinde 50 doğru cevap',
                'icon': 'bi-filetype-py',
                'color': '#3b82f6',
                'badge_type': 'specialty',
                'points_required': 0,
            },
            {
                'name': 'R Üstadı',
                'slug': 'r-ustadi',
                'description': 'R kategorisinde 50 doğru cevap',
                'icon': 'bi-graph-up',
                'color': '#2563eb',
                'badge_type': 'specialty',
                'points_required': 0,
            },
            {
                'name': 'İstatistik Ustası',
                'slug': 'istatistik-ustasi',
                'description': 'İstatistik kategorisinde 50 doğru cevap',
                'icon': 'bi-calculator',
                'color': '#7c3aed',
                'badge_type': 'specialty',
                'points_required': 0,
            },
            {
                'name': 'Quiz Efsanesi',
                'slug': 'quiz-efsanesi',
                'description': 'Quiz\'de toplam 1000 doğru cevap - TEKLİF VEREBİLİR',
                'icon': 'bi-star-fill',
                'color': '#f59e0b',
                'badge_type': 'specialty',
                'points_required': 0,
            },

            # ═══════════════════════════════════════════════════════════════
            # KATILIM ROZETLERİ (Forum Aktivitesine Göre Otomatik)
            # ═══════════════════════════════════════════════════════════════
            {
                'name': 'Yardımsever',
                'slug': 'yardimsever',
                'description': '50 soruya cevap verdi',
                'icon': 'bi-heart',
                'color': '#ec4899',
                'badge_type': 'participation',
                'points_required': 0,
            },
            {
                'name': 'Konu Açıcı',
                'slug': 'konu-acici',
                'description': '20 konu açtı',
                'icon': 'bi-chat-square-text',
                'color': '#06b6d4',
                'badge_type': 'participation',
                'points_required': 0,
            },
            {
                'name': 'En İyi Cevap',
                'slug': 'en-iyi-cevap',
                'description': 'Bir cevabı "En Faydalı" seçildi',
                'icon': 'bi-check-circle',
                'color': '#22c55e',
                'badge_type': 'participation',
                'points_required': 0,
            },
            {
                'name': 'Çözüm Ustası',
                'slug': 'cozum-ustasi',
                'description': '25 kez "En Faydalı Cevap" aldı - TEKLİF VEREBİLİR',
                'icon': 'bi-patch-check',
                'color': '#10b981',
                'badge_type': 'participation',
                'points_required': 0,
            },

            # ═══════════════════════════════════════════════════════════════
            # ÖZEL ROZETLER (Manuel Verilir veya Doğrulama ile)
            # ═══════════════════════════════════════════════════════════════
            {
                'name': 'Güvenilir Üye',
                'slug': 'guvenilir-uye',
                'description': 'E-posta, telefon ve LinkedIn doğrulandı',
                'icon': 'bi-shield-check',
                'color': '#14b8a6',
                'badge_type': 'special',
                'points_required': 0,
            },
            {
                'name': 'Moderatör',
                'slug': 'moderator',
                'description': 'Forum moderatörü - TÜM YETKİLER',
                'icon': 'bi-shield-fill-check',
                'color': '#dc2626',
                'badge_type': 'special',
                'points_required': 0,
            },
            {
                'name': 'Doğrulanmış Akademisyen',
                'slug': 'dogrulanmis-akademisyen',
                'description': 'Akademik kimliği doğrulandı - TÜM YETKİLER',
                'icon': 'bi-patch-check-fill',
                'color': '#0ea5e9',
                'badge_type': 'special',
                'points_required': 0,
            },
        ]

        created_count = 0
        updated_count = 0

        for badge_data in badges_data:
            badge, created = Badge.objects.update_or_create(
                slug=badge_data['slug'],
                defaults=badge_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        # Mevcut kullanıcılara puana göre rozet ver
        self.stdout.write('Kullanıcılara otomatik rozetler veriliyor...')
        for profile in Profile.objects.all():
            profile.check_and_award_badges()
            profile.update_rank()

        self.stdout.write(self.style.SUCCESS(f'''
══════════════════════════════════════════════════════════════════
                    ROZET SİSTEMİ HAZIR!
══════════════════════════════════════════════════════════════════
  Yeni Rozet: {created_count}
  Güncellenen: {updated_count}
  Toplam Rozet: {Badge.objects.count()}
══════════════════════════════════════════════════════════════════
                      ROZET YETKİLERİ
══════════════════════════════════════════════════════════════════
  TEKLİF VEREBİLİR:
    * Uzman (2500 puan)
    * Profesör (5000 puan)
    * Efsane (10000 puan)
    * Çözüm Ustası (25 en iyi cevap)
    * Quiz Efsanesi (1000 quiz doğru)
    * Doğrulanmış Akademisyen
    * Moderatör
    * Premium hesap (account_type)
══════════════════════════════════════════════════════════════════
        '''))
