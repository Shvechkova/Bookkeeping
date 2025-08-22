from django.utils import timezone
from django.db import models

from apps.employee.models import Employee


# Create your models here.
class Bank(models.Model):
    name = models.CharField("Банк", max_length=200)

    # slugish = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        verbose_name = "Банк"
        verbose_name_plural = "Банки"

    def __str__(self):
        return self.name


CATEGORY_OPERACCOUNT = [
    ("1", "Oфис"),
    ("2", "Реклама"),
    ("3", "Прочее"),
    ("4", "Банковские расходы"),
]


class GroupeOperaccount(models.Model):
    name = models.CharField("Имя", max_length=200)
    category = models.CharField(
        max_length=20, choices=CATEGORY_OPERACCOUNT, default="1"
    )

    # slugish = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        verbose_name = "Группа расходов операкаунта"
        verbose_name_plural = "Группы расходов операкаунта"

    def __str__(self):
        return self.name

    def get_category_name(self):
        for choice in CATEGORY_OPERACCOUNT:
            if choice[0] == self.category:
                return choice[1]
        return ""


class GroupeSalary(models.Model):
    name = models.CharField("Имя", max_length=200)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name="Банк")
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Группа расходов зарплаты"
        verbose_name_plural = "Группы расходов зарплаты"

    def __str__(self):
        return self.name


class CategNalog(models.Model):
    name = models.CharField("Имя", max_length=200)
    bank_in = models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name="Банк")
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )
    in_page_nalog = models.BooleanField("Отображение на странице налогов", default=True)

    class Meta:
        verbose_name = "Категория налога"
        verbose_name_plural = "Категории налогов"

    def __str__(self):
        return self.name


class CategForPercentGroupBank(models.Model):
    name = models.CharField("Имя", max_length=200)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name="Банк")
    category_between = models.ForeignKey(
        "CategOperationsBetweenBank",
        on_delete=models.CASCADE,
        verbose_name="Категория операции между счетами",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Категория процентных полей "
        verbose_name_plural = "Категории  процентных полей"

    def __str__(self):
        return self.name


class CategPercentGroupBank(models.Model):
    created_timestamp = models.DateTimeField(
        default=timezone.now, verbose_name="Дата добавления"
    )
    data = models.DateField(verbose_name="Дата добавления вручную")
    category = models.ForeignKey(
        CategForPercentGroupBank, on_delete=models.CASCADE, verbose_name="Категория"
    )
    category_between = models.ForeignKey(
        "CategOperationsBetweenBank",
        on_delete=models.CASCADE,
        verbose_name="Категория операции между счетами",
        blank=True,
        null=True,
    )
    percent = models.FloatField("Сумма", default="0")
    is_auto_persent = models.BooleanField(
        "Авто процент с прошлого месяца", default=True
    )
    in_need_operations= models.BooleanField("Необходимость операции", default=True)

    class Meta:
        verbose_name = "Проценты для сумм по категориям"
        verbose_name_plural = "Проценты для сумм по категориям"

    def __str__(self):
        return f"{self.category} - {self.percent}%"

class PercentEmployee(models.Model):
    created_timestamp = models.DateTimeField(
        default=timezone.now, verbose_name="Дата добавления"
    )
    data = models.DateField(verbose_name="Дата добавления вручную")
    category = models.ForeignKey(
        CategForPercentGroupBank, on_delete=models.CASCADE, verbose_name="Категория"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Сотрудник",
        
    )
    percent = models.FloatField("Сумма", default="0")
    is_auto_persent = models.BooleanField(
        "Авто процент с прошлого месяца", default=True
    )
    in_need_operations= models.BooleanField("Необходимость операции", default=True)

    class Meta:
        verbose_name = "Проценты для сумм по сотрудникам"
        verbose_name_plural = "Проценты для сумм по сотрудникам"

    def __str__(self):
        return f"{self.employee} - {self.percent}%"

class CategOperationsBetweenBank(models.Model):
    name = models.CharField("Имя", max_length=200)
    bank_in = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        verbose_name="банк откуда назначения операции",
        related_name="between_bank_in",
        blank=True,
        null=True,
    )
    bank_to = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name="between_bank_to",
        verbose_name="банк конечный назначения операции",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Категория операций между банками"
        verbose_name_plural = "Категория операций между банками"

    def __str__(self):
        return self.name
