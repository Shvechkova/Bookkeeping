from django.contrib import admin

from apps.employee.models import CategoryEmployee, Employee, EmployeeInCAtegory

class EmployeeInCAtegoryInline(admin.TabularInline):
    model = EmployeeInCAtegory
    extra = 1
    fields = (
        "category",
    )
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "is_active"]
    inlines = [
        EmployeeInCAtegoryInline,
    ]

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(CategoryEmployee)