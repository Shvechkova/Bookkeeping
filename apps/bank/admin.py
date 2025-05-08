from django.contrib import admin

from apps.bank.models import Bank, GroupeOperaccount, GroupeSalary

# Register your models here.
admin.site.register(Bank)
admin.site.register(GroupeOperaccount)
admin.site.register(GroupeSalary)
