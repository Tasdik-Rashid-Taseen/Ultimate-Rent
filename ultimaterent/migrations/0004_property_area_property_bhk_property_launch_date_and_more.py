# Generated by Django 4.0.3 on 2023-12-31 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0003_remove_property_photo_propertyimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='area',
            field=models.DecimalField(decimal_places=2, default=100.0, max_digits=7),
        ),
        migrations.AddField(
            model_name='property',
            name='bhk',
            field=models.CharField(default='1 BHK', max_length=50),
        ),
        migrations.AddField(
            model_name='property',
            name='launch_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='possession_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='price_range',
            field=models.CharField(default='₹0 L - ₹0 L', max_length=100),
        ),
    ]
