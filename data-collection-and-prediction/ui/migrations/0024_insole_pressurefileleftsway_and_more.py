# Generated by Django 4.2.6 on 2024-05-02 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0023_rename_pressurefileleft_insole_pressurefileleftwalk_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='insole',
            name='pressureFileLeftSway',
            field=models.FileField(null=True, upload_to='pressureFile/sway'),
        ),
        migrations.AddField(
            model_name='insole',
            name='pressureFileRightSway',
            field=models.FileField(null=True, upload_to='pressureFile/sway'),
        ),
        migrations.AlterField(
            model_name='insole',
            name='pressureFileLeftWalk',
            field=models.FileField(null=True, upload_to='pressureFile/walk'),
        ),
        migrations.AlterField(
            model_name='insole',
            name='pressureFileRightWalk',
            field=models.FileField(null=True, upload_to='pressureFile/walk'),
        ),
    ]
