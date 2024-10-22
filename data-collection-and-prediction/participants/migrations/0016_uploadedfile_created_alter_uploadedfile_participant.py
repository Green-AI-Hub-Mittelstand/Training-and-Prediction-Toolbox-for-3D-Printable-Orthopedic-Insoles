# Generated by Django 4.2.6 on 2023-11-14 18:37

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0015_uploadedfile_participant'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='participant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploads', to='participants.participant'),
        ),
    ]
