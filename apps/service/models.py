from django.db import models

from apps.client.models import Client, Contract

# Create your models here.
class Service(models.Model):
    name = models.CharField(
        "Категории услуг фирмы", max_length=150, blank=True, null=True)

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
    month = models.DateField(
        auto_now_add=True, verbose_name="Месяц"
    )

    # subcontract = models.ForeignKey(
    #     "SubcontractMonth", on_delete=models.SET_NULL, blank=True, null=True
    # )

    created_timestamp = models.DateField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    contract_sum = models.PositiveIntegerField("Сумма контракта", default="0")
    operations_add_all = models.PositiveIntegerField("Сумма прихода вся", default="0", blank=True, null=True)
    operations_add_diff_all = models.PositiveIntegerField(
        "Сумма прихода остаток", default="0", blank=True, null=True
    )
    operations_add_ip = models.PositiveIntegerField("Сумма прихода ИП", default=None, blank=True, null=True)
    operations_add_ооо = models.PositiveIntegerField("Сумма прихода ООО", default=None, blank=True, null=True)
    operations_add_nal = models.PositiveIntegerField("Сумма прихода нал", default=None, blank=True, null=True)

    operations_out_all = models.PositiveIntegerField("Сумма расхода вся", default="0", blank=True, null=True)
    operations_out_diff_all = models.PositiveIntegerField(
        "Сумма прихода остаток", default="0", blank=True, null=True
    )
    operations_out_ip = models.PositiveIntegerField("Сумма расхода ИП", default=None, blank=True, null=True)
    operations_out_ооо = models.PositiveIntegerField("Сумма расхода ООО", default=None, blank=True, null=True)
    operations_out_nal = models.PositiveIntegerField("Сумма расхода нал", default=None, blank=True, null=True)

    adv_all_sum = models.PositiveIntegerField(
        "Сумма ведения для ADV", default=None, blank=True, null=True)
    diff_sum = models.PositiveIntegerField(
        "сумма для распределения по скбподряду адв", default="0"
    )
    # diff_sum = models.PositiveIntegerField(
    #     "сумма для распределения по скбподряду адв", default="0"
    # )

    # chekin_sum_entrees = models.BooleanField(
    #     "чекин получения полной оплаты от клиента", default=False
    # )

    # chekin_sum_adv = models.BooleanField(
    #     "чекин оплаты всех субподрядов", default=False)

    # chekin_add_subcontr = models.BooleanField(
    #     "чекин есть ли распределение денег по субподрядам", default=False
    # )


class AdvPlatform(models.Model):
    name = models.CharField("Название площадки", max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Рекламная площадка"
        verbose_name_plural = "Рекламные площадки"
        
    
    def __str__(self):
        return self.name
