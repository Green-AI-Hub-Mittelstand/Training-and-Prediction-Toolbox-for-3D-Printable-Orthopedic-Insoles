# Generated by Django 4.2.6 on 2023-11-23 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0028_merge_20231121_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataprotection',
            name='public_id',
            field=models.IntegerField(default=-1),
        ),
    ]
