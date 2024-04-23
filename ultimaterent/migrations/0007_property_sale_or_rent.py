# Generated by Django 4.0.3 on 2024-01-07 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0006_property_balconies_property_bathroom_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='sale_or_rent',
            field=models.CharField(choices=[('sale', 'For Sale'), ('rent', 'For Rent')], default='sale', max_length=4, verbose_name='Property For'),
        ),
    ]
