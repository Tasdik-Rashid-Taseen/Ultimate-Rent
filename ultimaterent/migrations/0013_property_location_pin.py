# Generated by Django 4.0.3 on 2024-01-29 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0012_visitschedule_property_visitschedule_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='location_pin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
