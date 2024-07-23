# Generated by Django 4.2.6 on 2024-04-03 12:18

from django.db import migrations, models
import django.db.models.deletion


def delete_insoles(apps, schema_editor):
    Insole = apps.get_model('ui', 'Insole')
    Insole.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0020_remove_insoleparametersproductionleft_insoles_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_insoles),
        migrations.RemoveField(
            model_name='predictionsright',
            name='insoleParameters',
        ),
        migrations.RemoveField(
            model_name='predictionsright',
            name='insoles',
        ),
        migrations.RemoveField(
            model_name='predictedpointleft',
            name='predictions',
        ),
        migrations.RemoveField(
            model_name='predictedpointright',
            name='predictions',
        ),
        migrations.AddField(
            model_name='predictedpointleft',
            name='params',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='points', to='ui.insoleparametersproductionleft'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='predictedpointright',
            name='params',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='points', to='ui.insoleparametersproductionright'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='PredictionsLeft',
        ),
        migrations.DeleteModel(
            name='PredictionsRight',
        ),
    ]
