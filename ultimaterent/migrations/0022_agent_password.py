# Generated by Django 4.0.3 on 2024-02-09 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0021_agent_email_agent_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='password',
            field=models.CharField(default='', max_length=128),
        ),
    ]
