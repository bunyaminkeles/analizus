from django.core.management.base import BaseCommand
from forum.models import Skill
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Analizus platformu için yetenekler (skills) listesini veritabanına yükler.'

    def handle(self, *args, **kwargs):
        skills_data = [
            # İstatistik & Analiz Yazılımları
            "SPSS", "R Studio", "Stata", "SAS", "Minitab", "EViews", "JASP", "Jamovi", "AMOS", "SmartPLS", "LISREL",
            
            # Programlama & Veri Bilimi
            "Python", "R", "SQL", "MATLAB", "Julia", "C++", "Java", "Scala",
            "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Hadoop", "Spark",
            
            # İş Zekası & Görselleştirme
            "Excel", "Power BI", "Tableau", "QlikView", "Google Data Studio", "Looker", "D3.js",
            
            # Nitel Analiz
            "MAXQDA", "NVivo", "Atlas.ti", "Quirkos",
            
            # Akademik & Metodoloji
            "Akademik Yazım", "Literatür Taraması", "Tez Danışmanlığı", "Anket Tasarımı", 
            "Araştırma Yöntemleri", "Etik Kurul Başvurusu", "Turnitin Raporlama", "Bibliyometrik Analiz",
            
            # İstatistiksel Yöntemler
            "Regresyon Analizi", "Faktör Analizi", "Yapısal Eşitlik Modellemesi (SEM)", 
            "Zaman Serisi Analizi", "Meta-Analiz", "Güç Analizi (G*Power)", "Biyoistatistik", "Ekonometri"
        ]

        self.stdout.write("Yetenekler listesi yükleniyor...")
        
        count = 0
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'slug': slugify(skill_name)}
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'İşlem tamamlandı! {count} yeni yetenek eklendi.'))