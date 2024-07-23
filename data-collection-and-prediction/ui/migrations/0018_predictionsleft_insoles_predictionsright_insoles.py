# Generated by Django 4.2.6 on 2024-03-27 14:28

from django.db import migrations, models
import django.db.models.deletion

def delete_predictions_left(apps, schema_editor):
    PredictionsLeft = apps.get_model('ui', 'PredictionsLeft')
    PredictionsLeft.objects.all().delete()

def delete_predictions_right(apps, schema_editor):
    PredictionsRight = apps.get_model('ui', 'PredictionsRight')
    PredictionsRight.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0017_alter_predictionsleft_insoleparameters_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_predictions_left),
        migrations.RunPython(delete_predictions_right),
        migrations.AddField(
            model_name='predictionsleft',
            name='insoles',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ui.insole'),
        ),
        migrations.AddField(
            model_name='predictionsright',
            name='insoles',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ui.insole'),
        ),
    ]