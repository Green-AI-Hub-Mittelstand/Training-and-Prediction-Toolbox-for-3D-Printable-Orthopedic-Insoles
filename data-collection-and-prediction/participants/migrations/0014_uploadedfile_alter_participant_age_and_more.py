# Generated by Django 4.2.6 on 2023-11-13 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0013_participant_pressure_plate_done'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
            ],
        ),
        migrations.AlterField(
            model_name='participant',
            name='age',
            field=models.IntegerField(default=-1, null=True, verbose_name='Alter'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='gender',
            field=models.CharField(choices=[('m', 'männlich'), ('w', 'weiblich'), ('d', 'diverse'), ('-', '-')], default='-', max_length=3, verbose_name='Geschlecht'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='height',
            field=models.IntegerField(default=-1, null=True, verbose_name='Höhe in cm'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='weight',
            field=models.IntegerField(default=-1, null=True, verbose_name='Gewicht in kg'),
        ),
    ]
