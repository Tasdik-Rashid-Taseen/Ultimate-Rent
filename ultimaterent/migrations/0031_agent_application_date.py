# Generated by Django 4.0.3 on 2024-02-15 09:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0030_agent_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='application_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
