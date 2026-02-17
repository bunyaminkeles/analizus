from django.core.management.base import BaseCommand
from openalex.services.job_runner import cleanup_expired_openalex_s3_files


class Command(BaseCommand):
    help = 'OpenAlex S3 dosyalarını temizler (varsayılan: 3 günden eski)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=3, help='Kaç günden eski dosyalar silinsin')

    def handle(self, *args, **options):
        days = options['days']
        deleted = cleanup_expired_openalex_s3_files(days=days)
        self.stdout.write(self.style.SUCCESS(f'{deleted} dosya silindi (openalex, {days} günden eski)'))
