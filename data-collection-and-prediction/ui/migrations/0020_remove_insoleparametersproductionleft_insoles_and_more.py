# Generated by Django 4.2.6 on 2024-04-03 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0019_alter_predictedpointleft_predictions_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='insoleparametersproductionleft',
            name='insoles',
        ),
        migrations.RemoveField(
            model_name='insoleparametersproductionright',
            name='insoles',
        ),
        migrations.AddField(
            model_name='insoleparametersproductionleft',
            name='insole',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leftParameters', to='ui.insole'),
        ),
        migrations.AddField(
            model_name='insoleparametersproductionright',
            name='insole',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rightParameters', to='ui.insole'),
        ),
    ]
