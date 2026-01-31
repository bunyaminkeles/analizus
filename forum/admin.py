from django.contrib import admin
from django.utils.html import format_html
from .models import Section, Category, Topic, Post, Profile, ContactMessage, PrivateMessage, Badge, Notification, Skill, EmailVerification, DailyTip, QuizQuestion, QuizScore, FreelanceJob, JobProposal, JobReview, UserQuizAttempt, DonationTier, Donation, JobPayment, TopicTag, SiteSettings, BlogCategory, BlogPost

# --- GENEL AYARLAR ---
admin.site.site_header = "Analizus Komuta Merkezi"
admin.site.site_title = "Vizyon 2050 Admin"
admin.site.index_title = "Sistem Yönetim Paneli"

# 1. Kategori Yönetimi (Inline)
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1
    prepopulated_fields = {'slug': ('title',)}

# 2. Ana Bölüm (Section) Yönetimi
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'order_visual', 'category_count') 
    list_editable = ('order',)
    inlines = [CategoryInline]
    ordering = ('order',)

    def order_visual(self, obj):
        return format_html(
            '<div style="width:100px; background:#e9ecef; height:10px; border-radius:5px;">'
            '<div style="width:{}px; background:#00d2ff; height:10px; border-radius:5px;"></div>'
            '</div>',
            min(obj.order * 10, 100)
        )
    order_visual.short_description = "Görsel Sıralama"

    def category_count(self, obj):
        return obj.categories.count()
    category_count.short_description = "Kategori Sayısı"

# 3. Konu Etiketi (TopicTag) Yönetimi
@admin.register(TopicTag)
class TopicTagAdmin(admin.ModelAdmin):
    list_display = ('tag_preview', 'name', 'tag_type', 'order', 'topic_count', 'is_active')
    list_filter = ('tag_type', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def tag_preview(self, obj):
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">'
            '<i class="{}"></i> {}</span>',
            obj.color, obj.icon, obj.name
        )
    tag_preview.short_description = "Etiket"

    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = "Konu Sayısı"


# 4. Konu (Topic) Yönetimi
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('subject_link', 'category_colored', 'tags_display', 'starter', 'created_at', 'views', 'status')
    list_filter = ('is_pinned', 'is_closed', 'category', 'tags', 'created_at')
    search_fields = ('subject', 'starter__username')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    actions = ['make_pinned', 'make_unpinned', 'make_closed', 'make_open']

    def subject_link(self, obj):
        return format_html('<b>{}</b>', obj.subject)
    subject_link.short_description = "Konu Başlığı"

    def category_colored(self, obj):
        return format_html('<span style="color: #00d2ff;">{}</span>', obj.category.title)
    category_colored.short_description = "Kategori"

    def tags_display(self, obj):
        tags = obj.tags.all()
        if not tags:
            return "-"
        html_parts = []
        for tag in tags:
            html_parts.append(
                f'<span style="background: {tag.color}; color: white; padding: 2px 8px; '
                f'border-radius: 10px; font-size: 11px; margin-right: 4px;">{tag.name}</span>'
            )
        return format_html(''.join(html_parts))
    tags_display.short_description = "Etiketler"

    def status(self, obj):
        res = []
        if obj.is_pinned: res.append("📌 Sabit")
        if obj.is_closed: res.append("🔒 Kilitli")
        return " | ".join(res) if res else "Normal"

    # Custom Actions
    @admin.action(description='📌 Seçili konuları sabitle')
    def make_pinned(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} konu sabitlendi.')

    @admin.action(description='📌 Sabitlemeyi kaldır')
    def make_unpinned(self, request, queryset):
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} konunun sabitlemesi kaldırıldı.')

    @admin.action(description='🔒 Seçili konuları kilitle')
    def make_closed(self, request, queryset):
        updated = queryset.update(is_closed=True)
        self.message_user(request, f'{updated} konu kilitlendi.')

    @admin.action(description='🔓 Seçili konuları aç')
    def make_open(self, request, queryset):
        updated = queryset.update(is_closed=False)
        self.message_user(request, f'{updated} konu açıldı.')

