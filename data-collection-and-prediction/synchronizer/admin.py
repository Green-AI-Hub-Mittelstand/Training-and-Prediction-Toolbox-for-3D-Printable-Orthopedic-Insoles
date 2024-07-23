from django.contrib import admin
from .models import *

# Register your models here.

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp','entry',)

admin.site.register(LogEntry, LogEntryAdmin)
