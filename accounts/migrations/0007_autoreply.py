                                               

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_lead_follow_up_completed'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trigger', models.CharField(choices=[('form', 'Website Form'), ('whatsapp', 'WhatsApp'), ('call', 'Phone Call')], max_length=20)),
                ('message', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auto_replies', to='accounts.business')),
            ],
        ),
    ]
