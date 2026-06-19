from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TranscriptSettings, TranscriptJob


@admin.register(TranscriptSettings)
class TranscriptSettingsAdmin(ModelAdmin):
    list_display = ["max_minutes_admin", "max_minutes_user"]

    def max_minutes_user(self, obj):
        return obj.max_minutes_admin // 2
    max_minutes_user.short_description = "Standart kullanıcı maks. (dk)"

    def has_add_permission(self, request):
        return not TranscriptSettings.objects.exists()


@admin.register(TranscriptJob)
class TranscriptJobAdmin(ModelAdmin):
    list_display = ["id", "user", "video_id", "video_title", "language_used", "delivery", "status", "created_at"]
    list_filter = ["status", "delivery", "translated"]
    search_fields = ["user__username", "video_id", "video_title"]
    readonly_fields = ["created_at", "completed_at", "transcript_text"]
    ordering = ["-created_at"]
