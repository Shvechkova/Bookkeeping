from django.contrib import admin

from apps.core.models import LogsError, Logsinfo

# Register your models here.
admin.site.register(LogsError)
admin.site.register(Logsinfo)