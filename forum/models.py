from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
from django.utils import timezone
from datetime import timedelta
from forum.storage import get_storage

class Section(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Category(models.Model):
    section = models.ForeignKey(Section, related_name='categories', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    icon_class = models.CharField(max_length=50, default="bi-chat-square-text")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title.replace('ı', 'i'))
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class TopicTag(models.Model):
    """Konu etiketleri - Yazılım ve durum tag'leri"""
    TAG_TYPES = (
        ('software', 'Yazılım'),
        ('status', 'Durum'),
        ('other', 'Diğer'),
    )

    name = models.CharField(max_length=50, verbose_name="Etiket Adı")
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default="bi-tag", verbose_name="İkon")
    color = models.CharField(max_length=20, default="#6366f1", verbose_name="Renk")
    tag_type = models.CharField(max_length=20, choices=TAG_TYPES, default='software', verbose_name="Etiket Türü")
    order = models.IntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Konu Etiketi"
        verbose_name_plural = "Konu Etiketleri"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Topic(models.Model):
    category = models.ForeignKey(Category, related_name='topics', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(TopicTag, blank=True, related_name='topics', verbose_name="Etiketler")
    is_pinned = models.BooleanField(default=False, verbose_name="Sabitlenmiş")
    is_closed = models.BooleanField(default=False, verbose_name="Kilitli")

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={'pk': self.pk})

    @property
    def last_post(self):
        """Bu konuya atılan son gönderiyi döndürür."""
        return self.posts.order_by('-created_at').first()

class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    message = models.TextField()
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_best_answer = models.BooleanField(default=False, verbose_name="En Faydalı Yanıt")
    likes = models.PositiveIntegerField(default=0, verbose_name="Beğeni Sayısı")

    def __str__(self):
        return f"Post by {self.created_by.username}"

    def get_absolute_url(self):
        topic_url = self.topic.get_absolute_url()
        return f"{topic_url}#post-{self.id}"

class Badge(models.Model):
    """Kullanıcılara verilebilecek rozetler/etiketler"""
    BADGE_TYPES = (
        ('achievement', 'Başarı'),
        ('specialty', 'Uzmanlık'),
        ('participation', 'Katılım'),
        ('special', 'Özel'),
    )

    name = models.CharField(max_length=50, verbose_name="Rozet Adı")
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200, verbose_name="Açıklama")
    icon = models.CharField(max_length=50, default="bi-award", verbose_name="İkon (Bootstrap Icons)")
    color = models.CharField(max_length=20, default="#6366f1", verbose_name="Renk (Hex)")
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, default='achievement')
    points_required = models.IntegerField(default=0, verbose_name="Gereken Puan (0=manuel)")
    can_write_blog = models.BooleanField(default=False, verbose_name="Blog Yazabilir")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rozet"
        verbose_name_plural = "Rozetler"
        ordering = ['-points_required']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Kullanıcı uzmanlık alanları"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Yetenek Adı")
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default="bi-lightbulb", verbose_name="İkon")
    color = models.CharField(max_length=20, default="#6366f1", verbose_name="Renk")
    category = models.CharField(max_length=50, blank=True, verbose_name="Kategori")

    class Meta:
        verbose_name = "Yetenek"
        verbose_name_plural = "Yetenekler"
        ordering = ['name']

    def __str__(self):
        return self.name


