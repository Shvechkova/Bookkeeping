from django.db import models

from apps.employee.models import Employee


# Create your models here.
class Client(models.Model):
    name = models.CharField("имя клиента", max_length=200)
    manager = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        verbose_name="Менеджер клиента",
        blank=True,
        null=True,
    )
     
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        

class Contract(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, verbose_name="Клиент")

    contract_number = models.CharField("название номер контракта", max_length=200)
    contract_sum = models.PositiveIntegerField("сумма контракта", default="0")
    
    date_start = models.DateField("Дата начала действия", blank=True, null=True)
    date_end = models.DateField("Дата окончания", blank=True, null=True)
    service = models.ForeignKey(
        "service.Service",
        on_delete=models.PROTECT,
        verbose_name="Услуга контракта",
        blank=True,
        null=True,
    )
    created_timestamp = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )
    manager = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        verbose_name="Ответственный контракта",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Контракт"
        verbose_name_plural = "Контракты"
        
        
# class ServiceClient(models.Model):
#     service = models.ForeignKey(
#         Service,
#         on_delete=models.PROTECT,
#         verbose_name="Услуга",
#         blank=True,
#         null=True,
#     )
#     client = models.ForeignKey(
#         Client,
#         on_delete=models.PROTECT,
#         verbose_name="Клиент",
#         blank=True,
#         null=True,
#     )

#     created_timestamp = models.DateTimeField(
#         auto_now_add=True, verbose_name="Дата добавления"
#     )
#     # adv_all_sum = models.PositiveIntegerField("",default="0")

#     # def __str__(self):
#     #     return str(self.service )