# Generated by Django 4.2.6 on 2023-12-21 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0012_foamprintanalysis_scaledimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingdata',
            name='pressure_rot',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AddField(
            model_name='trainingdata',
            name='pressure_x',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AddField(
            model_name='trainingdata',
            name='pressure_y',
            field=models.FloatField(blank=True, default=0.0),
        ),
    ]