# Generated by Django 4.2.6 on 2024-02-15 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0040_participant_lock_sync'),
        ('dataInspection', '0026_insoleparameterleft_comments_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='animatedpressure',
            name='animationPoster',
            field=models.FileField(blank=True, null=True, upload_to='feet-animation'),
        ),
        migrations.AlterField(
            model_name='animatedpressure',
            name='uploadedFile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='animation', to='participants.uploadedfile'),
        ),
    ]
