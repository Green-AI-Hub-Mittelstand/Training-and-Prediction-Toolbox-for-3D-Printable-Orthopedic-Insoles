# Generated by Django 4.2.6 on 2024-02-12 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0020_foamprintanalysis_leftfootcontrast_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trainingdata',
            options={'verbose_name': 'Aligned Pressure Recording (TrainingData)', 'verbose_name_plural': 'Aligned Pressure Recordings (TrainingData)'},
        ),
        migrations.AddField(
            model_name='trainingdata',
            name='fit_quality',
            field=models.IntegerField(choices=[(0, 'schlecht'), (1, 'mittel'), (2, 'gut')], default=2),
        ),
    ]