class Profile(models.Model):
    ACCOUNT_TYPES = (
        ('Free', 'Ücretsiz Üye'),
        ('Premium', 'Premium Üye'),
        ('Expert', 'Uzman'),
    )

    # Rütbe seviyeleri (puana göre otomatik atanır)
    RANK_CHOICES = (
        ('newbie', 'Çaylak'),
        ('member', 'Üye'),
        ('active', 'Aktif Üye'),
        ('contributor', 'Katkıcı'),
        ('expert', 'Uzman'),
        ('master', 'Usta'),
        ('legend', 'Efsane'),
        ('admin', 'Yönetici'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', storage=get_storage, blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', storage=get_storage, blank=True, null=True, verbose_name="Kapak Fotoğrafı")
    bio = models.TextField(max_length=500, blank=True)
    title = models.CharField(max_length=100, blank=True, default="", verbose_name="Ünvan")
    location = models.CharField(max_length=100, blank=True, default="", verbose_name="Konum")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='Free')
    premium_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Premium Bitiş Tarihi")
    reputation = models.IntegerField(default=0, verbose_name="Akademik Puan")

    # Rütbe sistemi
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='newbie', verbose_name="Rütbe")
    badges = models.ManyToManyField(Badge, blank=True, related_name='users', verbose_name="Rozetler")

    # GELİŞMİŞ PROFİL ALANLARI
    skills = models.ManyToManyField('JobCategory', blank=True, related_name='profiles', verbose_name="Uzmanlık Alanları")
    university = models.CharField(max_length=150, blank=True, default="", verbose_name="Üniversite")
    department = models.CharField(max_length=150, blank=True, default="", verbose_name="Bölüm")
    academic_title = models.CharField(max_length=50, blank=True, default="", verbose_name="Akademik Unvan")

    # Sosyal medya linkleri
    website = models.URLField(blank=True, default="", verbose_name="Web Sitesi")
    linkedin = models.URLField(blank=True, default="", verbose_name="LinkedIn")
    twitter = models.CharField(max_length=50, blank=True, default="", verbose_name="Twitter/X Kullanıcı Adı")
    github = models.CharField(max_length=50, blank=True, default="", verbose_name="GitHub Kullanıcı Adı")
    orcid = models.CharField(max_length=20, blank=True, default="", verbose_name="ORCID ID")
    google_scholar = models.URLField(blank=True, default="", verbose_name="Google Scholar")

    # İstatistikler (cache için)
    total_topics = models.PositiveIntegerField(default=0, verbose_name="Toplam Konu")
    total_posts = models.PositiveIntegerField(default=0, verbose_name="Toplam Gönderi")
    total_likes_received = models.PositiveIntegerField(default=0, verbose_name="Alınan Beğeni")
    best_answers_count = models.PositiveIntegerField(default=0, verbose_name="En İyi Cevap Sayısı")

    # Tarihler
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Son Görülme")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Kayıt Tarihi")

    # EMAIL BİLDİRİM TERCİHLERİ
    email_on_reply = models.BooleanField(default=True, verbose_name="Konuma cevap geldiğinde email gönder")
    email_on_private_message = models.BooleanField(default=True, verbose_name="Özel mesaj geldiğinde email gönder")

    # Profil görünürlüğü
    is_public = models.BooleanField(default=True, verbose_name="Profil Herkese Açık")
    show_email = models.BooleanField(default=False, verbose_name="Email Adresini Göster")

    # E-posta doğrulama durumu
    email_verified = models.BooleanField(default=False, verbose_name="E-posta Doğrulandı")

    # Yeni Doğrulama Alanları
    phone_number = models.CharField(max_length=20, blank=True, default="", verbose_name="Telefon Numarası")
    phone_verified = models.BooleanField(default=False, verbose_name="Telefon Doğrulandı")
    linkedin_verified = models.BooleanField(default=False, verbose_name="LinkedIn Doğrulandı")

    # EDU mail ile giriş yapanlara geçici teklif hakkı
    edu_proposal_expires = models.DateTimeField(null=True, blank=True, verbose_name="EDU Teklif Hakkı Bitiş")
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False, blank=True, verbose_name="Takip Edilenler")

    # Günlük giriş streak
    login_streak = models.PositiveIntegerField(default=0, verbose_name="Giriş Serisi")
    max_login_streak = models.PositiveIntegerField(default=0, verbose_name="En Uzun Giriş Serisi")
    last_login_streak_date = models.DateField(null=True, blank=True, verbose_name="Son Seri Güncellemesi")

    # Onboarding
    SEGMENT_CHOICES = (
        ('student', 'Öğrenci'),
        ('academic', 'Akademisyen'),
        ('expert', 'Uzman'),
        ('curious', 'Meraklı'),
    )
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, blank=True, default='', verbose_name="Segment")
    onboarding_completed = models.BooleanField(default=False, verbose_name="Onboarding Tamamlandı")
    onboarding_interests = models.JSONField(default=list, blank=True, verbose_name="İlgi Alanları")
    onboarding_tools = models.JSONField(default=list, blank=True, verbose_name="Kullanılan Araçlar")

    # Hesap silme
    deletion_requested_at = models.DateTimeField(null=True, blank=True, verbose_name="Silme Talebi Tarihi")
    deletion_token = models.CharField(max_length=64, blank=True, default="", verbose_name="Silme Token")
    deletion_token_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Token Geçerlilik Süresi")

    def __str__(self):
        return self.user.username

    def update_rank(self):
        """Toplam puana göre rütbeyi otomatik günceller (Forum + Quiz)"""
        total = self.total_score  # Forum puanı + Quiz puanı

        if self.user.is_superuser or self.user.is_staff:
            self.rank = 'admin'
        elif total >= 5000:
            self.rank = 'legend'
        elif total >= 2500:
            self.rank = 'master'
        elif total >= 1000:
            self.rank = 'expert'
        elif total >= 500:
            self.rank = 'contributor'
        elif total >= 200:
            self.rank = 'active'
        elif total >= 50:
            self.rank = 'member'
        else:
            self.rank = 'newbie'
        self.save(update_fields=['rank'])

    def get_rank_display_with_icon(self):
        """Rütbe adı ve ikonu ile birlikte döndürür"""
        rank_icons = {
            'newbie': ('🌱', '#94a3b8'),
            'member': ('👤', '#64748b'),
            'active': ('⚡', '#3b82f6'),
            'contributor': ('✍️', '#8b5cf6'),
            'expert': ('🎯', '#f59e0b'),
            'master': ('👑', '#ef4444'),
            'legend': ('🏆', '#eab308'),
            'admin': ('🛡️', '#dc2626'),
        }
        icon, color = rank_icons.get(self.rank, ('👤', '#64748b'))
        return {'icon': icon, 'color': color, 'name': self.get_rank_display()}

    def check_and_award_badges(self):
        """Toplam puana göre otomatik rozet kontrolü ve ödüllendirme"""
        total = self.total_score  # Forum puanı + Quiz puanı
        auto_badges = Badge.objects.filter(points_required__gt=0, points_required__lte=total)
        for badge in auto_badges:
            self.badges.add(badge)

    def update_stats(self):
        """Kullanıcı istatistiklerini günceller"""
        self.total_topics = self.user.topics.count()
        self.total_posts = self.user.posts.count()
        self.total_likes_received = self.user.posts.aggregate(total=Sum('likes'))['total'] or 0
        self.best_answers_count = self.user.posts.filter(is_best_answer=True).count()
        self.save(update_fields=['total_topics', 'total_posts', 'total_likes_received', 'best_answers_count'])

    def get_activity_stats(self):
        """Aktivite istatistiklerini sözlük olarak döndürür"""
        return {
            'topics': self.total_topics,
            'posts': self.total_posts,
            'likes': self.total_likes_received,
            'best_answers': self.best_answers_count,
            'reputation': self.reputation,
            'badges': self.badges.count(),
        }

    @property
    def total_score(self):
        """Forum puanı + Quiz puanı = Toplam Puan"""
        quiz_points = 0
        quiz_score = self.user.quiz_scores.first()
        if quiz_score:
            quiz_points = quiz_score.total_points
        return self.reputation + quiz_points

    @property
    def is_premium(self):
        """Premium üyelik aktif mi kontrol et"""
        if self.account_type != 'Premium':
            return False
        if not self.premium_expires_at:
            return False
        return self.premium_expires_at > timezone.now()

    @property
    def quiz_points(self):
        """Sadece quiz puanını döndürür"""
        quiz_score = self.user.quiz_scores.first()
        return quiz_score.total_points if quiz_score else 0

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).total_seconds() < 300

    def get_full_name(self):
        """Tam adı veya kullanıcı adını döndürür"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username

    def get_display_title(self):
        """Görüntülenecek ünvanı döndürür"""
        if self.academic_title:
            return self.academic_title
        if self.title:
            return self.title
        return self.get_rank_display()

    # ═══════════════════════════════════════════════════════════════════════
    # YETKİ KONTROL METODLARI
    # ═══════════════════════════════════════════════════════════════════════

    def can_post_job(self):
        """İlan açma yetkisi kontrolü - Tüm kayıtlı kullanıcılar ilan açabilir"""
        return True, "Kayıtlı üye"

    def get_weekly_job_limit(self):
        """Haftalık ilan limiti: Premium = 3, diğer = 1"""
        if self.account_type == 'Premium':
            return 3
        return 1

    def get_weekly_job_count(self):
        """Bu hafta açılan ilan sayısı"""
        from datetime import timedelta
        from django.utils import timezone
        week_ago = timezone.now() - timedelta(days=7)
        return self.user.posted_jobs.filter(created_at__gte=week_ago).count()

    def can_post_job_now(self):
        """Kullanıcı şu an ilan açabilir mi? (limit + e-posta kontrolü)"""
        if not self.email_verified:
            return False, "İlan açmak için e-posta doğrulaması gerekli"
        if self.get_weekly_job_count() >= self.get_weekly_job_limit():
            limit = self.get_weekly_job_limit()
            return False, f"Haftalık ilan limitinize ({limit}) ulaştınız"
        return True, "İlan açabilirsiniz"

    def get_job_duration_days(self):
        """Puana göre ilan süresi: <500p=5gün, 500-1000p=14gün, 1000+p=30gün"""
        if self.total_score >= 1000:
            return 30
        elif self.total_score >= 500:
            return 14
        return 5

    def is_first_job(self):
        """Kullanıcının ilk ilanı mı?"""
        return self.user.posted_jobs.count() == 0

    def can_propose(self):
        """Teklif verme yetkisi kontrolü"""
        from django.utils import timezone

        # Admin/Staff her zaman verebilir
        if self.user.is_superuser or self.user.is_staff:
            return True, "Yönetici yetkisi"

        # Premium üyeler verebilir
        if self.account_type == 'Premium':
            return True, "Premium üyelik"

        # EDU mail ile geçici teklif hakkı
        if self.edu_proposal_expires and self.edu_proposal_expires > timezone.now():
            return True, "EDU mail ayrıcalığı (3 günlük)"

        # Belirli rütbeler verebilir (expert ve üstü)
        allowed_ranks = ['expert', 'master', 'legend', 'admin']
        if self.rank in allowed_ranks:
            return True, f"{self.get_rank_display()} rütbesi"

        # Belirli rozetler ile verebilir
        proposal_badges = [
            'uzman',              # 2500 puan
            'profesor',           # 5000 puan
            'efsane',             # 10000 puan
            'cozum-ustasi',       # 25 en iyi cevap
            'quiz-efsanesi',      # 1000 quiz doğru
            'dogrulanmis-akademisyen',
            'moderator',
        ]
        user_badges = self.badges.filter(slug__in=proposal_badges)
        if user_badges.exists():
            return True, user_badges.first().name

        return False, "Teklif vermek için 1000+ puan veya özel rozet gerekli"

    def get_permissions_summary(self):
        """Kullanıcının tüm yetkilerinin özetini döndürür"""
        can_post, post_reason = self.can_post_job()
        can_prop, prop_reason = self.can_propose()

        return {
            'can_post_job': can_post,
            'post_job_reason': post_reason,
            'can_propose': can_prop,
            'propose_reason': prop_reason,
            'is_premium': self.account_type == 'Premium',
            'is_verified': self.email_verified and self.phone_verified and self.linkedin_verified,
            'rank': self.rank,
            'rank_display': self.get_rank_display(),
            'reputation': self.reputation,
            'badge_count': self.badges.count(),
        }

    def get_badges_by_type(self):
        """Rozetleri türlerine göre gruplar"""
        badges = self.badges.all()
        return {
            'achievement': badges.filter(badge_type='achievement'),
            'specialty': badges.filter(badge_type='specialty'),
            'participation': badges.filter(badge_type='participation'),
            'special': badges.filter(badge_type='special'),
        }

    def get_next_badge_info(self):
        """Bir sonraki kazanılabilecek rozet bilgisini döndürür"""
        from .models import Badge
        # Puan bazlı rozetler
        next_badge = Badge.objects.filter(
            points_required__gt=self.reputation,
            is_active=True
        ).order_by('points_required').first()

        if next_badge:
            points_needed = next_badge.points_required - self.reputation
            return {
                'badge': next_badge,
                'points_needed': points_needed,
                'progress': int((self.reputation / next_badge.points_required) * 100)
            }
        return None


class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField(blank=True)  # Opsiyonel - sadece dosya da gönderilebilir
    attachment = models.FileField(upload_to='chat_attachments/%Y/%m/', storage=get_storage, blank=True, null=True, verbose_name="Dosya Eki")
    attachment_name = models.CharField(max_length=255, blank=True, verbose_name="Dosya Adı")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def get_attachment_type(self):
        """Dosya tipini döndür (image, pdf, document, other)"""
        if not self.attachment:
            return None
        ext = self.attachment.name.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return 'image'
        elif ext == 'pdf':
            return 'pdf'
        elif ext in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
            return 'document'
        return 'other'

    def get_absolute_url(self):
        """Mesajın URL'sini döndür (mesajlaşma sayfası)"""
        from django.urls import reverse
        return reverse('send_message', args=[self.sender.username])

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False, verbose_name="Okundu")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class PostLike(models.Model):
    """Kullanıcıların post beğenilerini takip eden model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Her kullanıcı bir post'a sadece 1 kez like verebilir
        verbose_name = "Beğeni"
        verbose_name_plural = "Beğeniler"

    def __str__(self):
        return f"{self.user.username} liked Post #{self.post.id}"

class Notification(models.Model):
    """Gerçek zamanlı bildirimler için model"""
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Alıcı")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True, verbose_name="Gönderen")
    verb = models.CharField(max_length=255, verbose_name="Eylem")
    
    # Bildirimin ilişkili olduğu nesne (örneğin, bir Post, bir Topic, vb.)
    # ContentType framework'ü kullanılarak esnek bir yapı oluşturulur.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False, verbose_name="Okundu mu?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"

    def __str__(self):
        if self.target:
            return f"{self.sender.username} -> {self.recipient.username}: {self.verb} -> {self.target}"
        return f"{self.sender.username} -> {self.recipient.username}: {self.verb}"

    def get_url(self):
        """Bildirimin hedef URL'sini döndürür"""
        if self.target and hasattr(self.target, 'get_absolute_url'):
            return self.target.get_absolute_url()
        return reverse('home')


