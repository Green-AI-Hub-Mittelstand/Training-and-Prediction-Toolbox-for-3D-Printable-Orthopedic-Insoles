# Generated by Django 4.2.6 on 2023-11-15 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0019_participant_desinfected_everything'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfile',
            name='upload_type',
            field=models.CharField(default='other', max_length=20),
        ),
    ]