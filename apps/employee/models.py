from django.db import models

# Create your models here.
class CategoryEmployee(models.Model):
    name = models.CharField("Отдел сотрудника",max_length=200)
    
    class Meta:
        verbose_name = "Отдел сотрудников"
        verbose_name_plural = "Отделы сотрудников"
    
    def __str__(self):
        return self.name    

class Employee(models.Model):
    first_name = models.CharField("Имя",max_length=200)
    last_name = models.CharField("Фамилия",max_length=200)
    # TYPE = (
    #     ("INTERNAL", "Внешний"),
    #     ("EXTERNAL", "Внутренний"),
    # )
    # type = models.CharField(max_length=8, choices=TYPE, default="EXTERNAL")
    # category = models.ForeignKey(
    #     CategoryEmployee,
    #     on_delete=models.SET_NULL,
    #     verbose_name="Категория",
    #     blank=True,
    #     null=True,
    # )
    date_start = models.DateField("Дата приема", blank=True, null=True)
    date_end = models.DateField("Дата увольнения", blank=True, null=True)
    is_active = models.BooleanField("Действующий", default=True)
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
    
    def __str__(self):
        return self.last_name
    
class EmployeeInCAtegory(models.Model):
    category = models.ForeignKey(
        CategoryEmployee,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        blank=True,
        null=True,
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        verbose_name="Сотрудник",
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = "Отдел сотрудника"
        verbose_name_plural = "Отделы сотрудников"
