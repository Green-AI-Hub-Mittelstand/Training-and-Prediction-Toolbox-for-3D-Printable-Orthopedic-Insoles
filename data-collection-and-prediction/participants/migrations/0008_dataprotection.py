# Generated by Django 4.2.6 on 2023-11-13 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0007_alter_participant_active_alter_participant_age_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataProtection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt')),
                ('svg', models.TextField()),
                ('pdf', models.FileField(blank=True, null=True, upload_to='')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
    ]