from django.db import models

# Create your models here.
class Service(models.Model):
    name = models.CharField(
        "Категории услуг фирмы", max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"
        
    
    def __str__(self):
        return self.name