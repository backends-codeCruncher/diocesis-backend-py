# Generated by Django 5.1.7 on 2025-04-01 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrusel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrusel',
            name='isActive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='carrusel',
            name='url',
            field=models.URLField(),
        ),
    ]
