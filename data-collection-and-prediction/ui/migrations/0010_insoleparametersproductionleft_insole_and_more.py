# Generated by Django 4.2.6 on 2024-03-19 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0009_predictionsleft_insole_predictionsright_insole_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='insoleparametersproductionleft',
            name='Insole',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ui.insole'),
        ),
        migrations.AddField(
            model_name='insoleparametersproductionright',
            name='Insole',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ui.insole'),
        ),
    ]
