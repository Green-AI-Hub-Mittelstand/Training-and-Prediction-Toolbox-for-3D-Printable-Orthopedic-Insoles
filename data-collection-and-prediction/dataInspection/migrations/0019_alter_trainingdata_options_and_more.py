# Generated by Django 4.2.6 on 2024-02-08 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0018_insoleparameterleft_insoleparameterright_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trainingdata',
            options={'verbose_name': 'Aligned Pressure Recording', 'verbose_name_plural': 'Aligned Pressure Recordings'},
        ),
        migrations.AddField(
            model_name='foamprintanalysis',
            name='scalingFactor',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='foamprintanalysis',
            name='scaledImage',
            field=models.FileField(blank=True, help_text='This is the correctly scaled image', null=True, upload_to='feet/'),
        ),
        migrations.AlterField(
            model_name='trainingdata',
            name='pressure_rot',
            field=models.FloatField(blank=True, default=0.0, help_text='Rotation of the pressure image on the foam print image'),
        ),
        migrations.AlterField(
            model_name='trainingdata',
            name='pressure_x',
            field=models.IntegerField(blank=True, default=0, help_text='Horizontal translation of the pressure image on the foam print image'),
        ),
        migrations.AlterField(
            model_name='trainingdata',
            name='pressure_y',
            field=models.IntegerField(blank=True, default=0, help_text='Vertical translation of the pressure image on the foam print image'),
        ),
    ]
