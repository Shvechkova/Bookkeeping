from django.utils import timezone
from django.db import models

# Create your models here.
class LogsError(models.Model):
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    location = models.CharField(
        "Место ошибки",
        max_length=200,
        blank=True,
        null=True,
    )
    info = models.CharField(
        "Инфо о ошибке",
        max_length=100000,
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = "Лог ошибок"
        verbose_name_plural = "Логи ошибок"

    def __str__(self):
        return f"Тип ошибки: {self.type_error},{self.created_timestamp} "
    
class Logsinfo(models.Model):
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    location = models.CharField(
        "Место ошибки",
        max_length=200,
        blank=True,
        null=True,
    )
    info = models.CharField(
        "Инфо о ошибке",
        max_length=100000,
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = "Информационные сообщения"
        verbose_name_plural = "Информационные сообщения"

    def __str__(self):
        return f"Тип ошибки: {self.type_error},{self.created_timestamp} "