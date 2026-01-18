import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import FreelanceJob, JobProposal, Category, Profile

class Command(BaseCommand):
    help = 'Freelance Market için örnek ilanlar ve teklifler oluşturur'

    def handle(self, *args, **kwargs):
        self.stdout.write("💼 Market verileri yükleniyor...")

        # Temizlik (Önce teklifleri sil, çünkü ilanlara bağlılar)
        JobProposal.objects.all().delete()
        FreelanceJob.objects.all().delete()

        # 1. Kullanıcıları Oluştur/Getir
        users_config = [
            ('AnalizUzmani_1', 'expert', 'İstatistikçi'),
            ('PythonDev_X', 'expert', 'Python Geliştirici'),
            ('TezMagduru_A', 'member', 'Yüksek Lisans Öğrencisi'),
            ('Arastirmaci_B', 'active', 'Doktora Öğrencisi'),
            ('SirketSahibi_C', 'premium', 'Proje Yöneticisi'),
        ]
        
        users = {}
        for username, rank, title in users_config:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('1234')
                user.save()
                # Profil oluştur
                Profile.objects.get_or_create(user=user)
            
            # Rütbe ve unvan güncelle
            if hasattr(user, 'profile'):
                user.profile.rank = rank
                user.profile.title = title
                user.profile.save()
            
            users[username] = user

        # 2. Kategorileri Getir
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.WARNING("⚠️ Kategori bulunamadı. Lütfen önce 'load_sample_data' komutunu çalıştırın."))
            return

        def get_category(slug_part):
            for cat in categories:
                if slug_part in cat.slug:
                    return cat
            return random.choice(categories)

        # 3. Örnek İlan Verileri
        jobs_data = [
            {
                'owner': 'TezMagduru_A',
                'title': 'SPSS ile Anket Verisi Analizi',
                'description': '150 kişilik anket verim var. T-test ve ANOVA analizleri yapılması gerekiyor. Raporlama dahil.',
                'budget_min': 500,
                'budget_max': 1000,
                'cat_slug': 'spss',
                'status': 'open'
            },
            {
                'owner': 'Arastirmaci_B',
                'title': 'Python ile Web Scraping Botu',
                'description': 'Emlak sitesinden veri çekecek bir bot lazım. Veriler Excel\'e kaydedilmeli.',
                'budget_min': 2000,
                'budget_max': 3000,
                'cat_slug': 'python',
                'status': 'open'
            },
            {
                'owner': 'SirketSahibi_C',
                'title': 'Satış Verileri Görselleştirme (Dashboard)',
                'description': 'Aylık satış verilerini görselleştirmek için Power BI veya Excel dashboard istiyorum.',
                'budget_min': 1500,
                'budget_max': 2500,
                'cat_slug': 'excel',
                'status': 'in_progress'
            },
            {
                'owner': 'TezMagduru_A',
                'title': 'Tez Düzenleme ve Formatlama',
                'description': 'Tezimin APA 7 formatına uygun hale getirilmesi gerekiyor.',
                'budget_min': 750,
                'budget_max': 1250,
                'cat_slug': 'tez',
                'status': 'completed'
            },
            {
                'owner': 'Arastirmaci_B',
                'title': 'R Studio ile Zaman Serisi Analizi',
                'description': 'ARIMA modeli kurulacak ve tahminleme yapılacak.',
                'budget_min': 1000,
                'budget_max': 2000,
                'cat_slug': 'r-programlama',
                'status': 'open'
            }
        ]

        experts = [users['AnalizUzmani_1'], users['PythonDev_X']]

        for data in jobs_data:
            owner = users.get(data['owner'])
            category = get_category(data['cat_slug'])
            
            job = FreelanceJob.objects.create(
                owner=owner,
                title=data['title'],
                description=data['description'],
                budget_min=data['budget_min'],
                budget_max=data['budget_max'],
                category=category,
                status=data['status']
            )
            self.stdout.write(f"✅ İlan: {job.title} ({job.get_status_display()})")

            # 4. Teklifler Oluştur
            if job.status != 'cancelled':
                potential_experts = [e for e in experts if e != owner]
                
                # Eğer iş devam ediyorsa veya tamamlandıysa, bir teklif kabul edilmiş olmalı
                accepted_expert = None
                if job.status in ['in_progress', 'completed']:
                    accepted_expert = random.choice(potential_experts)

                for expert in potential_experts:
                    # Teklif durumu belirle
                    proposal_status = 'pending'
                    if expert == accepted_expert:
                        proposal_status = 'accepted'
                    elif accepted_expert: 
                        proposal_status = 'rejected'

                    JobProposal.objects.create(
                        job=job,
                        expert=expert,
                        price=random.randint(int(job.budget_min), int(job.budget_max)),
                        duration=f"{random.randint(3, 10)} gün",
                        message=f"Merhaba, {category.title} konusunda deneyimliyim. İşi istediğiniz sürede teslim edebilirim.",
                        status=proposal_status
                    )
                    self.stdout.write(f"   ➡️ Teklif: {expert.username} ({proposal_status})")

        self.stdout.write(self.style.SUCCESS("🎉 Market verileri başarıyla yüklendi!"))