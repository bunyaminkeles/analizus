from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Tüm başlatma komutlarını sırasıyla çalıştırır (Render deployment için)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-quiz',
            action='store_true',
            help='Quiz soru üretimini atla (API key yoksa)'
        )

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('''
╔══════════════════════════════════════════════════════════════════╗
║           🚀 ANALİZUS BAŞLATMA SİSTEMİ                           ║
║           Tüm veriler hazırlanıyor...                            ║
╚══════════════════════════════════════════════════════════════════╝
        '''))

        commands = [
            ('setup_categories', 'Kategoriler oluşturuluyor...'),
            ('create_badges', 'Rozetler oluşturuluyor...'),
            ('create_skills', 'Yetenekler oluşturuluyor...'),
        ]

        # Quiz üretimini atla seçeneği
        if not kwargs.get('skip_quiz'):
            commands.append(('generate_daily_quiz', 'Günlük quiz soruları üretiliyor...'))

        success_count = 0
        error_count = 0

        for cmd, description in commands:
            try:
                self.stdout.write(f'\n📌 {description}')
                self.stdout.write('-' * 50)
                call_command(cmd)
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ {cmd} tamamlandı!'))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'❌ {cmd} hatası: {str(e)}'))

        # Özet
        self.stdout.write(self.style.SUCCESS(f'''
╔══════════════════════════════════════════════════════════════════╗
║                    ✅ BAŞLATMA TAMAMLANDI                         ║
╠══════════════════════════════════════════════════════════════════╣
║  Başarılı: {success_count:<51} ║
║  Hatalı: {error_count:<53} ║
╠══════════════════════════════════════════════════════════════════╣
║  Render Deployment için:                                         ║
║    Build Command: pip install -r requirements.txt                ║
║    Start Command: gunicorn analizdestek.wsgi:application         ║
║                                                                   ║
║  İlk deployment sonrası çalıştırın:                              ║
║    python manage.py migrate                                      ║
║    python manage.py setup_all                                    ║
╚══════════════════════════════════════════════════════════════════╝
        '''))
