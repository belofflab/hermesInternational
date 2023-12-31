# Generated by Django 4.2.3 on 2023-09-07 03:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_alter_account_addresses_alter_account_purchases'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchasePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='purchase_photos/', verbose_name='Фотография')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='accounts.purchase', verbose_name='Покупка')),
            ],
            options={
                'verbose_name': 'Фотография покупки',
                'verbose_name_plural': 'Фотографии покупок',
            },
        ),
    ]
