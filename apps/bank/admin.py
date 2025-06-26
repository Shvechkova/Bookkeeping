from django.contrib import admin

from apps.bank.models import Bank, CategForPercentGroupBank, CategNalog, CategOperationsBetweenBank, GroupeOperaccount, GroupeSalary
from apps.service.models import SubcontractOtherCategory

# Register your models here.
admin.site.register(Bank)
admin.site.register(GroupeOperaccount)
admin.site.register(GroupeSalary)
admin.site.register(CategNalog)
admin.site.register(SubcontractOtherCategory)
admin.site.register(CategForPercentGroupBank)
admin.site.register(CategOperationsBetweenBank)