# Generated by Django 3.0.5 on 2020-05-04 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapsearch', '0006_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('Point', 'Point'), ('LineString', 'LineString'), ('Polygon', 'Polygon')], max_length=30)),
                ('legend_symbol', models.TextField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('legend_description', models.ManyToManyField(blank=True, to='mapsearch.Text')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layers', to='mapsearch.Map')),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('geom', models.TextField(blank=True, null=True)),
                ('label', models.ManyToManyField(blank=True, to='mapsearch.Text')),
                ('layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='mapsearch.Layer')),
            ],
        ),
    ]