from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('istatistik', '0003_add_ttesti_anova_tools'),
    ]

    operations = [
        migrations.AlterField(
            model_name='istatistikjob',
            name='tool',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('cronbach', 'Güvenilirlik Analizi (Cronbach Alpha)'),
                    ('normallik', 'Normallik Testi'),
                    ('betimsel', 'Betimleyici İstatistik'),
                    ('korelasyon', 'Korelasyon Matrisi'),
                    ('ttesti', 't-Testi'),
                    ('anova', 'Tek Yönlü ANOVA'),
                    ('mann_whitney', 'Mann-Whitney U Testi'),
                    ('kruskal_wallis', 'Kruskal-Wallis H Testi'),
                ],
            ),
        ),
    ]