class EmailVerification(models.Model):
    """E-posta doğrulama token modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "E-posta Doğrulama"
        verbose_name_plural = "E-posta Doğrulamaları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.token}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token 24 saat geçerli
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Token'ın geçerli olup olmadığını kontrol eder"""
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_for_user(cls, user):
        """Kullanıcı için yeni doğrulama token'ı oluşturur"""
        # Önceki kullanılmamış token'ları geçersiz kıl
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        return cls.objects.create(user=user)


class DailyTip(models.Model):
    """Günlük ipucu sistemi"""
    CATEGORY_CHOICES = [
        ('spss', 'SPSS'),
        ('python', 'Python'),
        ('r', 'R'),
        ('excel', 'Excel'),
        ('statistics', 'İstatistik'),
        ('methodology', 'Metodoloji'),
        ('academic', 'Akademik Yazım'),
    ]

    title = models.CharField(max_length=200, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Kategori")
    icon = models.CharField(max_length=50, default="bi-lightbulb", verbose_name="İkon")

    publish_date = models.DateField(verbose_name="Yayın Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    views = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme")
    likes = models.PositiveIntegerField(default=0, verbose_name="Beğeni")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-publish_date']
        verbose_name = "Günlük İpucu"
        verbose_name_plural = "Günlük İpuçları"

    def __str__(self):
        return f"{self.publish_date} - {self.title}"

    @classmethod
    def get_today_tip(cls):
        """Bugünün ipucunu döndürür"""
        today = timezone.now().date()
        return cls.objects.filter(publish_date=today, is_active=True).first()


class QuizQuestion(models.Model):
    """İstatistik Arena quiz soruları"""
    CATEGORY_CHOICES = [
        ('spss', 'SPSS'),
        ('python', 'Python'),
        ('r', 'R'),
        ('statistics', 'İstatistik'),
        ('methodology', 'Metodoloji'),
        ('cronbach', 'Güvenilirlik (Cronbach Alpha)'),
        ('normallik', 'Normallik Testi'),
        ('korelasyon', 'Korelasyon'),
        ('ttesti', 't-Testi'),
        ('anova', 'ANOVA'),
        ('betimsel', 'Betimleyici İstatistik'),
        ('output_reading', 'Çıktı Okuma'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Kolay'),
        ('medium', 'Orta'),
        ('hard', 'Zor'),
    ]

    question = models.TextField(verbose_name="Soru")
    option_a = models.CharField(max_length=255, verbose_name="A Şıkkı")
    option_b = models.CharField(max_length=255, verbose_name="B Şıkkı")
    option_c = models.CharField(max_length=255, verbose_name="C Şıkkı")
    option_d = models.CharField(max_length=255, verbose_name="D Şıkkı")
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')], verbose_name="Doğru Cevap")

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Kategori")
    topic = models.CharField(max_length=50, blank=True, verbose_name="Alt Konu")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', verbose_name="Zorluk")
    explanation = models.TextField(blank=True, verbose_name="Açıklama")
    image = models.ImageField(upload_to='quiz/images/', blank=True, null=True, verbose_name="Görsel (opsiyonel)")

    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Quiz Sorusu"
        verbose_name_plural = "Quiz Soruları"

    def __str__(self):
        return self.question[:50]

    @classmethod
    def get_random_question(cls):
        """Rastgele aktif bir soru döndürür"""
        return cls.objects.filter(is_active=True).order_by('?').first()


class UserQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quiz Denemesi"
        verbose_name_plural = "Quiz Denemeleri"

class QuizScore(models.Model):
    """Kullanıcı quiz puanları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_scores')
    total_points = models.PositiveIntegerField(default=0, verbose_name="Toplam Puan")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="Doğru Cevap")
    total_answers = models.PositiveIntegerField(default=0, verbose_name="Toplam Cevap")
    streak = models.PositiveIntegerField(default=0, verbose_name="Seri")
    last_played = models.DateTimeField(null=True, blank=True, verbose_name="Son Oynanma")

    class Meta:
        verbose_name = "Quiz Puanı"
        verbose_name_plural = "Quiz Puanları"

    def get_category_stats(self):
        """Kategori bazında başarı istatistiklerini döndürür"""
        from django.db.models import Count, Q

        attempts = UserQuizAttempt.objects.filter(user=self.user)

        stats = {}
        for cat_code, cat_name in QuizQuestion.CATEGORY_CHOICES:
            cat_attempts = attempts.filter(question__category=cat_code)
            total = cat_attempts.count()
            correct = cat_attempts.filter(is_correct=True).count()

            if total > 0:
                stats[cat_code] = {
                    'name': cat_name,
                    'total': total,
                    'correct': correct,
                    'percentage': round((correct / total) * 100, 1),
                }

        return stats


class QuizCategoryScore(models.Model):
    """Kullanıcının kategori bazında quiz performansı"""
    CATEGORY_CHOICES = QuizQuestion.CATEGORY_CHOICES

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_category_scores')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Kategori")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="Doğru Cevap")
    total_answers = models.PositiveIntegerField(default=0, verbose_name="Toplam Cevap")
    points = models.PositiveIntegerField(default=0, verbose_name="Puan")

    class Meta:
        verbose_name = "Kategori Quiz Puanı"
        verbose_name_plural = "Kategori Quiz Puanları"
        unique_together = ['user', 'category']

    @property
    def success_rate(self):
        if self.total_answers == 0:
            return 0
        return round((self.correct_answers / self.total_answers) * 100, 1)

    def __str__(self):
        return f"{self.user.username} - {self.get_category_display()}: %{self.success_rate}"

    def __str__(self):
        return f"{self.user.username} - {self.total_points} puan"

class SuccessStory(models.Model):
    """Kullanıcı başarı hikayeleri (Before/After)"""
    APPROVAL_CHOICES = (
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    job = models.ForeignKey(
        'FreelanceJob', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='success_stories',
        verbose_name="İlgili İş İlanı"
    )
    quote = models.TextField(verbose_name="Hikaye Alıntısı")
    achievements = models.JSONField(default=list, verbose_name="Başarı Maddeleri")
    resources = models.JSONField(default=list, verbose_name="Kullanılan Kaynaklar")
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False, verbose_name="Haftanın Hikayesi")
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_CHOICES,
        default='pending', verbose_name="Onay Durumu"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Başarı Hikayesi"
        verbose_name_plural = "Başarı Hikayeleri"
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} - Başarı Hikayesi"

class JobCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name="Kategori Adı")
    order = models.IntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "İş Kategorisi"
        verbose_name_plural = "İş Kategorileri"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class FreelanceJob(models.Model):
    """Kullanıcıların verdiği iş ilanları (Freelance Market)"""
    STATUS_CHOICES = (
        ('open', 'Açık (Teklif Bekliyor)'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs', verbose_name="İlan Sahibi")
    title = models.CharField(max_length=200, verbose_name="İlan Başlığı")
    reference_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Referans Numarası")
    description = models.TextField(verbose_name="İş Tanımı")
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Min Bütçe (TL)")
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Max Bütçe (TL)")
    expected_duration = models.CharField(max_length=100, blank=True, verbose_name="Beklenen Teslim Süresi")
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs', verbose_name="Kategori")
    
    likes = models.ManyToManyField(User, related_name='liked_jobs', blank=True, verbose_name="Beğenenler")
    saved_by = models.ManyToManyField(User, related_name='saved_jobs', blank=True, verbose_name="Kaydedenler")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Durum")
    views = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme")
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkarılmış")
    featured_until = models.DateTimeField(null=True, blank=True, verbose_name="Vitrin Bitiş Tarihi")

    FEATURE_STATUS_CHOICES = (
        ('none', 'Yok'),
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    )
    feature_status = models.CharField(max_length=20, choices=FEATURE_STATUS_CHOICES, default='none', verbose_name="Vitrin Durumu")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    is_edited = models.BooleanField(default=False, verbose_name="Düzenlendi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "İş İlanı"
        verbose_name_plural = "İş İlanları"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.reference_number:
            from django.utils import timezone
            current_year = timezone.now().year

            last_job_ref = FreelanceJob.objects.filter(
                created_at__year=current_year,
                reference_number__isnull=False
            ).order_by('-reference_number').values_list('reference_number', flat=True).first()

            new_seq = 1
            if last_job_ref:
                try:
                    last_seq = int(last_job_ref.split('/')[-1])
                    new_seq = last_seq + 1
                except (ValueError, IndexError):
                    pass

            self.reference_number = f"{current_year}/{new_seq:04d}"

        # İlan iptal veya tamamlandıysa bekleyen teklifleri reddet
        if self.pk and self.status in ('cancelled', 'completed'):
            old = FreelanceJob.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            if old not in ('cancelled', 'completed'):
                super().save(*args, **kwargs)
                self.proposals.filter(status='pending').update(status='rejected')
                return

        super().save(*args, **kwargs)

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def is_expired(self):
        if self.expires_at and self.status == 'open':
            return timezone.now() > self.expires_at
        return False

    @property
    def days_remaining(self):
        if not self.expires_at or self.status != 'open':
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

    def expire_if_needed(self):
        """Süresi geçmişse ilanı otomatik kapat. Değiştiyse True döner."""
        if self.is_expired:
            self.status = 'cancelled'
            self.save(update_fields=['status'])
            return True
        return False

    @staticmethod
    def can_post(user):
        """İlan açma yetkisi kontrolü (Rozet veya Rütbe)"""
        if not user.is_authenticated:
            return False
        if not hasattr(user, 'profile'):
            return False
        can_post, _ = user.profile.can_post_job()
        return can_post

class JobProposal(models.Model):
    """Uzmanların iş ilanlarına verdiği teklifler"""
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
    )

    job = models.ForeignKey(FreelanceJob, on_delete=models.CASCADE, related_name='proposals', verbose_name="İlan")
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals', verbose_name="Uzman")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Teklif (TL)")
    duration = models.CharField(max_length=50, verbose_name="Süre (Örn: 3 gün)")
    message = models.TextField(verbose_name="Ön Yazı")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Teklif"
        verbose_name_plural = "Teklifler"
        unique_together = ('job', 'expert')

    def __str__(self):
        return f"{self.expert.username} - {self.job.title}"

    @staticmethod
    def can_propose(user):
        """Bir kullanıcının teklif verip veremeyeceğini kontrol eder."""
        if not user.is_authenticated:
            return False
        if not hasattr(user, 'profile'):
            return False
        can_prop, _ = user.profile.can_propose()
        return can_prop


class JobReview(models.Model):
    """İş tamamlandıktan sonra karşılıklı değerlendirme"""
    job = models.ForeignKey(FreelanceJob, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Puan")
    comment = models.CharField(max_length=300, blank=True, verbose_name="Yorum")
    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İş Değerlendirmesi"
        verbose_name_plural = "İş Değerlendirmeleri"
        unique_together = ('job', 'reviewer')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Her iki taraf da onaylı değerlendirme yaptıysa ilanı kapat
        if self.job.reviews.filter(is_approved=True).count() >= 2:
            self.job.status = 'completed'
            self.job.save()


class DonationTier(models.Model):
    """Bağış katmanları - Admin panelden yönetilebilir"""
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Minimum Miktar (TL)")
    premium_days = models.IntegerField(verbose_name="Premium Gün Sayısı")
    name = models.CharField(max_length=50, blank=True, verbose_name="Katman Adı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Bağış Katmanı"
        verbose_name_plural = "Bağış Katmanları"
        ordering = ['-min_amount']  # En yüksekten en düşüğe

    def __str__(self):
        return f"{self.min_amount}+ TL → {self.premium_days} gün"

    @classmethod
    def get_premium_days_for_amount(cls, amount):
        """Verilen miktar için premium gün sayısını döndür"""
        tier = cls.objects.filter(
            is_active=True,
            min_amount__lte=amount
        ).order_by('-min_amount').first()
        return tier.premium_days if tier else 0


class Donation(models.Model):
    """Bağış sistemi için model"""
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('pending_confirmation', 'Onay Bekliyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations', verbose_name="Bağışçı")
    email = models.EmailField(verbose_name="E-posta")
    name = models.CharField(max_length=100, blank=True, verbose_name="İsim")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar (TL)")
    payment_id = models.CharField(max_length=100, unique=True, verbose_name="Ödeme ID")
    conversation_id = models.CharField(max_length=100, blank=True, verbose_name="Konuşma ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    premium_days_granted = models.IntegerField(default=0, verbose_name="Verilen Premium Gün")
    message = models.TextField(blank=True, verbose_name="Mesaj")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anonim")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Bağış"
        verbose_name_plural = "Bağışlar"
        ordering = ['-created_at']

    def __str__(self):
        donor = self.name or (self.user.username if self.user else "Anonim")
        return f"{donor} - {self.amount}₺"

    def get_premium_days(self):
        """Bağış miktarına göre premium gün hesapla (DonationTier modelinden)"""
        return DonationTier.get_premium_days_for_amount(float(self.amount))

    def grant_premium(self):
        """Kullanıcıya premium üyelik ver"""
        if not self.user:
            return False

        days = self.get_premium_days()
        if days == 0:
            return False

        profile = self.user.profile
        now = timezone.now()

        # Mevcut premium varsa üzerine ekle, yoksa şu andan itibaren başlat
        if profile.premium_expires_at and profile.premium_expires_at > now:
            profile.premium_expires_at += timedelta(days=days)
        else:
            profile.premium_expires_at = now + timedelta(days=days)

        profile.account_type = 'Premium'
        profile.save(update_fields=['account_type', 'premium_expires_at'])

        self.premium_days_granted = days
        self.save(update_fields=['premium_days_granted'])

        return True

    def grant_supporter_badge(self):
        """Destekçi rozetini ver"""
        if not self.user:
            return False

        badge, created = Badge.objects.get_or_create(
            slug='destekci',
            defaults={
                'name': 'Destekçi',
                'description': 'Platformumuza bağış yaparak destek oldu',
                'icon': 'bi-heart-fill',
                'color': '#ec4899',
                'badge_type': 'special',
                'points_required': 0,
            }
        )
        self.user.profile.badges.add(badge)
        return True

    @classmethod
    def get_total_donations(cls):
        """Toplam bağış miktarını döndür"""
        from django.db.models import Sum
        total = cls.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum']
        return total or 0

    @classmethod
    def get_recent_donors(cls, limit=5):
        """Son bağışçıları döndür"""
        return cls.objects.filter(
            status='completed',
            is_anonymous=False
        ).select_related('user').order_by('-completed_at')[:limit]

    @classmethod
    def get_top_donors(cls, limit=5):
        """En çok bağış yapanları döndür"""
        from django.db.models import Sum
        return cls.objects.filter(
            status='completed',
            is_anonymous=False,
            user__isnull=False
        ).values('user__username', 'user__id').annotate(
            total=Sum('amount')
        ).order_by('-total')[:limit]

class JobPayment(models.Model):
    """İlan vitrin ödemeleri için model"""
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('pending_confirmation', 'Onay Bekliyor'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
    )

    job = models.ForeignKey(FreelanceJob, on_delete=models.CASCADE, related_name='payments', verbose_name="İlan")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar")
    duration_days = models.PositiveIntegerField(default=7, verbose_name="Vitrin Süresi (Gün)")
    payment_id = models.CharField(max_length=100, unique=True, verbose_name="Ödeme ID")
    conversation_id = models.CharField(max_length=100, verbose_name="Konuşma ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} - {self.amount}₺ - {self.get_status_display()}"


class SiteSettings(models.Model):
    """Site genelinde tekil ayarlar"""
    # Otomatik Paylaşım Ayarları
    auto_share_topics = models.BooleanField(default=False, verbose_name="Yeni konuları otomatik paylaş")
    auto_share_jobs = models.BooleanField(default=False, verbose_name="Yeni ilanları otomatik paylaş")

    # Feature Flags
    feature_blog = models.BooleanField(default=True, verbose_name="Blog")
    feature_market = models.BooleanField(default=True, verbose_name="Hizmetler Pazarı")
    feature_proposal_price_privacy = models.BooleanField(
        default=True,
        verbose_name="Teklif Fiyatı Gizliliği",
        help_text="İlan detaylarında teklif fiyatı yalnızca ilan sahibi ve teklif veren tarafından gösterilsin."
    )
    feature_ai_assistant = models.BooleanField(default=True, verbose_name="AI Asistan")
    feature_trdizin = models.BooleanField(default=False, verbose_name="TR Dizin Tarama")
    feature_openalex = models.BooleanField(default=True, verbose_name="OpenAlex Yayın Tarama")
    feature_semanticscholar = models.BooleanField(default=True, verbose_name="Semantic Scholar Tarama")
    feature_oaipmh = models.BooleanField(default=True, verbose_name="Üniversite Tez Arşivi (OAI-PMH)")
    feature_quiz = models.BooleanField(default=True, verbose_name="İstatistik Arena (Quiz)")
    feature_messaging = models.BooleanField(default=True, verbose_name="Özel Mesajlaşma")
    feature_donation = models.BooleanField(default=True, verbose_name="Bağış Sistemi")
    feature_success_stories = models.BooleanField(default=True, verbose_name="Başarı Hikayeleri")
    feature_bibliometrics = models.BooleanField(default=True, verbose_name="Bibliometrik Analiz")
    feature_yoktez = models.BooleanField(default=True, verbose_name="YÖK Tez Arama")
    feature_tezanaliz = models.BooleanField(default=True, verbose_name="Tez & Makale Analizi")
    feature_istatistik = models.BooleanField(default=True, verbose_name="İstatistik Analiz Araçları")

    # Analiz Limitleri
    analiz_max_records = models.PositiveIntegerField(
        default=500,
        verbose_name="Analiz Maks. Kayıt Sayısı",
        help_text="Tez & Makale Analizi ve TR Dizin Makale Analizi için işlenecek maksimum kayıt sayısı. (default: 500)",
    )
    scrap_max_records = models.PositiveIntegerField(
        default=5000,
        verbose_name="Scraping Maks. Kayıt Sayısı",
        help_text="TR Dizin, OpenAlex ve OAI-PMH scraperlarının çekebileceği maksimum kayıt sayısı. (default: 5000)",
    )

    # Bibliometrik Analiz Fiyatlandırma (TL)
    biblio_price_500 = models.PositiveIntegerField(default=500, verbose_name="0-500 kayıt fiyatı (TL)")
    biblio_price_2000 = models.PositiveIntegerField(default=900, verbose_name="501-2000 kayıt fiyatı (TL)")
    biblio_price_3000 = models.PositiveIntegerField(default=1300, verbose_name="2001-3000 kayıt fiyatı (TL)")
    biblio_price_4000 = models.PositiveIntegerField(default=1700, verbose_name="3001-4000 kayıt fiyatı (TL)")
    biblio_price_5000 = models.PositiveIntegerField(default=2100, verbose_name="4001-5000 kayıt fiyatı (TL)")

    class Meta:
        verbose_name = "Site Ayarı"
        verbose_name_plural = "Site Ayarları"

    def __str__(self):
        return "Site Ayarları"

    def save(self, *args, **kwargs):
        # Sadece tek kayıt olsun
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Silmeyi engelle

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ═══════════════════════════════════════════════════════════════════════════════
# BLOG SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════════

class BlogCategory(models.Model):
    """Blog kategorileri"""
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default="bi-folder", verbose_name="İkon")
    color = models.CharField(max_length=20, default="#00d2ff", verbose_name="Renk")
    order = models.IntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Blog Kategorisi"
        verbose_name_plural = "Blog Kategorileri"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    """Blog etiketleri — araç ve konu bazlı filtreleme için (Excel, Power BI, Python vb.)"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Etiket Adı")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Blog Etiketi"
        verbose_name_plural = "Blog Etiketleri"
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Blog yazıları"""
    STATUS_CHOICES = (
        ('draft', 'Taslak'),
        ('published', 'Yayında'),
    )

    title = models.CharField(max_length=200, verbose_name="Başlık")
    slug = models.SlugField(unique=True, max_length=250)
    excerpt = models.TextField(max_length=300, verbose_name="Özet", help_text="Kısa açıklama (liste görünümünde gösterilir)")
    content = models.TextField(verbose_name="İçerik", help_text="Maksimum 50.000 karakter (~8.000 kelime)")
    cover_image = models.ImageField(upload_to='blog/covers/', storage=get_storage, blank=True, null=True, verbose_name="Kapak Görseli")

    LEVEL_CHOICES = (
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name="Yazar")
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name="Kategori")
    tags = models.ManyToManyField('BlogTag', blank=True, related_name='posts', verbose_name="Etiketler")
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, blank=True, verbose_name="Seviye",
                             help_text="Hedef okuyucu kitlesi (boş bırakılabilir)")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Durum")
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")

    views = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme")
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts', verbose_name="Beğeniler")

    # SEO
    meta_title = models.CharField(max_length=70, blank=True, verbose_name="SEO Başlık")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="SEO Açıklama")

    # LinkedIn paylaşım takibi
    shared_to_linkedin = models.BooleanField(default=False, verbose_name="LinkedIn'e Paylaşıldı")
    linkedin_share_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Yayın Tarihi")

    class Meta:
        verbose_name = "Blog Yazısı"
        verbose_name_plural = "Blog Yazıları"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.content and len(self.content) > 50000:
            raise ValidationError({'content': f'İçerik 50.000 karakteri aşamaz. Şu an: {len(self.content)} karakter.'})

    def save(self, *args, **kwargs):
        from django.utils import timezone
        self.full_clean()  # Validasyonu çalıştır
        # Yayına alındığında tarih ata
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Tahmini okuma süresi (dakika)"""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    @property
    def total_likes(self):
        return self.likes.count()


# ─── ÇALIŞMA ODALARI ─────────────────────────────────────────────────────────

STUDYROOM_TERMS = """
<h6 class="fw-semibold text-white mb-3">Çalışma Odası Kurulum Koşulları ve Sorumlulukları</h6>
<ol class="text-white-50 small" style="line-height:2;">
  <li><strong class="text-white">Konu Sadakati:</strong> Oluşturduğunuz oda yalnızca belirttiğiniz konu ve hedef doğrultusunda kullanılacaktır. Konu dışı içerik, reklam veya alakasız tartışmalar yasaktır.</li>
  <li><strong class="text-white">Akademik Dürüstlük:</strong> Oda içinde paylaşılan tüm içerikler akademik etik kurallara uygun olacaktır. İntihal, sahte veri veya yanıltıcı bilgi paylaşımı yasaktır.</li>
  <li><strong class="text-white">Süre Sınırı:</strong> Odalar en fazla <strong class="text-white">90 gün (3 ay)</strong> aktif kalabilir. Bitiş tarihinde oda otomatik arşive alınır; içerikler okunabilir ve aranabilir olmaya devam eder, yeni gönderi kabul edilmez.</li>
  <li><strong class="text-white">Moderasyon Sorumluluğu:</strong> Oda kurucusu olarak tartışmaların platform kurallarına uygunluğunu takip etmekle yükümlüsünüz. Kural ihlali gördüğünüzde platform yönetimine bildirmeniz beklenmektedir.</li>
  <li><strong class="text-white">Üye Limiti:</strong> Odanız belirlediğiniz maksimum üye sayısıyla sınırlıdır. Limit artışı için platform yönetimine başvurabilirsiniz.</li>
  <li><strong class="text-white">Platform Kuralları:</strong> Analizus Topluluk Kuralları bu oda için de geçerlidir. Odanızda gerçekleşen ihlallerden kurucu sorumlu tutulabilir.</li>
  <li><strong class="text-white">Yönetici Müdahalesi:</strong> Platform yöneticileri kural ihlali halinde odayı kapatma, içerik silme veya üye çıkarma hakkını saklı tutar.</li>
  <li><strong class="text-white">Ticari Kullanım Yasağı:</strong> Çalışma odaları ücretli kurs, reklam veya ticari satış amacıyla kullanılamaz.</li>
  <li><strong class="text-white">Veri Gizliliği:</strong> Oda üyelerinin kişisel bilgilerini izinsiz paylaşmak yasaktır.</li>
  <li><strong class="text-white">Tek Aktif Oda Hakkı:</strong> Her kullanıcı aynı anda yalnızca 1 aktif çalışma odası kurabilir.</li>
</ol>
"""


class StudyRoom(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('active', 'Aktif'),
        ('archived', 'Arşiv'),
        ('rejected', 'Reddedildi'),
    ]

    title = models.CharField(max_length=200, verbose_name="Oda Başlığı")
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(verbose_name="Açıklama")
    goal = models.TextField(max_length=500, verbose_name="Hedef")
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='study_rooms', verbose_name="İlgili Kategori"
    )
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_rooms', verbose_name="Kurucu"
    )
    ends_at = models.DateTimeField(verbose_name="Bitiş Tarihi")
    max_members = models.PositiveIntegerField(default=20, verbose_name="Maksimum Üye")
    is_public = models.BooleanField(default=True, verbose_name="Herkese Açık")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    creator_bio = models.CharField(max_length=300, blank=True, verbose_name="Kurucu Tanıtımı")

    # Şartname onayı
    terms_agreed = models.BooleanField(default=False, verbose_name="Şartname Onaylandı")
    terms_agreed_at = models.DateTimeField(null=True, blank=True, verbose_name="Şartname Onay Tarihi")

    # Admin inceleme
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='reviewed_rooms', verbose_name="İnceleyen"
    )
    review_note = models.TextField(blank=True, verbose_name="İnceleme Notu")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Çalışma Odası"
        verbose_name_plural = "Çalışma Odaları"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('studyroom_detail', kwargs={'slug': self.slug})

    @property
    def member_count(self):
        return self.memberships.count()

    @property
    def post_count(self):
        return self.room_posts.count()

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.ends_at

    def auto_archive_if_expired(self):
        from django.utils import timezone
        if self.status == 'active' and timezone.now() > self.ends_at:
            self.status = 'archived'
            self.save(update_fields=['status'])
            return True
        return False

    def days_remaining(self):
        from django.utils import timezone
        if self.status != 'active':
            return 0
        delta = self.ends_at - timezone.now()
        return max(0, delta.days)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base = slugify(self.title)[:180]
            self.slug = f"{base}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)


