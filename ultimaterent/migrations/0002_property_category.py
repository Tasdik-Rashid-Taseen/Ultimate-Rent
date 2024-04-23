# Generated by Django 4.0.3 on 2023-11-06 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='category',
            field=models.CharField(choices=[('AP', 'Apartment'), ('VL', 'Villa'), ('HM', 'Home'), ('OF', 'Office')], default='AP', max_length=2),
        ),
    ]