# 4. Mesaj (Post) Yönetimi - ✅ DÜZELTİLDİ
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'topic_link', 'short_message', 'created_at')
    search_fields = ('message', 'created_by__username', 'topic__subject')
    list_filter = ('created_at', 'topic__category')
    date_hierarchy = 'created_at'

    def short_message(self, obj):
        return obj.message[:50] + "..."
    short_message.short_description = "Mesaj"

    def topic_link(self, obj):
        return format_html('<a href="/admin/forum/topic/{}/change/" style="color: #00d2ff;">{}</a>', obj.topic.id, obj.topic.subject[:40])
    topic_link.short_description = "Konu"

# 5. Özel Mesaj (DM) Yönetimi
@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_content', 'created_at', 'read_status')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'message')
    actions = ['mark_as_read', 'mark_as_unread']

    def short_content(self, obj):
        return obj.message[:50] + "..."
    short_content.short_description = "Mesaj İçeriği"

    def read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color: #28a745;">✅ Okundu</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">❌ Okunmadı</span>')
    read_status.short_description = "Durum"

    # Custom Actions
    @admin.action(description='✅ Okundu olarak işaretle')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} mesaj okundu olarak işaretlendi.')

    @admin.action(description='❌ Okunmadı olarak işaretle')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} mesaj okunmadı olarak işaretlendi.')

# 6. Yetenek (Skill) Yönetimi
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill_preview', 'name', 'category', 'user_count')
    list_filter = ('category',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def skill_preview(self, obj):
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">'
            '<i class="{}"></i> {}</span>',
            obj.color, obj.icon, obj.name
        )
    skill_preview.short_description = "Yetenek"

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = "Kullanıcı Sayısı"


# 7. Rozet (Badge) Yönetimi
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('badge_preview', 'name', 'badge_type', 'points_required', 'user_count', 'is_active')
    list_filter = ('badge_type', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'points_required')

    def badge_preview(self, obj):
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">'
            '<i class="{}"></i> {}</span>',
            obj.color, obj.icon, obj.name
        )
    badge_preview.short_description = "Rozet"

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = "Kullanıcı Sayısı"


