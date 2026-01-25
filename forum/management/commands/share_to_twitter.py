"""
Twitter Paylaşım Management Komutu

Kullanım:
    python manage.py share_to_twitter --daily-tip      # Günün ipucunu paylaş
    python manage.py share_to_twitter --topic 123      # Belirli konuyu paylaş
    python manage.py share_to_twitter --recent-topics  # Son 24 saat konularını paylaş
    python manage.py share_to_twitter --test           # Bağlantıyı test et
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Twitter\'da içerik paylaş'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daily-tip',
            action='store_true',
            help='Günün ipucunu paylaş'
        )
        parser.add_argument(
            '--topic',
            type=int,
            help='Belirli bir konuyu paylaş (Topic ID)'
        )
        parser.add_argument(
            '--recent-topics',
            action='store_true',
            help='Son 24 saat içinde açılan konuları paylaş'
        )
        parser.add_argument(
            '--job',
            type=int,
            help='Belirli bir iş ilanını paylaş (Job ID)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Twitter bağlantısını test et'
        )

    def handle(self, *args, **options):
        from forum.services.twitter_service import (
            get_twitter_service,
            format_topic_tweet,
            format_daily_tip_tweet,
            format_job_tweet
        )
        from forum.models import Topic, DailyTip, FreelanceJob

        service = get_twitter_service()
        site_url = getattr(settings, 'SITE_URL', 'https://analizus.com')

        # Bağlantı testi
        if options['test']:
            if service.is_available():
                self.stdout.write(self.style.SUCCESS('✅ Twitter bağlantısı başarılı!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Twitter bağlantısı kurulamadı. API anahtarlarını kontrol edin.'))
            return

        if not service.is_available():
            self.stdout.write(self.style.ERROR('❌ Twitter servisi kullanılamıyor.'))
            return

        # Günün ipucu
        if options['daily_tip']:
            tip = DailyTip.get_today_tip()
            if tip:
                tweet_text = format_daily_tip_tweet(tip, site_url)
                result = service.post_tweet(tweet_text)
                if result.success:
                    self.stdout.write(self.style.SUCCESS(f'✅ Günün ipucu paylaşıldı: {result.tweet_url}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Hata: {result.error}'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Bugün için ipucu bulunamadı.'))
            return

        # Belirli konu
        if options['topic']:
            try:
                topic = Topic.objects.get(pk=options['topic'])
                tweet_text = format_topic_tweet(topic, site_url)
                result = service.post_tweet(tweet_text)
                if result.success:
                    self.stdout.write(self.style.SUCCESS(f'✅ Konu paylaşıldı: {result.tweet_url}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Hata: {result.error}'))
            except Topic.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Konu bulunamadı: #{options["topic"]}'))
            return

        # Son 24 saat konuları
        if options['recent_topics']:
            yesterday = timezone.now() - timedelta(days=1)
            topics = Topic.objects.filter(created_at__gte=yesterday).order_by('-created_at')

            if not topics.exists():
                self.stdout.write(self.style.WARNING('⚠️ Son 24 saatte konu açılmamış.'))
                return

            shared = 0
            for topic in topics[:5]:  # Max 5 konu paylaş (rate limit)
                tweet_text = format_topic_tweet(topic, site_url)
                result = service.post_tweet(tweet_text)
                if result.success:
                    shared += 1
                    self.stdout.write(f'  ✅ {topic.subject[:50]}...')

            self.stdout.write(self.style.SUCCESS(f'\n🐦 {shared}/{topics.count()} konu paylaşıldı.'))
            return

        # Belirli iş ilanı
        if options['job']:
            try:
                job = FreelanceJob.objects.get(pk=options['job'])
                tweet_text = format_job_tweet(job, site_url)
                result = service.post_tweet(tweet_text)
                if result.success:
                    self.stdout.write(self.style.SUCCESS(f'✅ İlan paylaşıldı: {result.tweet_url}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Hata: {result.error}'))
            except FreelanceJob.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ İlan bulunamadı: #{options["job"]}'))
            return

        # Hiçbir seçenek verilmediyse yardım göster
        self.stdout.write(self.style.WARNING('Kullanım:'))
        self.stdout.write('  python manage.py share_to_twitter --test')
        self.stdout.write('  python manage.py share_to_twitter --daily-tip')
        self.stdout.write('  python manage.py share_to_twitter --topic 123')
        self.stdout.write('  python manage.py share_to_twitter --recent-topics')
        self.stdout.write('  python manage.py share_to_twitter --job 45')
