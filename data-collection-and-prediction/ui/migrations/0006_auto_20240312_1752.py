# Generated by Django 4.2.6 on 2024-03-12 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0005_insoleparametersproductionleft_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='comments_participant',
            new_name = 'comments_customer',
        ),
    ]
