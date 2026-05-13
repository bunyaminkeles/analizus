from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0113_blog_tez_savunmasi_istatistik_sorulari'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='username',
            field=models.CharField(blank=True, help_text='Analizus kullanıcı adı (profil linki için)', max_length=150, verbose_name='Kullanıcı Adı'),
        ),
    ]
