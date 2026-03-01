from django.core.management.base import BaseCommand
from forum.models import Section, Category  # İki modeli de çağırıyoruz
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Forum Section ve Category yapısını kurar'

    def handle(self, *args, **kwargs):
        # Section ve Category'ler admin panelden yönetiliyor.
        self.stdout.write(self.style.WARNING('setup_categories: Section/Category oluşturma devre dışı. Admin panelden yönetin.'))