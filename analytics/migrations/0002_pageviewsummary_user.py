import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pageviewsummary',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='pageviewsummary',
            name='unique_users',
        ),
        migrations.AddField(
            model_name='pageviewsummary',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='page_view_summaries',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='pageviewsummary',
            unique_together={('date', 'path', 'user')},
        ),
    ]
