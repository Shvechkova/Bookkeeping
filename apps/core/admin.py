from django.contrib import admin

from apps.core.models import LogsError, Logsinfo
class LogsErrorAdmin(admin.ModelAdmin):
    list_display_links = None
    list_display = [
        "location",
        "info",
        "created_timestamp",
    ]
    
class LogsinfoAdmin(admin.ModelAdmin):
    search_fields = [
        "info",
    ]
    list_display_links = None
    list_display = [
        "location",
        "info",
        "created_timestamp",
    ]  
# Register your models here.
admin.site.register(LogsError,LogsErrorAdmin)
admin.site.register(Logsinfo,LogsinfoAdmin)