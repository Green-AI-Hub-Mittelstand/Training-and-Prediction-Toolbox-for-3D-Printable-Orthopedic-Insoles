# Generated by Django 4.2.6 on 2024-03-12 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='age',
            field=models.IntegerField(null=True, verbose_name='Alter'),
        ),
        migrations.AddField(
            model_name='customer',
            name='comments_experimenter',
            field=models.TextField(blank=True, default='', verbose_name='Kommentare Experimenter'),
        ),
        migrations.AddField(
            model_name='customer',
            name='comments_participant',
            field=models.TextField(blank=True, default='', verbose_name='Kommentare Teilnehmer'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gender',
            field=models.CharField(choices=[('m', 'männlich'), ('w', 'weiblich'), ('d', 'divers'), ('-', '-')], default='-', max_length=3, verbose_name='Geschlecht'),
        ),
        migrations.AddField(
            model_name='customer',
            name='heel_spur_left',
            field=models.BooleanField(blank=True, default=False, help_text='Ein Fersensporn ist eine wenige Millimeter kleine dornartige Verknöcherung an der Ferse.', verbose_name='Fersensporn links'),
        ),
        migrations.AddField(
            model_name='customer',
            name='heel_spur_right',
            field=models.BooleanField(blank=True, default=False, verbose_name='Fersensporn rechts'),
        ),
        migrations.AddField(
            model_name='customer',
            name='height',
            field=models.IntegerField(null=True, verbose_name='Größe in cm'),
        ),
        migrations.AddField(
            model_name='customer',
            name='leg_shortening_left',
            field=models.IntegerField(default='0', help_text='Ein Verkürzungsausgleich dient u.a. zum Ausgleich einer Beinverkürzung sowie Skoliose', verbose_name='Verkürzungsausgleich links in cm'),
        ),
        migrations.AddField(
            model_name='customer',
            name='leg_shortening_right',
            field=models.IntegerField(default='0', verbose_name='Verkürzungsausgleich rechts in cm'),
        ),
        migrations.AddField(
            model_name='customer',
            name='pain_points',
            field=models.JSONField(blank=True, default=dict, verbose_name='Schmerzpunkte'),
        ),
        migrations.AddField(
            model_name='customer',
            name='pain_points_render',
            field=models.FileField(blank=True, null=True, upload_to='pain_points'),
        ),
        migrations.AddField(
            model_name='customer',
            name='shoe_size',
            field=models.FloatField(choices=[(-1.0, '-1.0'), (30.0, '30'), (30.5, '30.5'), (31.0, '31'), (31.5, '31.5'), (32.0, '32'), (32.5, '32.5'), (33.0, '33'), (33.5, '33.5'), (34.0, '34'), (34.5, '34.5'), (35.0, '35'), (35.5, '35.5'), (36.0, '36'), (36.5, '36.5'), (37.0, '37'), (37.5, '37.5'), (38.0, '38'), (38.5, '38.5'), (39.0, '39'), (39.5, '39.5'), (40.0, '40'), (40.5, '40.5'), (41.0, '41'), (41.5, '41.5'), (42.0, '42'), (42.5, '42.5'), (43.0, '43'), (43.5, '43.5'), (44.0, '44'), (44.5, '44.5'), (45.0, '45'), (45.5, '45.5'), (46.0, '46'), (46.5, '46.5'), (47.0, '47'), (47.5, '47.5'), (48.0, '48'), (48.5, '48.5'), (49.0, '49'), (49.5, '49.5'), (50.0, '50'), (50.5, '50.5'), (51.0, '51'), (51.5, '51.5'), (52.0, '52')], null=True, verbose_name='Schuhgröße'),
        ),
        migrations.AddField(
            model_name='customer',
            name='weight',
            field=models.IntegerField(null=True, verbose_name='Gewicht in kg'),
        ),
    ]
