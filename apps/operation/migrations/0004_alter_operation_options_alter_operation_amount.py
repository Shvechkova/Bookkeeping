# Generated by Django 5.2 on 2025-05-06 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0003_operation_suborder'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operation',
            options={'verbose_name': 'Операция', 'verbose_name_plural': 'Операции'},
        ),
        migrations.AlterField(
            model_name='operation',
            name='amount',
            field=models.FloatField(default='0', verbose_name='Сумма'),
        ),
    ]