# 8. Profil Yönetimi
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_preview', 'rank_display', 'reputation', 'account_type', 'email_status', 'university_info', 'stats_display')
    list_editable = ('account_type',)
    search_fields = ('user__username', 'title', 'university', 'department')
    list_filter = ('account_type', 'rank', 'is_public', 'email_verified')
    filter_horizontal = ('badges', 'skills')
    actions = ['update_all_ranks', 'update_all_stats', 'verify_emails']

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('user', 'avatar', 'cover_image', 'bio', 'title', 'location')
        }),
        ('Akademik Bilgiler', {
            'fields': ('university', 'department', 'academic_title'),
            'classes': ('collapse',)
        }),
        ('Sosyal Medya', {
            'fields': ('website', 'linkedin', 'twitter', 'github', 'orcid', 'google_scholar'),
            'classes': ('collapse',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('account_type', 'rank', 'reputation', 'badges', 'skills')
        }),
        ('İstatistikler', {
            'fields': ('total_topics', 'total_posts', 'total_likes_received', 'best_answers_count'),
            'classes': ('collapse',)
        }),
        ('Tercihler', {
            'fields': ('email_on_reply', 'email_on_private_message', 'is_public', 'show_email', 'email_verified'),
            'classes': ('collapse',)
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">', obj.avatar.url)
        return format_html('<div style="width: 40px; height: 40px; border-radius: 50%; background: #555; display: flex; align-items: center; justify-content: center; color: white;">{}</div>', obj.user.username[0].upper())
    avatar_preview.short_description = "Avatar"

    def rank_display(self, obj):
        rank_info = obj.get_rank_display_with_icon()
        return format_html(
            '<span style="color: {};">{} {}</span>',
            rank_info['color'], rank_info['icon'], rank_info['name']
        )
    rank_display.short_description = "Rütbe"

    def university_info(self, obj):
        if obj.university:
            return format_html('<span title="{}">{}</span>', obj.department or '-', obj.university[:20] + '...' if len(obj.university) > 20 else obj.university)
        return format_html('<span style="color: #888;">-</span>')
    university_info.short_description = "Üniversite"

    def stats_display(self, obj):
        return format_html(
            '<span title="Konu: {}, Gönderi: {}, Beğeni: {}">📊 {}/{}/{}</span>',
            obj.total_topics, obj.total_posts, obj.total_likes_received,
            obj.total_topics, obj.total_posts, obj.total_likes_received
        )
    stats_display.short_description = "İstatistikler"

    @admin.action(description='🔄 Seçili kullanıcıların rütbelerini güncelle')
    def update_all_ranks(self, request, queryset):
        for profile in queryset:
            profile.update_rank()
        self.message_user(request, f'{queryset.count()} kullanıcının rütbesi güncellendi.')

    @admin.action(description='📊 Seçili kullanıcıların istatistiklerini güncelle')
    def update_all_stats(self, request, queryset):
        for profile in queryset:
            profile.update_stats()
        self.message_user(request, f'{queryset.count()} kullanıcının istatistikleri güncellendi.')

    def email_status(self, obj):
        if obj.email_verified:
            return format_html('<span style="color: #28a745;">✅ Doğrulandı</span>')
        return format_html('<span style="color: #dc3545;">❌ Doğrulanmadı</span>')
    email_status.short_description = "E-posta"

    @admin.action(description='✅ E-postaları doğrulanmış olarak işaretle')
    def verify_emails(self, request, queryset):
        updated = queryset.update(email_verified=True)
        self.message_user(request, f'{updated} kullanıcının e-postası doğrulandı olarak işaretlendi.')


# 8. Bildirim Yönetimi
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'verb', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'verb')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read']

    @admin.action(description='✅ Okundu olarak işaretle')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} bildirim okundu olarak işaretlendi.')

# 7. İletişim Mesajları
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at_formatted', 'preview_message')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def created_at_formatted(self, obj):
        return format_html('<span style="color: #00d2ff;">{}</span>', obj.created_at.strftime('%d %b %Y, %H:%M'))
    created_at_formatted.short_description = "Tarih"

    def preview_message(self, obj):
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message
    preview_message.short_description = "Mesaj Önizleme"


# 9. E-posta Doğrulama Yönetimi
@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_short', 'created_at', 'expires_at', 'status')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at')
    date_hierarchy = 'created_at'

    def token_short(self, obj):
        return str(obj.token)[:8] + "..."
    token_short.short_description = "Token"

    def status(self, obj):
        if obj.is_used:
            return format_html('<span style="color: #28a745;">✅ Kullanıldı</span>')
        if obj.is_valid():
            return format_html('<span style="color: #ffc107;">⏳ Bekliyor</span>')
        return format_html('<span style="color: #dc3545;">❌ Süresi Dolmuş</span>')
    status.short_description = "Durum"


# 10. Günlük İpucu Yönetimi
@admin.register(DailyTip)
class DailyTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'publish_date', 'is_active', 'views', 'likes')
    list_filter = ('category', 'is_active', 'publish_date')
    search_fields = ('title', 'content')
    date_hierarchy = 'publish_date'
    list_editable = ('is_active',)
    ordering = ('-publish_date',)

    fieldsets = (
        ('İçerik', {
            'fields': ('title', 'content', 'category', 'icon')
        }),
        ('Yayın', {
            'fields': ('publish_date', 'is_active')
        }),
        ('İstatistik', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
    )


# 11. Quiz Soruları Yönetimi
@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_short', 'category', 'difficulty', 'correct_answer', 'is_active')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('question', 'option_a', 'option_b', 'option_c', 'option_d')
    list_editable = ('is_active',)

    def question_short(self, obj):
        return obj.question[:60] + "..." if len(obj.question) > 60 else obj.question
    question_short.short_description = "Soru"

    fieldsets = (
        ('Soru', {
            'fields': ('question', 'category', 'difficulty')
        }),
        ('Şıklar', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('Açıklama', {
            'fields': ('explanation',),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('is_active',)
        }),
    )


# 12. Quiz Puanları Yönetimi
@admin.register(QuizScore)
class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'correct_answers', 'total_answers', 'streak', 'last_played')
    list_filter = ('last_played',)
    search_fields = ('user__username',)
    ordering = ('-total_points',)

@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('user__username', 'question__question')

@admin.register(FreelanceJob)
class FreelanceJobAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'status', 'is_featured', 'featured_until', 'views', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('likes', 'saved_by')

@admin.register(JobProposal)
class JobProposalAdmin(admin.ModelAdmin):
    list_display = ('job', 'expert', 'price', 'duration', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'expert__username', 'message')


@admin.register(JobReview)
class JobReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'reviewer', 'reviewed_user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('job__title', 'reviewer__username', 'reviewed_user__username', 'comment')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} değerlendirme onaylandı.')
    approve_reviews.short_description = "Seçili değerlendirmeleri onayla"


