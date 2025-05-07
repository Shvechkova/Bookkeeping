from django.db import models


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
        ('1', "Oфис"),
        ('2', "Реклама"),
        ('3', "Прочее"),
        ('4', "Банковские расходы"),
    ]

class GroupeOperaccount(models.Model):
    name = models.CharField("Имя", max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_OPERACCOUNT, default='1')
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
