# Generated by Django 4.2.6 on 2024-03-27 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0016_remove_predictionsleft_insoles_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='predictionsleft',
            name='insoleParameters',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='ui.insoleparametersproductionleft'),
        ),
        migrations.AlterField(
            model_name='predictionsright',
            name='insoleParameters',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='ui.insoleparametersproductionright'),
        ),
    ]
