# Generated by Django 4.2.3 on 2023-07-26 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_account_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=255, verbose_name='Город')),
                ('street', models.CharField(max_length=255, verbose_name='Улица')),
                ('state', models.CharField(max_length=255, verbose_name='Штат')),
                ('postal_code', models.CharField(max_length=255, verbose_name='Почтовый индекс')),
                ('country', models.CharField(max_length=255, verbose_name='Страна')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='country',
            field=models.CharField(max_length=255, null=True, verbose_name='Страна'),
        ),
        migrations.AddField(
            model_name='account',
            name='addresses',
            field=models.ManyToManyField(to='accounts.accountdata', verbose_name='Адреса пользователя'),
        ),
    ]
