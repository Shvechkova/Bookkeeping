# Generated by Django 5.2 on 2025-06-26 08:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0014_alter_categforpercentgroupbank_options_and_more'),
        ('operation', '0009_operation_suborder_other'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='between_bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bank.categoperationsbetweenbank', verbose_name='Между банками'),
        ),
    ]
