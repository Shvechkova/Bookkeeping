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
