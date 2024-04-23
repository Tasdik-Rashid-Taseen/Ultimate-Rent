# Generated by Django 4.0.3 on 2023-11-11 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ultimaterent', '0002_property_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='photo',
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='property_images/')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='ultimaterent.property')),
            ],
        ),
    ]