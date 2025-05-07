from django.contrib import admin

from apps.bank.models import Bank, GroupeOperaccount

# Register your models here.
admin.site.register(Bank)
admin.site.register(GroupeOperaccount)