class StudyRoomMembership(models.Model):
    ROLE_CHOICES = [
        ('creator', 'Kurucu'),
        ('member', 'Üye'),
    ]
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'user')
        verbose_name = "Oda Üyeliği"
        verbose_name_plural = "Oda Üyelikleri"

    def __str__(self):
        return f"{self.user.username} @ {self.room.title}"


class StudyRoomPost(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='room_posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_posts')
    message = models.TextField(verbose_name="Mesaj")
    file = models.FileField(upload_to='studyrooms/', storage=get_storage, null=True, blank=True, verbose_name="Dosya")
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True, verbose_name="Düzenleme Zamanı")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Oda Gönderisi"
        verbose_name_plural = "Oda Gönderileri"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('studyroom_detail', kwargs={'slug': self.room.slug})

    def __str__(self):
        return f"{self.author.username}: {self.message[:60]}"


class TeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name="İsim Soyisim")
    title = models.CharField(max_length=100, verbose_name="Ünvan/Görev")
    bio = models.TextField(verbose_name="Kısa Özgeçmiş")
    image = models.ImageField(upload_to="team/", storage=get_storage, blank=True, null=True, verbose_name="Fotoğraf")
    skills = models.CharField(max_length=200, blank=True, help_text="Virgülle ayırarak yazın (örn: SPSS, R Studio, Ölçek Geliştirme)", verbose_name="Yetenekler/Etiketler")
    username = models.CharField(max_length=150, blank=True, help_text="Analizus kullanıcı adı (profil linki için)", verbose_name="Kullanıcı Adı")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        ordering = ['order']
        verbose_name = "Ekip Üyesi"
        verbose_name_plural = "Ekip Üyeleri"

    def __str__(self):
        return self.name

    def get_profile_url(self):
        return f"/profile/{self.username}/" if self.username else None

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',')] if self.skills else []


