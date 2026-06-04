from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from analytics.models import PageView, PageViewSummary

DEFAULT_RETENTION_DAYS = 5


class Command(BaseCommand):
    help = 'Eski sayfa ziyaret loglarını özetleyip siler (varsayılan: 5 gün)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=DEFAULT_RETENTION_DAYS,
                            help='Kaç günden eski kayıtlar silinsin (varsayılan: 5)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Silme yapmadan sadece sayıları göster')

    def handle(self, *args, **options):
        cutoff = date.today() - timedelta(days=options['days'])
        old_qs = PageView.objects.filter(timestamp__date__lt=cutoff)
        total_old = old_qs.count()

        if total_old == 0:
            self.stdout.write('Silinecek eski kayıt yok.')
            return

        aggregates = list(
            old_qs
            .values('timestamp__date', 'path', 'tab_name')
            .annotate(
                visit_count=Count('id'),
                unique_users=Count('user_id', distinct=True),
            )
        )

        if options['dry_run']:
            self.stdout.write(
                f'[Dry-run] {total_old} ham kayıt silinecek, '
                f'{len(aggregates)} özet satırı oluşturulacak/güncellenecek.'
            )
            return

        with transaction.atomic():
            upserted = 0
            for row in aggregates:
                obj, created = PageViewSummary.objects.get_or_create(
                    date=row['timestamp__date'],
                    path=row['path'],
                    defaults={
                        'tab_name': row['tab_name'],
                        'visit_count': row['visit_count'],
                        'unique_users': row['unique_users'],
                    },
                )
                if not created:
                    obj.visit_count += row['visit_count']
                    obj.unique_users = max(obj.unique_users, row['unique_users'])
                    obj.save(update_fields=['visit_count', 'unique_users'])
                upserted += 1

            deleted_count, _ = old_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'{deleted_count} ham kayıt silindi, {upserted} özet satırı güncellendi.'
            )
        )
