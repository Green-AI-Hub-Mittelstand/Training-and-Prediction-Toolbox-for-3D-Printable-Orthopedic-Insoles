# Generated by Django 4.2.6 on 2023-11-21 16:03

from django.db import migrations



def create_tokens(apps, schema_editor):
    # Get all existing users
    User = apps.get_model('auth', 'User')
    Token = apps.get_model('authtoken',"Token")
    users = User.objects.all()

    Token.objects.all().delete()

    for user in users:
        # Check if the user already has a token
        Token.objects.get_or_create(user=user)
        


class Migration(migrations.Migration):

    dependencies = [
        ('synchronizer', '0002_logentry_direction'),
    ]

    operations = [
        migrations.RunPython(create_tokens),
    ]
