# Generated by Django 4.2.3 on 2023-07-31 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_purchasedeliveryoption_name_en_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyoutCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_visible', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории скуп-листа',
            },
        ),
        migrations.CreateModel(
            name='Buyout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, verbose_name='Товар|Товары')),
                ('percent', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Процент')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.buyoutcategory')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Скуп-лист',
            },
        ),
    ]
