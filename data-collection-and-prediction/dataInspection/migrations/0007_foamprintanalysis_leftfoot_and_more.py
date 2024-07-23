# Generated by Django 4.2.6 on 2023-12-13 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0006_alter_trainingdata_foamprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='foamprintanalysis',
            name='leftFoot',
            field=models.FileField(blank=True, null=True, upload_to='feet/'),
        ),
        migrations.AddField(
            model_name='foamprintanalysis',
            name='rightFoot',
            field=models.FileField(blank=True, null=True, upload_to='feet/'),
        ),
    ]
