# Generated by Django 4.2.3 on 2023-09-09 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_service_invoice_service'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'verbose_name': 'Услугу', 'verbose_name_plural': 'Услуги'},
        ),
    ]
