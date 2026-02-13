from django.core.management.base import BaseCommand
from trdizin.services.job_runner import cleanup_expired_s3_files

class Command(BaseCommand):
    help = 'Cleans up expired TR Dizin S3 files for jobs that did not result in an order.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='The number of days after which a file is considered expired.',
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(self.style.NOTICE(f'Starting cleanup of TR Dizin S3 files older than {days} days...'))
        
        deleted_count = cleanup_expired_s3_files(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'Cleanup complete. {deleted_count} files were deleted.'))
