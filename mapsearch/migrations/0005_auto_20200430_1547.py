# Generated by Django 3.0.5 on 2020-04-30 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapsearch', '0004_auto_20200430_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='xmax',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='map',
            name='xmin',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='map',
            name='ymax',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='map',
            name='ymin',
            field=models.FloatField(null=True),
        ),
    ]
