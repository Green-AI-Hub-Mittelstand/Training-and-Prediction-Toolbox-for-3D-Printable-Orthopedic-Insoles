# Generated by Django 4.2.6 on 2023-12-03 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0004_trainingdata_validated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingdata',
            name='foamPrint',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dataInspection.foamprintanalysis'),
        ),
    ]
