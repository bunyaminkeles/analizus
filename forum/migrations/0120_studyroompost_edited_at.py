from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0119_sitesettings_feature_semanticscholar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyroompost',
            name='edited_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Düzenleme Zamanı'),
        ),
    ]
