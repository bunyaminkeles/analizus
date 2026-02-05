"""
Veritabanı temizlik komutu - Neon kapasite yönetimi için.

Kullanım:
    python manage.py cleanup_database          # Normal temizlik
    python manage.py cleanup_database --dry-run # Önizleme (silmeden)
    python manage.py cleanup_database --aggressive # Daha agresif temizlik

Otomatik çalıştırma (cron):
    0 3 * * * cd /app && python manage.py cleanup_database >> /var/log/cleanup.log 2>&1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import connection


class Command(BaseCommand):
    help = 'Eski verileri temizleyerek veritabanı boyutunu küçültür (Neon kapasite yönetimi)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Silmeden önce kaç kayıt silineceğini göster',
        )
        parser.add_argument(
            '--aggressive',
            action='store_true',
            help='Daha agresif temizlik (15 gün yerine 7 gün)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        aggressive = options['aggressive']

        # Temizlik süreleri
        notification_days = 7 if aggressive else 30
        session_days = 7 if aggressive else 14
        verification_days = 1 if aggressive else 3
        quiz_attempt_days = 30 if aggressive else 90

        now = timezone.now()
        total_deleted = 0

        self.stdout.write(self.style.HTTP_INFO('=' * 50))
        self.stdout.write(self.style.HTTP_INFO('VERITABANI TEMİZLİK RAPORU'))
        self.stdout.write(self.style.HTTP_INFO(f'Tarih: {now.strftime("%Y-%m-%d %H:%M")}'))
        self.stdout.write(self.style.HTTP_INFO(f'Mod: {"DRY-RUN (önizleme)" if dry_run else "GERÇEK"}'))
        self.stdout.write(self.style.HTTP_INFO('=' * 50))

        # 1. Eski bildirimleri temizle (okunmuş ve X günden eski)
        total_deleted += self._cleanup_notifications(now, notification_days, dry_run)

        # 2. Eski email verification tokenlarını temizle
        total_deleted += self._cleanup_email_verifications(now, verification_days, dry_run)

        # 3. Eski session'ları temizle
        total_deleted += self._cleanup_sessions(dry_run)

        # 4. Eski quiz denemelerini temizle (opsiyonel - istatistik için saklanabilir)
        total_deleted += self._cleanup_quiz_attempts(now, quiz_attempt_days, dry_run)

        # 5. Django içerik tiplerini temizle (orphan kayıtlar)
        total_deleted += self._cleanup_orphan_content_types(dry_run)

        # Özet
        self.stdout.write(self.style.HTTP_INFO('=' * 50))
        if dry_run:
            self.stdout.write(self.style.WARNING(f'TOPLAM SİLİNECEK: {total_deleted} kayıt'))
            self.stdout.write(self.style.WARNING('--dry-run olmadan çalıştırarak gerçek silme yapabilirsiniz.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'TOPLAM SİLİNEN: {total_deleted} kayıt'))

            # VACUUM öner
            self.stdout.write(self.style.HTTP_INFO('-' * 50))
            self.stdout.write(self.style.NOTICE(
                'NOT: Silinen alanı geri kazanmak için Neon konsolundan '
                'VACUUM FULL çalıştırmanız önerilir.'
            ))

    def _cleanup_notifications(self, now, days, dry_run):
        """Eski okunmuş bildirimleri temizle"""
        from forum.models import Notification

        cutoff = now - timedelta(days=days)
        queryset = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff
        )
        count = queryset.count()

        if count > 0:
            if not dry_run:
                queryset.delete()
            self.stdout.write(
                f'  [Notification] {count} eski okunmuş bildirim ({days} günden eski) '
                f'{"silinecek" if dry_run else "silindi"}'
            )
        else:
            self.stdout.write(f'  [Notification] Temizlenecek kayıt yok')

        return count

    def _cleanup_email_verifications(self, now, days, dry_run):
        """Kullanılmış veya süresi dolmuş email doğrulama tokenlarını temizle"""
        from forum.models import EmailVerification

        cutoff = now - timedelta(days=days)
        queryset = EmailVerification.objects.filter(
            is_used=True
        ) | EmailVerification.objects.filter(
            expires_at__lt=now,
            created_at__lt=cutoff
        )
        count = queryset.count()

        if count > 0:
            if not dry_run:
                queryset.delete()
            self.stdout.write(
                f'  [EmailVerification] {count} eski/kullanılmış token '
                f'{"silinecek" if dry_run else "silindi"}'
            )
        else:
            self.stdout.write(f'  [EmailVerification] Temizlenecek kayıt yok')

        return count

    def _cleanup_sessions(self, dry_run):
        """Süresi dolmuş session'ları temizle"""
        from django.contrib.sessions.models import Session

        now = timezone.now()
        queryset = Session.objects.filter(expire_date__lt=now)
        count = queryset.count()

        if count > 0:
            if not dry_run:
                queryset.delete()
            self.stdout.write(
                f'  [Session] {count} süresi dolmuş session '
                f'{"silinecek" if dry_run else "silindi"}'
            )
        else:
            self.stdout.write(f'  [Session] Temizlenecek kayıt yok')

        return count

    def _cleanup_quiz_attempts(self, now, days, dry_run):
        """Eski quiz denemelerini temizle (QuizScore'daki özet veriler korunur)"""
        from forum.models import UserQuizAttempt

        cutoff = now - timedelta(days=days)
        queryset = UserQuizAttempt.objects.filter(created_at__lt=cutoff)
        count = queryset.count()

        if count > 0:
            if not dry_run:
                queryset.delete()
            self.stdout.write(
                f'  [UserQuizAttempt] {count} eski quiz denemesi ({days} günden eski) '
                f'{"silinecek" if dry_run else "silindi"}'
            )
        else:
            self.stdout.write(f'  [UserQuizAttempt] Temizlenecek kayıt yok')

        return count

    def _cleanup_orphan_content_types(self, dry_run):
        """Orphan content type kayıtlarını temizle (GenericForeignKey'lerden kalan)"""
        # Bu daha karmaşık bir işlem, şimdilik pas geç
        # İleride eklenebilir
        return 0

    def _get_db_size(self):
        """Veritabanı boyutunu döndür (sadece PostgreSQL için)"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                return cursor.fetchone()[0]
        except Exception:
            return "Bilinmiyor"
