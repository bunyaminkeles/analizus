"""
Üniversite endpoint listesini DB'ye yükler.
Kullanım: python manage.py load_universities
"""
import json
import os
from django.core.management.base import BaseCommand
from oaipmh.models import University


class Command(BaseCommand):
    help = 'scripts/oai_endpoints.json dosyasından üniversiteleri DB\'ye yükler'

    def handle(self, *args, **options):
        json_path = os.path.join('scripts', 'oai_endpoints.json')
        if not os.path.exists(json_path):
            self.stderr.write(f"Dosya bulunamadı: {json_path}")
            return

        with open(json_path, encoding='utf-8') as f:
            endpoints = json.load(f)

        created = 0
        updated = 0
        for ep in endpoints:
            obj, is_new = University.objects.update_or_create(
                domain=ep['domain'],
                defaults={
                    'name': ep['university'],
                    'oai_url': ep['oai_url'],
                    'repo_name': ep.get('repo_name', ''),
                    'is_active': True,
                }
            )
            if is_new:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created} üniversite eklendi, {updated} güncellendi.")
        )
