# Generated by Django 4.0.3 on 2024-02-09 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0023_remove_agent_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
