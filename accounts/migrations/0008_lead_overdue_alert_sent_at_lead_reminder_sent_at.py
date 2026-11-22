                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_autoreply'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='overdue_alert_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='reminder_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
