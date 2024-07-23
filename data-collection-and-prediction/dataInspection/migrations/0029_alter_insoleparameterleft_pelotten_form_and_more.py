# Generated by Django 4.2.6 on 2024-02-18 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0028_alter_insoleparameterleft_aussenrand_anheben_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insoleparameterleft',
            name='pelotten_form',
            field=models.IntegerField(choices=[(0, 'Schmal'), (1, 'Breit'), (2, 'Stufe')], default=0, verbose_name='Pelottenform'),
        ),
        migrations.AlterField(
            model_name='insoleparameterright',
            name='pelotten_form',
            field=models.IntegerField(choices=[(0, 'Schmal'), (1, 'Breit'), (2, 'Stufe')], default=0, verbose_name='Pelottenform'),
        ),
    ]