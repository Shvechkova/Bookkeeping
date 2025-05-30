# Generated by Django 5.2 on 2025-04-29 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='employee',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Действующий'),
        ),
    ]
