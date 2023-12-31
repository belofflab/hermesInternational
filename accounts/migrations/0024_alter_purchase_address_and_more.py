# Generated by Django 4.2.3 on 2023-09-07 05:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_alter_purchase_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.accountdata'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='delivery_method',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Метод доставки'),
        ),
    ]
