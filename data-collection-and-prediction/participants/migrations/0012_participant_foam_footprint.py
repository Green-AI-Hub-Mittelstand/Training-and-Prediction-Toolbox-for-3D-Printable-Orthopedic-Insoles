# Generated by Django 4.2.6 on 2023-11-13 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0011_participant_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='foam_footprint',
            field=models.BooleanField(blank=True, default=False, verbose_name='Teilnehmer*in hat Fußabdruck abgegeben'),
        ),
    ]