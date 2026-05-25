from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0117_privatemessage_edit_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_visits', models.PositiveBigIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Site Ziyaret Sayacı',
            },
        ),
    ]
