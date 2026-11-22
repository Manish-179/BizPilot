                                               

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='follow_up_completed',
            field=models.BooleanField(default=False),
        ),
    ]
