import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('trdizin', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MakaleAnaliz',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('query_summary', models.CharField(blank=True, max_length=500)),
                ('status', models.CharField(choices=[('pending', 'Bekliyor'), ('running', 'Çalışıyor'), ('completed', 'Tamamlandı'), ('failed', 'Başarısız')], default='pending', max_length=20)),
                ('total_records', models.IntegerField(default=0)),
                ('analysis_data', models.JSONField(blank=True, default=dict)),
                ('pdf_url', models.URLField(blank=True, default='', max_length=500)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='makale_analizler', to=settings.AUTH_USER_MODEL)),
                ('dizin_job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analizler', to='trdizin.dizinsearchjob')),
            ],
            options={
                'verbose_name': 'Makale Analizi',
                'verbose_name_plural': 'Makale Analizleri',
                'ordering': ['-created_at'],
            },
        ),
    ]
