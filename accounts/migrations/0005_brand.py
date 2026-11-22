                                               

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/logos/')),
                ('primary_color', models.CharField(default='#12bfae', max_length=7)),
                ('secondary_color', models.CharField(default='#0b1220', max_length=7)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='brands/banners/')),
                ('tagline', models.CharField(blank=True, max_length=200)),
                ('storefront_enabled', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='brand', to='accounts.business')),
            ],
        ),
    ]
