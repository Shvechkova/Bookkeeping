from django.db import models

from apps.bank.models import Bank
from apps.client.models import Client, Contract
from apps.employee.models import CategoryEmployee, Employee

# Create your models here.
class Service(models.Model):
    name = models.CharField(
        "Категории услуг фирмы", max_length=150, blank=True, null=True)
    name_long_ru = models.CharField(
        "Категории на русском полное название ", max_length=266, blank=True, null=True)
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        
    
    def __str__(self):
        return self.name


class ServicesClientMonthlyInvoice(models.Model):
    client = models.ForeignKey(
        Client,  on_delete=models.PROTECT,verbose_name="Клиент", blank=True, null=True)
    service = models.ForeignKey(
        Service,  on_delete=models.PROTECT,verbose_name="Услуга", blank=True, null=True
    )
    contract = models.ForeignKey(
        Contract,  on_delete=models.PROTECT,verbose_name="Контракт", blank=True, null=True
    )
    month = models.DateField( verbose_name="Месяц", blank=True, 
    )

    # subcontract = models.ForeignKey(
    #     "SubcontractMonth", on_delete=models.SET_NULL, blank=True, null=True
    # )

    created_timestamp = models.DateField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    contract_sum = models.FloatField("Сумма контракта", default="0")
    operations_add_all = models.FloatField("Сумма прихода вся", default="0", blank=True, null=True)
    operations_add_diff_all = models.FloatField(
        "Сумма прихода остаток", default="0", blank=True, null=True
    )
    # # operations_add_ip = models.FloatField("Сумма прихода ИП", default=None, blank=True, null=True)
    # # operations_add_ооо = models.FloatField("Сумма прихода ООО", default=None, blank=True, null=True)
    # # operations_add_nal = models.FloatField("Сумма прихода нал", default=None, blank=True, null=True)

    # operations_out_all = models.FloatField("Сумма расхода вся", default="0", blank=True, null=True)
    # operations_out_diff_all = models.FloatField(
    #     "Сумма прихода остаток", default="0", blank=True, null=True
    # )
    # operations_out_ip = models.FloatField("Сумма расхода ИП", default=None, blank=True, null=True)
    # operations_out_ооо = models.FloatField("Сумма расхода ООО", default=None, blank=True, null=True)
    # operations_out_nal = models.FloatField("Сумма расхода нал", default=None, blank=True, null=True)

    adv_all_sum = models.FloatField(
        "Сумма ведения для ADV", default=None, blank=True, null=True)
    diff_sum = models.FloatField(
        "сумма для распределения по скбподряду адв", default="0"
    )


    # chekin_sum_entrees = models.BooleanField(
    #     "чекин получения полной оплаты от клиента", default=False
    # )

    # chekin_sum_adv = models.BooleanField(
    #     "чекин оплаты всех субподрядов", default=False)

    # chekin_add_subcontr = models.BooleanField(
    #     "чекин есть ли распределение денег по субподрядам", default=False
    # )


class SubcontractMonth(models.Model):
    employee = models.ForeignKey(
        Employee,
        verbose_name="Сотрудник",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    category_employee = models.ForeignKey(
        CategoryEmployee,
        verbose_name="Отдел",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    platform = models.ForeignKey(
        "AdvPlatform",
        verbose_name="Рекламная площадка",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # other = models.ForeignKey(
    #     "SubcontractOther",
    #     verbose_name="Тип субподряда",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )

    created_timestamp = models.DateField(
        auto_now_add=True, verbose_name="Дата добавления"
    )
    # Запланированные траты
    amount = models.FloatField("сумма субподряд", default="0")
    month_bill = models.ForeignKey(
        ServicesClientMonthlyInvoice, on_delete=models.CASCADE, blank=True, null=True
    )
    
class SubcontractOtherCategory(models.Model):
    name = models.CharField("Название другого субподряда", max_length=200, blank=True, null=True)
    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        verbose_name="банк",
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = "Субподряд другое"
        verbose_name_plural = "Субподряд другое"
       
    
    def __str__(self):
        return self.name


class AdvPlatform(models.Model):
    name = models.CharField("Название площадки", max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Рекламная площадка"
        verbose_name_plural = "Рекламные площадки"
        
    
    def __str__(self):
        return self.name
