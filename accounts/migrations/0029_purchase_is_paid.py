# Generated by Django 4.2.3 on 2023-09-09 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_purchase_is_ready_pay'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Оплачена'),
        ),
    ]