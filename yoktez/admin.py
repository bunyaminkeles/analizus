from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import YokTezUniversite

# YokTezSearchJob admin kaydı oaipmh/admin.py'de YokTezSearchJobProxy
# üzerinden "Arama Servisleri" bölümünde yapılmaktadır.


@admin.register(YokTezUniversite)
class YokTezUniversiteAdmin(ModelAdmin):
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ['name', 'yok_id', 'is_active', 'last_checked_at', 'last_result_count', 'flagged_for_review']
    list_filter = ['is_active', 'flagged_for_review']
    search_fields = ['name', 'yok_id']
    list_editable = ['is_active']
