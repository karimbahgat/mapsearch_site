# Generated by Django 3.0.5 on 2020-04-29 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapsearch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='thumbnail',
            field=models.BinaryField(blank=True),
        ),
    ]