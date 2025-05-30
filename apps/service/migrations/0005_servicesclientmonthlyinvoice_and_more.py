# Generated by Django 5.2 on 2025-04-30 15:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_alter_client_manager'),
        ('service', '0004_servicesmonthlyinvoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicesClientMonthlyInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(auto_now_add=True, verbose_name='Месяц')),
                ('created_timestamp', models.DateField(auto_now_add=True, verbose_name='Дата добавления')),
                ('contract_sum', models.PositiveIntegerField(default='0', verbose_name='Сумма контракта')),
                ('operations_add_all', models.PositiveIntegerField(default='0', verbose_name='Сумма прихода вся')),
                ('operations_add_ip', models.PositiveIntegerField(default=None, verbose_name='Сумма прихода ИП')),
                ('operations_add_ооо', models.PositiveIntegerField(default=None, verbose_name='Сумма прихода ООО')),
                ('operations_add_nal', models.PositiveIntegerField(default=None, verbose_name='Сумма прихода нал')),
                ('operations_out_all', models.PositiveIntegerField(default='0', verbose_name='Сумма расхода вся')),
                ('operations_out_ip', models.PositiveIntegerField(default=None, verbose_name='Сумма расхода ИП')),
                ('operations_out_ооо', models.PositiveIntegerField(default=None, verbose_name='Сумма расхода ООО')),
                ('operations_out_nal', models.PositiveIntegerField(default=None, verbose_name='Сумма расхода нал')),
                ('adv_all_sum', models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Сумма ведения для ADV')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='client.client', verbose_name='Клиент')),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='client.contract', verbose_name='Контракт')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='service.service', verbose_name='Услуга')),
            ],
        ),
        migrations.DeleteModel(
            name='ServicesMonthlyInvoice',
        ),
    ]
