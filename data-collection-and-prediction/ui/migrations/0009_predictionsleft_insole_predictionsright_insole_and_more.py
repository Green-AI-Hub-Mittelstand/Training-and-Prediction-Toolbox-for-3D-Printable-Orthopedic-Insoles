# Generated by Django 4.2.6 on 2024-03-19 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0008_remove_customer_comments_experimenter'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictionsleft',
            name='insole',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ui.insole'),
        ),
        migrations.AddField(
            model_name='predictionsright',
            name='insole',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ui.insole'),
        ),
        migrations.AlterField(
            model_name='insole',
            name='pressureFileLeft',
            field=models.FileField(null=True, upload_to='pressureFile/'),
        ),
        migrations.AlterField(
            model_name='insole',
            name='pressureFileRight',
            field=models.FileField(null=True, upload_to='pressureFile/'),
        ),
    ]