# 14. Bağış Katmanları
@admin.register(DonationTier)
class DonationTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_amount_display', 'premium_days_display', 'is_active')
    list_editable = ('is_active',)
    ordering = ('-min_amount',)

    def min_amount_display(self, obj):
        return format_html('<span style="color: #22c55e; font-weight: bold;">{}+ TL</span>', obj.min_amount)
    min_amount_display.short_description = "Minimum Miktar"

    def premium_days_display(self, obj):
        return format_html('<span style="color: #ffc107; font-weight: bold;">{} gün</span>', obj.premium_days)
    premium_days_display.short_description = "Premium Süresi"


# 15. Bağış Yönetimi
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_display', 'amount_display', 'status_display', 'premium_days_granted', 'created_at', 'completed_at')
    list_filter = ('status', 'is_anonymous', 'created_at')
    search_fields = ('name', 'email', 'user__username', 'payment_id')
    date_hierarchy = 'created_at'
    readonly_fields = ('payment_id', 'conversation_id', 'created_at', 'completed_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Bağışçı Bilgileri', {
            'fields': ('user', 'name', 'email', 'is_anonymous')
        }),
        ('Ödeme Bilgileri', {
            'fields': ('amount', 'status', 'payment_id', 'conversation_id')
        }),
        ('Ödüller', {
            'fields': ('premium_days_granted', 'message')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def donor_display(self, obj):
        if obj.is_anonymous:
            return format_html('<span style="color: #888;">Anonim</span>')
        name = obj.name or (obj.user.username if obj.user else obj.email)
        return format_html('<span style="color: #ec4899;"><i class="bi bi-heart-fill"></i> {}</span>', name)
    donor_display.short_description = "Bağışçı"

    def amount_display(self, obj):
        return format_html('<span style="color: #22c55e; font-weight: bold;">{}₺</span>', obj.amount)
    amount_display.short_description = "Miktar"

    def status_display(self, obj):
        colors = {
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545'
        }
        icons = {
            'pending': '⏳',
            'completed': '✅',
            'failed': '❌'
        }
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(obj.status, '#888'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )
    status_display.short_description = "Durum"

@admin.register(JobPayment)
class JobPaymentAdmin(admin.ModelAdmin):
    list_display = ('job', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'payment_id')
    readonly_fields = ('payment_id', 'conversation_id', 'created_at')
    ordering = ('-created_at',)


# --- SITE AYARLARI & LINKEDIN ---
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'linkedin_status', 'auto_share_topics', 'auto_share_jobs')
    readonly_fields = ('linkedin_connected_at', 'linkedin_person_urn')

    fieldsets = (
        ('LinkedIn Entegrasyonu', {
            'fields': ('linkedin_access_token', 'linkedin_person_urn', 'linkedin_organization_id', 'linkedin_connected_at'),
            'description': '<a href="/linkedin/connect/" class="button" style="padding: 8px 16px; background: #0077b5; color: white; text-decoration: none; border-radius: 4px;">🔗 LinkedIn Hesabı Bağla</a> &nbsp; <a href="/linkedin/share-test/" class="button" onclick="return confirm(\'Test paylaşımı yapılacak. Emin misiniz?\');" style="padding: 8px 16px; background: #28a745; color: white; text-decoration: none; border-radius: 4px;">🧪 Test Paylaşımı Yap</a>'
        }),
        ('Otomatik Paylaşım', {
            'fields': ('auto_share_topics', 'auto_share_jobs'),
        }),
    )

    def linkedin_status(self, obj):
        if obj.linkedin_access_token:
            return format_html('<span style="color: #28a745;">✅ Bağlı</span>')
        return format_html('<span style="color: #dc3545;">❌ Bağlı Değil</span>')
    linkedin_status.short_description = "LinkedIn"

    def has_add_permission(self, request):
        # Sadece 1 kayıt olabilir
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# BLOG YÖNETİMİ
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'order', 'post_count')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)

    def color_preview(self, obj):
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 4px;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = "Renk"

    def post_count(self, obj):
        return obj.posts.filter(status='published').count()
    post_count.short_description = "Yazı Sayısı"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status_display', 'is_featured', 'views', 'created_at')
    list_filter = ('status', 'category', 'is_featured', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('İçerik', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'cover_image')
        }),
        ('Kategori & Yazar', {
            'fields': ('category', 'author')
        }),
        ('Yayın Ayarları', {
            'fields': ('status', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('LinkedIn', {
            'fields': ('shared_to_linkedin', 'linkedin_share_date'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('views', 'shared_to_linkedin', 'linkedin_share_date', 'published_at')

    def status_display(self, obj):
        colors = {'draft': '#ffc107', 'published': '#28a745'}
        icons = {'draft': '📝', 'published': '✅'}
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(obj.status, '#888'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )
    status_display.short_description = "Durum"

    actions = ['publish_posts', 'share_to_linkedin', 'reset_linkedin_share']

    @admin.action(description="LinkedIn paylaşım durumunu sıfırla")
    def reset_linkedin_share(self, request, queryset):
        updated = queryset.update(shared_to_linkedin=False, linkedin_share_date=None)
        self.message_user(request, f'{updated} yazının LinkedIn durumu sıfırlandı. Tekrar paylaşılabilir.')

    @admin.action(description="Seçili yazıları yayınla")
    def publish_posts(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='draft').update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} yazı yayınlandı.')

    @admin.action(description="LinkedIn'de paylaş")
    def share_to_linkedin(self, request, queryset):
        from .linkedin_utils import linkedin_api
        from django.utils import timezone
        from django.contrib import messages

        total = queryset.count()
        drafts = queryset.filter(status='draft').count()
        already_shared = queryset.filter(shared_to_linkedin=True).count()
        eligible = queryset.filter(status='published', shared_to_linkedin=False)

        shared = 0
        errors = []

        for post in eligible:
            text = f"📝 Yeni Blog Yazısı: {post.title}\n\n"
            text += f"{post.excerpt[:150]}...\n\n"
            text += "#Analizus #VeriAnalizi #Blog"

            url = f"https://www.analizus.com/blog/{post.slug}/"

            result = linkedin_api.post_share(text=text, url=url, title=post.title, description=post.excerpt[:100])

            if result.get('success'):
                post.shared_to_linkedin = True
                post.linkedin_share_date = timezone.now()
                post.save()
                shared += 1
            else:
                errors.append(f"{post.title}: {result.get('error', 'Bilinmeyen hata')}")

        # Detaylı mesaj göster
        if shared > 0:
            self.message_user(request, f'✅ {shared} yazı LinkedIn\'de paylaşıldı.', messages.SUCCESS)
        if drafts > 0:
            self.message_user(request, f'⚠️ {drafts} yazı taslak durumunda (önce yayınlayın).', messages.WARNING)
        if already_shared > 0:
            self.message_user(request, f'ℹ️ {already_shared} yazı zaten paylaşılmış.', messages.INFO)
        if errors:
            for err in errors[:3]:  # İlk 3 hatayı göster
                self.message_user(request, f'❌ Hata: {err}', messages.ERROR)