# Generated by Django 4.2.3 on 2023-07-30 04:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_accountnotifysettings_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountnotifysettings',
            options={'verbose_name': 'Настройки', 'verbose_name_plural': 'Настройки пользовательских уведомлений'},
        ),
    ]
