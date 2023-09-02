# Generated by Django 4.2.3 on 2023-09-01 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_alter_account_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='addresses',
            field=models.ManyToManyField(blank=True, to='accounts.accountdata', verbose_name='Адреса пользователя'),
        ),
        migrations.AlterField(
            model_name='account',
            name='purchases',
            field=models.ManyToManyField(blank=True, to='accounts.purchase', verbose_name='Покупки'),
        ),
    ]