class ProjectRequest(models.Model):
    ANALYSIS_CHOICES = [
        ('visualization', 'Veri Görselleştirme'),
        ('ml', 'Makine Öğrenmesi / Yapay Zeka'),
        ('statistics', 'İstatistiksel Analiz'),
        ('cleaning', 'Veri Temizleme / Hazırlama'),
        ('timeseries', 'Zaman Serisi Analizi'),
        ('nlp', 'Metin / NLP Analizi'),
        ('literature', 'Tez / Makale Veri İndirme'),
        ('other', 'Diğer'),
    ]
    DATA_SIZE_CHOICES = [
        ('small', '1.000 satırdan az'),
        ('medium', '1.000 – 100.000 satır'),
        ('large', '100.000 satır ve üzeri'),
        ('unknown', 'Bilmiyorum'),
    ]
    TIMELINE_CHOICES = [
        ('urgent', '1 hafta içinde'),
        ('short', '1 ay içinde'),
        ('flexible', 'Esnek'),
    ]
    STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('in_review', 'İnceleniyor'),
        ('contacted', 'İletişime Geçildi'),
        ('closed', 'Kapatıldı'),
    ]

    SOURCE_CHOICES = [
        ('direct', 'Doğrudan Form'),
        ('yoktez', 'YÖK Tez'),
        ('trdizin', 'TR Dizin'),
    ]

    name = models.CharField(max_length=150, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    company = models.CharField(max_length=200, blank=True, verbose_name="Kişi / Şirket / Kurum")
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_CHOICES, verbose_name="Analiz Türü")
    description = models.TextField(verbose_name="Proje Açıklaması")
    data_size = models.CharField(max_length=20, choices=DATA_SIZE_CHOICES, verbose_name="Veri Boyutu")
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, verbose_name="Süre Beklentisi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Durum")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct', blank=True, verbose_name="Kaynak")
    admin_notes = models.TextField(blank=True, verbose_name="Admin Notları")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proje Talebi"
        verbose_name_plural = "Proje Talepleri"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.get_analysis_type_display()} ({self.created_at.strftime('%d.%m.%Y')})"


class SiteVisit(models.Model):
    """Toplam site ziyaretçi sayacı — tek satır, atomik artırım."""
    total_visits = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Site Ziyaret Sayacı"

    @classmethod
    def increment(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        if not created:
            cls.objects.filter(pk=1).update(total_visits=models.F('total_visits') + 1)

    @classmethod
    def get_count(cls):
        try:
            return cls.objects.get(pk=1).total_visits
        except cls.DoesNotExist:
            return 0
