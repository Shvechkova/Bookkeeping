from django.db import models

from apps.employee.models import Employee

# Create your models here.
class Client(models.Model):
    name = models.CharField("имя клиента", max_length=200)
    manager = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        verbose_name="Менеджер",
        blank=True,
        null=True,
    )
     
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"