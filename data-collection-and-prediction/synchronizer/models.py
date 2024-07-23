from django.db import models

# Create your models here.

class LogEntry(models.Model):
    
    RECEIVED = "received"
    SENT = "sent"
    
    CHOICES = (
        (RECEIVED, RECEIVED),
        (SENT, SENT),
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    entry = models.CharField(max_length=200)
    direction = models.CharField(max_length=20, default=RECEIVED)



from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created and not kwargs.get('raw', False):
        Token.objects.create(user=instance)