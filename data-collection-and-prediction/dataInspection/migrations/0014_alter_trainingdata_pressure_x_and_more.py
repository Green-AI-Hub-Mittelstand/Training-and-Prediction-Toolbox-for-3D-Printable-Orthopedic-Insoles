# Generated by Django 4.2.6 on 2023-12-21 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0013_trainingdata_pressure_rot_trainingdata_pressure_x_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingdata',
            name='pressure_x',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='trainingdata',
            name='pressure_y',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
