from django.utils import timezone
from django.db import models
from datetime import datetime

from apps.bank.models import Bank
from apps.service.models import ServicesClientMonthlyInvoice, SubcontractMonth


# Create your models here.
class Operation(models.Model):
    created_timestamp = models.DateTimeField(
        default=timezone.now, verbose_name="Дата добавления"
    )
    data = models.DateField(verbose_name="Дата добавления вручную")
    bank_in = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        verbose_name="банк откуда назначения операции",
        related_name="bank_in",
        blank=True,
        null=True,
    )
    bank_to = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name="bank_to",
        verbose_name="банк конечный назначения операции",
        blank=True,
        null=True,
    )

    amount = models.FloatField("Сумма",default="0")
    comment = models.TextField("Комментарий", blank=True, null=True)

    monthly_bill = models.ForeignKey(
        ServicesClientMonthlyInvoice,
        on_delete=models.PROTECT,
        verbose_name="Счет за цслугу",
        blank=True,
        null=True,
    )
    suborder = models.ForeignKey(
        SubcontractMonth,
        on_delete=models.PROTECT,
        verbose_name="Субподряд для оплат",
        blank=True,
        null=True,
    )
    # name = models.ForeignKey(
    #     NameOperation,
    #     on_delete=models.PROTECT,
    #     verbose_name="Название операции",
    #     blank=True,
    #     null=True,
    # )
    # category = models.ForeignKey(
    #     CategoryOperation,
    #     on_delete=models.PROTECT,
    #     verbose_name="Категория операции",
    #     blank=True,
    #     null=True,
    # )
    # meta_category = models.ForeignKey(
    #     MetaCategoryOperation,
    #     on_delete=models.PROTECT,
    #     verbose_name="Главная категория операции",
    #     blank=True,
    #     null=True,
    # )

    # people = models.ForeignKey(
    #     Employee,
    #     on_delete=models.PROTECT,
    #     verbose_name="зарплата",
    #     blank=True,
    #     null=True,
    # )

    TYPE_OPERATION = [
        ("entry", "entry"),
        ("out", "out"),
    ]

    type_operation = models.CharField(
        max_length=5, choices=TYPE_OPERATION, default="out"
    )

    META_CATEGORY = [
        ("oper_account", "oper_account"),
        ("banking", "banking"),
        ("nalog", "nalog"),
        ("salary", "salary"),
        ("suborders", "suborders"),
        ("entrering", "entrering"),
        ("none", "none"),
    ]
    meta_categ = models.CharField(max_length=20, choices=META_CATEGORY, default="none")
    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"
        
    def save(self, *args, **kwargs):
        if self.comment == "":
            self.comment = None
        super().save(*args, **kwargs)