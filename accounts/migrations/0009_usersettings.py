                                               

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_lead_overdue_alert_sent_at_lead_reminder_sent_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('dark', 'Dark'), ('light', 'Light')], default='dark', max_length=10)),
                ('accent_color', models.CharField(default='#12bfae', max_length=7)),
                ('email_notifications', models.BooleanField(default=True)),
                ('lead_notifications', models.BooleanField(default=True)),
                ('followup_reminders', models.BooleanField(default=True)),
                ('overdue_alerts', models.BooleanField(default=True)),
                ('automation_enabled', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
