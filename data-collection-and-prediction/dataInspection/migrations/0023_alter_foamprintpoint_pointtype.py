# Generated by Django 4.2.6 on 2024-02-13 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataInspection', '0022_insoleparameterleft_pelotten_form_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foamprintpoint',
            name='pointType',
            field=models.IntegerField(choices=[(-1, '-- nicht erkannt --'), (0, 'Vorderster Punkt'), (1, 'Zehe 1'), (2, 'Zehe 2'), (3, 'Zehe 3'), (4, 'Zehe 4'), (5, 'Zehe 5'), (6, 'Ballenpunkt Innen'), (7, 'Ballenpunkt Aussen'), (8, 'Mittelfusskoepfchen 1'), (9, 'Mittelfusskoepfchen 2'), (10, 'Mittelfusskoepfchen 3'), (11, 'Mittelfusskoepfchen 4'), (12, 'Mittelfusskoepfchen 5'), (13, 'Pelottenpunkt'), (14, 'Basis MFK 5'), (15, 'Laengsgewoelbestuetze'), (16, 'Fersenspornpunkt'), (17, 'Fersenmittelpunkt'), (18, 'Fersenbreite Aussen'), (19, 'Fersenbreite Innen'), (20, 'Hinterster Punkt'), (21, 'Schnittachse')], default=-1),
        ),
    ]
